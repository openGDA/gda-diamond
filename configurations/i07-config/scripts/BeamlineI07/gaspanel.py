from gdascripts.scannable.epics.PvManager import PvManager
from gdascripts.scannable.preloadedArray import PreloadedArray
from gda.device.scannable import ScannableBase
from gda.scan import ScanPositionProvider, ConcurrentScan
from time import sleep
import scisoftpy as dnp

class GasPanelValue():
    def __init__( self, initVal ):
        self.value = initVal

GASPANEL_INCREMENT = GasPanelValue(20)
GASPANEL_STOP = GasPanelValue(True)

class GasPanel():
    def __init__( self, name, pvRoot ):
        self.name = name
        valves = ['VALVE-%02d:CON' % x for x in range(1,9)]
        valvesReadBack = ['VALVE-%02d:STA' % x for x in range(1,9)]
        self.valvesControl = dict( zip(range(1,9), valves) )
        self.valvesRead = dict( zip(range(1,9), valvesReadBack) )
        self.pvs = PvManager(['MODE', 'MODE_ACTIVE'] + valves + valvesReadBack, pvRoot)
        self.pvs.configure()
        self.requestStates = {'Fill':0, 'Absorption':1, 'Abort':2, 'Idle':3}
        self.activeStates = {0:'Unkown', 1:'Fill', 2:'Absorption', 3:'Unknown', 4:'Idle', 5:'Unknown'}
        self.valveStates = {0:'Fault', 1:'Open', 2:'Opening', 3:'Closed', 4:'Closing'} #VALVE-XX:STA, not :CON

    def openValve( self, valve ):
        self.pvs[ self.valvesControl[valve] ].caput(0)

    def closeValve( self, valve ):
        self.pvs[ self.valvesControl[valve] ].caput(1)

    def posValve( self, valve ):
        return self.valveStates[ int(self.pvs[ self.valvesRead[valve] ].caget()) ]

    def setThreshold( self, delta ):
        self.pvs['THRESHOLD'].caput( float(delta) )

    def getThreshold( self ):
        return float( self.pvs['THRESHOLD_RBV'].caget() )

    def fill( self, pressure ):
        #maybe raise exception if called before abort called
        if self.isBusy(): raise Exception("Gas panel is busy; call abort first")
        self.pvs['PRESSDEM'].caput( float(pressure) )
        self.pvs['MODE'].caput( int(self.requestStates['Fill']) )

    def readChamberPressure( self ):
        return float(self.pvs['PRESSURE_RBV'].caget())

    def equilibrate( self ):
        #maybe raise exception if called before abort is
        if self.isBusy(): raise Exception("Gas panel is busy; call abort first")
        self.pvs['MODE'].caput( int(self.requestStates['Absorption']) )

    def getMode( self ):
        mode  = int(self.pvs['MODE_ACTIVE'].caget())
        if mode > 4: mode = 4
        return self.activeStates[mode]

    def abort( self ):
        self.pvs['MODE'].caput( int(self.requestStates['Abort']) )

    def isBusy(self):
        #mode is "Idle" even when lowering pressure, so we must monitor the valve to the vacuum pump too
        return self.getMode() != 'Idle' or int(self.pvs['VALVE-07:STA'].caget()) != 3

    def waitWhileBusy( self ):
        while True:
            sleep(1)
            if not self.isBusy():
                #gas panel sometimes reports Idle before it's really finished filling
                sleep(1)
                if not self.isBusy(): break

class DummyGasPanel():
    def __init__( self, name ):
        self.name = name
        self.valves = dict.fromkeys(range(1,9), 'Closed')
        self.threshold = 5
        self.chamberPressure = 50
        self.samplePressure = 10
        self.chamberVolume = 8
        self.sampleVolume = 2

    def openValve( self, valve ):
        self.valves[valve] = 'Open'

    def closeValve( self, valve ):
        self.valves[valve] = 'Closed'

    def posValve( self, valve ):
        return self.valves[valve]

    def setThreshold( self, delta ):
        self.threshold = delta

    def getThreshold( self ):
        return threshold

    def fill( self, pressure ):
        self.chamberPressure = pressure

    def readChamberPressure(self):
        return float( self.chamberPressure )

    def equilibrate( self ):
        pressure = ( (self.chamberPressure * self.chamberVolume +
         self.samplePressure * self.sampleVolume) /
         (self.chamberVolume + self.sampleVolume) )

        self.samplePressure = pressure
        self.chamberPressure = pressure

    def getMode( self ):
        return 'Idle'

    def abort( self ):
        pass

    def isBusy( self ):
        return False

    def waitWhileBusy( self ):
        while True:
            sleep(0.1)
            if not self.isBusy(): break

def gasScanStop():
    GASPANEL_STOP.value = True

def gasScan( panel, initialPressure, maxCount, *args ):
    GASPANEL_STOP.value = False
    deltaSum = 0;
    deltaSumDataSet = []
    pressureDataSet = []
    additionalScannables = list(args)
    otherScannables = dict( (scannable.getName(), []) for scannable in additionalScannables )
    i = 0
    while ((i < maxCount) or (maxCount < 0)) and not GASPANEL_STOP.value:
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

        for scannable in additionalScannables:
            otherScannables[ scannable.getName() ].append( scannable.getPosition() )

        print "Pi: %f\nPf: %f\ndelta: %f\ndeltaSum: %f\n" % (initialPressure, finalPressure, delta, deltaSum)
        dnp.plot.line(
            dnp.array( pressureDataSet ),
            [(dnp.array( deltaSumDataSet ), "deltaSum")],
            title="deltaSum v Pressure",
            name="GasPanel" )

        initialPressure = finalPressure + GASPANEL_INCREMENT.value

    panel.abort()
    formatStrings = ["%5.5g", "%5.5g"]
    for scannable in additionalScannables:
        formatStrings += [x for x in scannable.getOutputFormat()]

    columns = { "Pressure":pressureDataSet, "deltaSum":deltaSumDataSet }
    columnNames = ["Pressure", "deltaSum"]

    for scannable in additionalScannables:
        scannableNames = scannable.getInputNames() + scannable.getExtraNames()
        if len(scannableNames) == 1:
            columns[scannable.getName()] = otherScannables[ scannable.getName() ]
            columnNames.append( scannable.getName() )
        elif len(scannableNames) > 1:
            j = 0
            for column in scannableNames:
                columns[column] = [ x[j] for x in otherScannables[scannable.getName()] ]
                columnNames.append( column )
                j += 1

    dataScannable = PreloadedArray( "dataScannable", columnNames, formatStrings, True )
    for column in columns.keys():
        dataScannable.setColumn( column, columns[column] )

    print dataScannable.getOutputFormat()
    print dataScannable.getPosition()
    print dataScannable
    adhocScan = ConcurrentScan( [dataScannable, 0, dataScannable.getLength() - 1, 1] )
    adhocScan.runScan()

class GasPanelScannable( ScannableBase ):
    def __init__( self, name, panel, initialPressure = 10, increment = 10 ):
        self.name = name
        self.index = 0
        self.deltaSum = 0
        self.panel = panel
        self.initialPressure = initialPressure
        self.increment = increment
        self.inputNames = ["Pressure"]
        self.extraNames = ["deltaSum"]
        self.outputFormat = [ "%5.5g", "%5.5g" ]
        self.inScan = False

    def posValve( self, valve, value=None ):
        if value == None:
            return self.panel.posValve( valve )
#        if not ( isinstance(value, int) or isinstance(value, basestring) ):
#            raise TypeError( "Invalid type: value must be 1, 0 or 'close', 'open'" )
        elif value == 1 or ( isinstance(value, basestring) and
                 (value.lower() == "close" or value.lower() == "closed") ):
            self.panel.closeValve( valve )
        elif value == 0 or ( isinstance(value, basestring) and value.lower() == "open" ):
            self.panel.openValve( valve )
        else:
            raise TypeError( "Invalid type: value must be 1, 0 or 'close', 'open'" )
        sleep(1)
        return self.panel.posValve( valve )

    def readChamberPressure( self ):
        return self.panel.readChamberPressure()

    def getMode( self ):
        return self.panel.getMode()

    def getThreshold( self ):
        return self.panel.getThreshold()

    def setThreshold( self, value ):
        self.panel.setThreshold( value )

    def atScanStart( self ):
        self.nextPressure = self.initialPressure
        self.deltaSum = 0
        self.pressureDataSet = []
        self.deltaSumDataSet = []
        self.inScan = True

    def atPointStart( self ):
        self.panel.fill( self.nextPressure )
        sleep(1)
        self.panel.waitWhileBusy()
        self.panel.equilibrate()
        sleep(1)
        self.inScan = True

    def atPointEnd( self ):
        self.inScan = False
        self.deltaSumDataSet.append( self.deltaSum )
        self.pressureDataSet.append( self.pressureToAdd )

        dnp.plot.line(
            dnp.array( self.pressureDataSet ),
            [(dnp.array( self.deltaSumDataSet ), "deltaSum")],
            title="deltaSum v Pressure",
            name="GasPanel" )

        self.nextPressure = self.pressure + self.increment

    def getPosition( self ):
        self.pressure = self.panel.readChamberPressure()
        if not self.inScan:
            return ( self.pressure, 0 )
        #don't add to self.pressureDataSet here, in case someone accidently pos's mid scan
        self.pressureToAdd = self.pressure
        delta = self.nextPressure - self.pressure
        self.deltaSum += delta
        returnValues = (self.pressure, self.deltaSum)
        return returnValues

    def waitWhileBusy( self ):
        inScanValue = self.inScan
        self.inScan = False
        self.panel.waitWhileBusy()
        self.inScan = inScanValue

    def isBusy( self ):
        self.panel.isBusy()

    def asynchronousMoveTo( self, position ):
        self.panel.fill( position )
        sleep(1)

    def atScanEnd( self ):
        self.stop()

    def atCommandFailure( self ):
        self.stop()

    def stop( self ):
        self.inScan = False
        self.panel.abort()

