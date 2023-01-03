from gda.scan.ede import TimeResolvedExperimentParameters

class EdeScanRunner:
    def __init__(self):
        self.scanFileName=""
    
    def __call__(self, params):
        # print "FrelonScan::__call__ ",params, params.__class__
        if len(params) > 0:
            self.scanFileName = str(params[0])
               
        if not os.path.isfile(self.scanFileName) :
            print "Unable to run scan - couldn't find file called '",self.scanFileName,"'"
            return
        
        print "Running Ede scan using settings from xml file : ",self.scanFileName

        #Load params from xml file
        timeResolvedParams = TimeResolvedExperimentParameters.loadFromFile(str(self.scanFileName))
        # Create time resolved experiment from the params
        experiment = timeResolvedParams.createTimeResolvedExperiment()
        # Run the scan
        experiment.runExperiment()
        
ede_scan = EdeScanRunner()

vararg_alias("ede_scan")
