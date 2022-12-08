from gda.configuration.properties import LocalProperties
from gda.jython import Jython
from gda.factory import Finder

class Scan_Utilities:
    
    def __init__(self):
        print "constructor"
        self.JythonNS = Finder.findSingleton(Jython)
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
