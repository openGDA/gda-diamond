from gdascripts.scannable.epics.PvManager import PvManager
from gda.device.scannable import ScannableBase
from gda.scan import ScanPositionProvider
from time import sleep
import scisoftpy as dnp

class GasPanelIncrementValue():
    def __init__( self, initVal ):
        self.value = initVal

GASPANEL_INCREMENT = GasPanelIncrementValue(10)

class GasPanel():
    def __init__(self, name, pvRoot):
        self.name = name
        valves = ['VALVE-%02d:CON' % x for x in range(1,9)]
        valvesReadBack = ['VALVE-%02d:STA' % x for x in range(1,9)]
        self.valvesControl = dict( zip(range(1,9), valves) )
        self.valvesRead = dict( zip(range(1,9), valvesReadBack) )
        self.pvs = PvManager(['MODE', 'MODE_ACTIVE'] + valves + valvesReadBack, pvRoot)
        self.pvs.configure()
        self.requestStates = {'Fill':0, 'Absorption':1, 'Abort':2, 'Idle':3}
        self.activeStates = {1:'Fill', 2:'Absorption', 4:'Idle'}
        self.valveStates = {0:'Fault', 1:'Open', 2:'Opening', 3:'Closed', 4:'Closing'} #VALVE-XX:STA, not :CON

    def openValve(self, valve):
        self.pvs[ self.valvesControl[valve] ].caput(0)

    def closeValve(self, valve):
        self.pvs[ self.valvesControl[valve] ].caput(1)

    def posValve(self, valve):
        return self.valveStates[ int(self.pvs[ self.valvesRead[valve] ].caget()) ]

    def setThreshold(self, delta):
        self.pvs['THRESHOLD'].caput( float(delta) )

    def getThreshold(self):
        return float( self.pvs['THRESHOLD_RBV'].caget() )

    def fill(self, pressure):
        #maybe raise exception if called before abort called
        if self.isBusy(): raise Exception("Gas panel is busy; call abort first")
        self.pvs['PRESSDEM'].caput( float(pressure) )
        self.pvs['MODE'].caput( int(self.requestStates['Fill']) )

    def readChamberPressure(self):
        return float(self.pvs['PRESSURE_RBV'].caget())

    def equilibrate(self):
        #maybe raise exception if called before abort is
        if self.isBusy(): raise Exception("Gas panel is busy; call abort first")
        self.pvs['MODE'].caput( int(self.requestStates['Absorption']) )

    def getMode(self):
        mode = int(self.pvs['MODE_ACTIVE'].caget())
        if mode > 4: mode = 4
        return self.activeStates[mode]

    def abort(self):
        self.pvs['MODE'].caput( int(self.requestStates['Abort']) )

    def isBusy(self):
        #mode is "Idle" even when lowering pressure, so we must monitor the valve to the vacuum pump too
        return self.getMode() != 'Idle' or int(self.pvs['VALVE-07:STA'].caget()) != 3

    def waitWhileBusy(self):
        while True:
            sleep(0.1)
            if not self.isBusy(): break

class DummyGasPanel():
    def __init__(self, name):
        self.name = name
        self.valves = dict.fromkeys(range(1,9), 'Closed')
        self.threshold = 5
        self.chamberPressure = 50
        self.samplePressure = 10
        self.chamberVolume = 8
        self.sampleVolume = 2

    def openValve(self, valve):
        self.valves[valve] = 'Open'

    def closeValve(self, valve):
        self.valves[valve] = 'Closed'

    def posValve(self, valve):
        return self.valves[valve]

    def setThreshold(self, delta):
        self.threshold = delta

    def getThreshold(self):
        return threshold

    def fill(self, pressure):
        self.chamberPressure = pressure

    def readChamberPressure(self):
        return float( self.chamberPressure )

    def equilibrate(self):
        pressure = ( (self.chamberPressure * self.chamberVolume +
         self.samplePressure * self.sampleVolume) /
         (self.chamberVolume + self.sampleVolume) )

        self.samplePressure = pressure
        self.chamberPressure = pressure

    def getMode(self):
        return 'Idle'

    def abort(self):
        pass

    def isBusy(self):
        return False

    def waitWhileBusy(self):
        while True:
            sleep(0.1)
            if not self.isBusy(): break

def gasScan(panel, initialPressure, maxCount = -1):
    deltaSum = 0;
    deltaSumDataSet = []
    pressureDataSet = []
    i = 0
    while (i < maxCount) or (maxCount < 0):
        i+=1
        panel.abort()
        panel.fill(initialPressure)
        print "filling to %f" % initialPressure
        sleep(1) #gas panel is a little sleepy
        panel.waitWhileBusy()
        initialPressure = panel.readChamberPressure()
        panel.equilibrate()
        print "equilibrating"
        sleep(1)
        panel.waitWhileBusy()
        finalPressure = panel.readChamberPressure()
        pressureDataSet.append( finalPressure )
        delta = initialPressure - finalPressure
        deltaSum += delta
        deltaSumDataSet.append( deltaSum )
        print "Pi: %f\nPf: %f\ndelta: %f\ndeltaSum: %f\n" % (initialPressure, finalPressure, delta, deltaSum)
        initialPressure = finalPressure + GASPANEL_INCREMENT.value
        dnp.plot.line(
            dnp.array( pressureDataSet ),
            [(dnp.array( deltaSumDataSet ), "deltaSum")],
            title="deltaSum v Pressure",
            name="GasPanel" )

    panel.abort()
    #dnp.plot.line( dnp.array( pressureDataSet ), dnp.array( deltaSumDataSet ), "deltaSum v Pressure" )

class GasPanelScannable( ScannableBase ):
    def __init__( self, name, pvRoot, threshold = 5 ):
        self.verbose = False
        self.setName( name )
        self.setInputNames( ["index"] )
        self.setExtraNames( ["p_requested", "p_actual", "p_final", "difference_sum"] )
        self.pvs = PvManager( ['MODE', 'MODE_ACTIVE', 'VALVE-07:STA'], pvRoot )
        self.pvs.configure()
        self.requestStates = { 'Fill':0, 'Absorption':1, 'Abort':2, 'Idle':3 }
        self.activeStates = { 1:'Fill', 2:'Absorption', 4:'Idle' }
        self.threshold = threshold
        self.final = 0
        self.initialPressure = 50
        self.increment = 10
        self.sumDifferences = 0

    def getPosition( self ):
        #return float( self.pvs['PRESSURE_RBV'].caget() )
        if self.verbose: print "getPosition called"
        self.final = float( self.pvs['PRESSURE_RBV'].caget() )
        difference = self.actualPressure - self.final
        self.sumDifferences += difference
        return (self.index, self.requestedPressure, self.actualPressure, self.final, self.sumDifferences)

    def asynchronousMoveTo( self, index ):
        self.index = index
        self.requestedPressure = self.final + self.increment
        self.pvs['PRESSDEM'].caput( self.requestedPressure )
        self.pvs['MODE'].caput( int(self.requestStates['Fill']) )
        if self.verbose: print "asyncMoveTo: %d, %f" % (index, self.requestedPressure)
        self.waitWhileBusy()
        self.actualPressure = float(self.pvs['PRESSURE_RBV'].caget())
        self.equilibrate()

    def isBusy( self ):
        return self.getMode() != 'Idle' or int( self.pvs['VALVE-07:STA'].caget() ) != 3

    def waitWhileBusy( self ):
        busy = True
        while busy:
            sleep(1)
            busy = self.isBusy()

    def getMode( self ):
        mode = int(self.pvs['MODE_ACTIVE'].caget())
        if mode > 4: mode = 4
        return self.activeStates[mode]

    def equilibrate( self ):
        if self.verbose: print "equilibrating"
        self.pvs['MODE'].caput( int(self.requestStates['Absorption']) )
        self.waitWhileBusy()

    def atScanStart(self):
        self.final = self.initialPressure - self.increment
        self.sumDifferences = 0

    def atScanEnd( self ):
        self.stop()

    def stop( self ):
        self.pvs['MODE'].caput( int(self.requestStates['Abort'] ) )

    def atCommandFailure(self):
        self.stop()



