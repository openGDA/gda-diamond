from gda.scan.ede import TimeResolvedExperimentParameters

class FrelonScanRunner:
    def __init__(self):
        self.scanFileName=""
    
    def __call__(self, params):
        # print "FrelonScan::__call__ ",params, params.__class__
        if len(params) > 0:
            self.scanFileName = str(params[0])
               
        if os.path.isfile(self.scanFileName) == False :
            print "Unable to run scan - couldn't find file called '",self.scanFileName,"'"
            return
        
        print "Running Ede LinearExperiment using settings from xml file : ",self.scanFileName

        #Load params from xml file
        timeResolvedParams = TimeResolvedExperimentParameters.loadFromFile(str(self.scanFileName))
        
        # Create time resolved experiment from the params
        theExperiment = timeResolvedParams.createTimeResolvedExperiment()
        
        # Run the scan
        theExperiment.runExperiment()
        
frelon_scan = FrelonScanRunner()

vararg_alias("frelon_scan")
