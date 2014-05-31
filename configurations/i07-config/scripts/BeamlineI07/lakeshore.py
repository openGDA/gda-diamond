from gda.device.scannable import ScannableBase

class LakeshoreDoubleReadout( ScannableBase ):
    def __init__( self, name, lakeshore ):
        self.lakeshore = lakeshore
        self.controller = lakeshore.getController()
        self.setName( name )
        self.setInputNames( ["Lakeshore_1"] )
        self.setExtraNames( ["Lakeshore_2"] )

    def getPosition( self ):
        return ( self.lakeshore.getCurrentTemperature(), self.lakeshore.controller.getChannel1Temp() )

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


