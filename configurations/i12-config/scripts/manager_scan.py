from java.io import File
from uk.ac.gda.client.tomo.basic.beans import BasicTomographyParameters
from uk.ac.gda.util.beans.xml import XMLHelpers

class ScanManager():
    
    def __init__(self):
        self.scans = []
        
    def addBasicTomographyScan(self,file_name):
        # get the bean from the 
        bean = XMLHelpers.readBean(File(file_name),BasicTomographyParameters)
        self.addScan(bean)
    
    def addScan(self,bean):
        self.scans.insert(0, bean)
        
    def nextScan(self):
        try :
            return self.scans.pop()
        except :
            return None
    
    def viewQuedScans(self):
        for i in range(len(self.scans)):
            print(self.scans[i])
            
    def clear(self):
        self.scans = []