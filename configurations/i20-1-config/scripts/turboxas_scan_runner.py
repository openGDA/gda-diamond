from gda.scan import TurboXasParameters, TurboXasMotorParameters, TurboXasScan

class TurboXasScanRunner:
    def __init__(self):
        self.scanFileName=""
    
    def __call__(self, params):
        print "FrelonScan::__call__ ",params, params.__class__
        if len(params) > 0:
            self.scanFileName = params[0]
        
        print "Params : filename = ",self.scanFileName

        #Load params from xml file
        turboXasParams = TurboXasParameters.loadFromFile(str(self.scanFileName))
        print "TurboXAS parameters from file : ",self.scanFileName
        print turboXasParams.toXML();
        
        # Get motor params
        turboXasMotorParams = turboXasParams.getMotorParameters();
        print "TurboXAS motor parameters"
        print turboXasMotorParams.toXML()
        
        txasScan = TurboXasScan( turbo_xas_slit, turboXasMotorParams, [scaler_for_zebra] )
       
        # Run the scan
        txasScan.runScan()
        
turboxas_scan = TurboXasScanRunner()

vararg_alias("turboxas_scan")
