from gda.configuration.properties import LocalProperties
class Scan_Utilities:
    #global SRSWriteAtFileCreation
    def __init__(self):
        print "constructor"
        self.JythonNS = finder.find("command_server")
        self.metaData = []
        self.filePrefix=""
        self.expt=""
        
    def setScanFilePrefix(self, prefix):
        LocalProperties.set("gda.data.scan.datawriter.filePrefix", prefix)
        self.filePrefix=prefix
    
    def setExperimentName(self, expt):
        LocalProperties.set("gda.data.scan.datawriter.srsExperiment", expt)
       
    
    def setMetaData(self, metaData):
        self.metaData=[]
        self.metaData.append(metaData)
        SRSWriteAtFileCreation = metaData
        print SRSWriteAtFileCreation
        self.JythonNS.placeInJythonNamespace("SRSWriteAtFileCreation",SRSWriteAtFileCreation,None)
    
    def addMetaData(self, metaData):
        self.metaData.append(metaData)
        command=""
        for s in self.metaData:
            command = command + s + "\n"
        SRSWriteAtFileCreation = command
        print SRSWriteAtFileCreation
        self.JythonNS.placeInJythonNamespace("SRSWriteAtFileCreation",SRSWriteAtFileCreation, None)
    
