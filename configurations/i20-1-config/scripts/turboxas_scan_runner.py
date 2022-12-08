from gda.scan import TurboXasParameters, TurboXasMotorParameters, TurboXasScan
import os.path

class TurboXasScanRunner:
    def __init__(self):
        self.scanFileName=""
    
    def __call__(self, params):
        # print "FrelonScan::__call__ ",params, params.__class__
        if len(params) == 1 :
            self.scanFileName = params[0]
        
        if os.path.isfile(self.scanFileName) == False :
            print "Unable to run scan - couldn't find file called '",self.scanFileName,"'"
            return

        print "Running TurboXAS scan using parameters from xml file : ",self.scanFileName
        
        #Load params from xml file
        turboXasParams = TurboXasParameters.loadFromFile(str(self.scanFileName))
        # print turboXasParams.toXML();
        
        # Show the motor parameters
        turboXasMotorParams = turboXasParams.getMotorParameters();
        print "TurboXAS motor parameters"
        print turboXasMotorParams.toXML()
        
        txasScan = turboXasParams.createScan()
       
        # Run the scan
        txasScan.runScan()
        
turboxas_scan = TurboXasScanRunner()

vararg_alias("turboxas_scan")
