from gda.device.scannable import ScannableBase

class LakeshoreDoubleReadout( ScannableBase ):
    def __init__( self, name, lakeshore ):
        self.lakeshore = lakeshore
        self.controller = lakeshore.getController()
        self.setName( name )
        self.setInputNames( ["Lakeshore"] )
        #self.setExtraNames( ["Lakeshore_2"] )
        #self.setOutputFormat(["%5.5g", "%5.5g"])
        self.setOutputFormat(["%5.5g"])

    def getPosition( self ):
        #return ( self.lakeshore.getCurrentTemperature(), self.lakeshore.controller.getChannel1Temp() )
        return self.lakeshore.getCurrentTemperature()

    def rawAsynchronousMoveTo( self, temp ):
        self.lakeshore.rawAsynchronousMoveTo( temp )

    def setTargetTemperature( self, temp ):
        self.lakeshore.setTargetTemperature( temp )

    def waitForTemp( self ):
        self.lakeshore.waitForTemp()

    def isBusy( self ):
        return self.lakeshore.isBusy()

    def stop( self ):
        pass
        #self.lakeshore.stop()

    def atScanEnd(self):
        self.stop()

    def atCommandFailure(self):
        self.stop()

    def getChannelTemp( self, channel ):
        methods = [self.controller.getTemp,
            self.controller.getChannel1Temp,
            self.controller.getChannel2Temp,
            self.controller.getChannel3Temp]
        return methods[channel]()

class LakeshoreDoubleReadoutDummy( ScannableBase ):
    def __init__( self, name ):
        self.setName( name )
        self.setInputNames( ["Lakeshore_1"] )
        self.setExtraNames( ["Lakeshore_2"] )
        self.temps = [100.0, 101.0, 102.0, 103.0]
        self.setOutputFormat(["%5.5g", "%5.5g"])

    def getPosition( self ):
        return (self.temps[0], self.temps[1])

    def rawAsynchronousMoveTo( self, temp ):
        self.temps = [temp] * 4

    def setTargetTemperature( self, temp ):
        self.temps = [temp] * 4

    def waitForTemp( self ):
        pass

    def isBusy( self ):
        return False

    def stop( self ):
        pass

    def atScanEnd( self ):
        self.stop

    def atCommandFailure( self ):
        self.stop

    def getChannelTemp( self, channel ):
        return self.temps[channel]
