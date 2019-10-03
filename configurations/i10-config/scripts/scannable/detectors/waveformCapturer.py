'''
Created on 13 May 2016

@author: fy65
'''
from gda.device.detector import DetectorBase
from gda.epics import CAClient
from gda.jython import InterfaceProvider
from gda.data import NumTracker
from gda.jython import InterfaceProvider

class WaveformCapturer(DetectorBase):
    '''
    read-only detector to capture a data array from specified PV
    '''
    def __init__(self, name, pvname):
        '''
        Constructor
        '''
        self.setName(name)
        self.pv=pvname
        self.caclient=CAClient(pvname)
        self.pointNumber=0
        
    def collectData(self):
        #read-only waveform does not need to be triggered
        pass
    
    def getStatus(self):
        #read-only waveform always available
        return 0
    
    def readout(self):
        try:
            if not self.caclient.isConfigured():
                self.caclient.configure()
                output=self.caclient.cagetArrayDouble()
                self.caclient.clearup()
            else:
                output=self.caclient.cagetArrayDouble()
            return self.writeDataToFile(output)
        except Exception, err:
            print "Error returning current position", err
            raise Exception

    def getDataDimensions(self):
        try:
            if not self.caclient.isConfigured():
                self.caclient.configure()
                output=int(self.caclient.getElementCount())
                self.caclient.clearup()
            else:
                output=float(self.caclient.getElementCount())
            return output
        except:
            print "Error returning element count"
            return 1
       
    def createsOwnFiles(self):
        return True
    
    def writeDataToFile(self, data=[]):
        filenumber = NumTracker("i10").getCurrentFileNumber();
        waveformfilename=str(InterfaceProvider.getPathConstructor().createFromDefaultProperty())+"/"+ str("i10-")+str(filenumber)+"-"+str(self.getName())+"_"+str(self.pointNumber)+".dat"
        print waveformfilename
        datafile=open(waveformfilename, 'w')
        for value in data:
            datafile.write(str(value)+'\n')
        datafile.flush()
        datafile.close()
        return waveformfilename
    
    def atScanStart(self):
        if not self.caclient.isConfigured():
            self.caclient.configure()
        self.pointNumber=0

    def atPointStart(self):
        self.pointNumber+=1
              
    def atScanEnd(self):
        if self.caclient.isConfigured():
            self.caclient.clearup()
        self.pointNumber=0

