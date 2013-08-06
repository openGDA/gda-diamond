from gda.scan import StaticScan
from gda.analysis import ScanFileHolder, RCPPlotter
from time import sleep
from gda.scan import ConcurrentScan

class MythenAcquisition:
    def __init__(self, mythen, test):
        self.outputFile = ""
        self.rawFile = ""
        self.calibFile = '/dls_sw/b18/software/mythen/MythenSoft/module/calibration.dat'
        self.data = None
        self.acquiring = False
        self.header = "no header"
        self.mythen = mythen
        self.test = test
    
    def setHeader(self, header):
        self.header = header
    
    def getCalibLocation(self):
        return self.calibFile
    
    def getRawFileName(self):
        return self.rawFile
    
    def acquire(self, time):
        self.mythen.setCollectionTime(time)
        scan = ConcurrentScan([self.test, 0, 0, 1, self.mythen])
        scan.runScan()
        
        self.rawFile = str(self.mythen.getDataDirectory()) +"/"+ self.mythen.getCurrentFilename()+".raw"
        prefix = self.rawFile[:self.rawFile.rfind("-")]
        fileNum = self.rawFile[self.rawFile.rfind("-"):self.rawFile.rfind(".")]
        self.outputFile = prefix + fileNum + ".dat"

        self.createSRS()
        
    def createSRS(self):
        self.data = ScanFileHolder()
        self.data.loadSRS(self.outputFile)

    def plotRaw(self):
        RCPPlotter.plot("Mythen Controller",self.data[3], self.data[1])
    
    def plotCalib(self):
        RCPPlotter.plot("Mythen Controller",self.data[0], self.data[1])
    
    def isAcquiring(self):
        return self.acquiring
    
#Alternate method using non depricated file loader

#data = ScanFileLoader("84054-mythen-0001", "/dls/b18/data/2013/cm5943-2/").getSFH()
#data.getNames()
#array(java.lang.String, [u'Angle', u'Count', u'Error', u'Channel'])

#channels = data.getLazyDataset("Channel")
#counts = data.getLazyDataset("Count")
#angles = data.getLazyDataset("Angle")

#RCPPlotter.plot("Mythen Controller",angles, counts)