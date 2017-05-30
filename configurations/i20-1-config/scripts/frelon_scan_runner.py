from gda.scan.ede import TimeResolvedExperimentParameters

class FrelonScanRunner:
    def __init__(self):
        self.scanFileName=""
        self.singleSpectrum = False
    
    def __call__(self, params):
        print "FrelonScan::__call__ ",params, params.__class__
        if len(params) > 0:
            self.scanFileName = params[0]
        if len(params) > 1:
            self.singleSpectrum = bool(params[1])
        
        print "Params : filename = ",self.scanFileName," , singleSpectrum = ",self.singleSpectrum

        #Load params from xml file
        timeResolvedParams = TimeResolvedExperimentParameters.loadFromFile(str(self.scanFileName))
        
        # Create time resolved experiment from the params
        theExperiment = timeResolvedParams.createTimeResolvedExperiment()
        
        # Run the scan
        theExperiment.runExperiment()
        
frelon_scan = FrelonScanRunner()

vararg_alias("frelon_scan")
