from gaspanel import GasPanel, GasPanelScannable

class GasPanelDataHolder():
    def __init__():
        self.pressures = []
        self.deltaSums = []

    def addPointWithDelta( self, pressure, delta ):
        self.pressures.append( pressure )
        if len( self.deltaSums ) == 0:
            self.deltaSums.append( delta )
        else:
            self.deltaSums.append( self.deltaSums[-1] + delta )

    def addPoint( self, pressure, deltaSum ):
        self.pressures.append( pressure )
        self.deltaSums.append( deltaSum )

    def getLastPoint():
        return ( self, self.pressures[-1], self.deltaSum[-1] )

class GasPanelScannableMarkII( ScannableBase ):
    def __init__( self, name, pvRoot, threshold = 5 ):
        self.setName( name )
        self.setInputNames( ["index"] )
        self.dataManager = GasPanelDataHolder()
        self.inScan = False

    def getPosition( self ):
        pressure = float( self.pvs['PRESSURE_RBV'].caget() )
        if self.inScan:
            self.final = pressure
            difference = self.actualPressure - self.final
            self.dataManager.addPoint( pressure, difference )
        else:
            return pressure

    def asynchronousMoveTo( self, index ):
        self.index = index
        self.requestedPressure = self.final + self.increment
        self.pvs['PRESSDEM'].caput( self.requestedPressure )
        self.pvs['MODE'].caput( int(self.requestStates['Fill']) )
        self.waitWhileBusy()
        self.actualPressure = float(self.pvs['PRESSURE_RBV'].caget())
        self.equilibrate()

    def isBusy( self ):
        return self.getMode() != 'Idle' or int( self.pvs['VALVE-07:STA'].caget() ) != 3

    def waitWhileBusy( self ):
        busy = True
        while busy:
            sleep(1) #the gas panel is a little sleepy
            busy = self.isBusy()

    def atScanStart( self ):
        self.inScan = True

    def atScanEnd( self ):
        self.stop()

    def atCommandFailure( self ):
        self.stop()

    def stop( self ):
        self.inScan = False
        self.pvs['MODE'].caput( int(self.requestStates['Abort']) )
