'''
Created on 10 Jun 2019

@author: fy65
'''
from gda.device.detector import DetectorBase, NexusDetector, NXDetectorData
from zurich.ziPythonClientMessager import ZiDAQServerMessager
from gda.device import Detector
from gda.factory import ConfigurableBase
from org.slf4j import LoggerFactory
from time import sleep
from gda.data.nexus.extractor import NexusGroupData

class ZurichDetector(DetectorBase, NexusDetector):
    '''
    classdocs
    '''


    def __init__(self, name, ipaddress, port, terminator, separator, dataPath='/dev4206/demods/0/sample', staticsPath='/dev4206/scopes/0/wave'):
        '''
        Constructor
        '''
        self.logger=LoggerFactory.getLogger(ZurichDetector)
        self.setName(name)
        self.length=1
        self.collectionTime=None
        self.communicator=ZiDAQServerMessager(ipaddress, port, terminator, separator)
        self.dataPath=dataPath
        self.staticsPath=staticsPath
        
    def configure(self):
        self.logger.debug("{}: configure called", self.getName())
        self.super__configure()
        #ConfigurableBase.configure(self)
     
    def setCollectionTime(self, t):
        self.logger.debug("{}: set collection time called with {}",self.getName(), t)
        self.collectionTime=t 
        
    def getDataDimensions(self):
        return [self.communicator.get('/dev4206/scopes/0/length')]
    
    def prepareForCollection(self):
        self.communicator.set(['/dev4206/demods/0/enable', 1]) # Enable the demodulator output
        self.communicator.set(['/dev4206/demods/0/rate', 100]) # set transfer rate 100 S/s
        self.communicator.subscribe(self.dataPath)
        
        self.communicator.loadModule('scope')
        self.communicator.subscribeToModule('scope', self.staticsPath)
        self.communicator.setValueToModule('scope', 'scopeModule/mode', 0)
        self.communicator.setValueToModule('scope', 'scopeModule/historylength', 1)
        
        self.communicator.set(['/dev4206/scopes/0/channels/0/inputselect', 0]) #select voltage input
        self.communicator.set(['/dev4206/scopes/0/length', 4096]) #set sample length
        self.communicator.set(['/dev4206/scopes/0/time', 5]) #set sample rate
        
        self.communicator.set(['/dev4206/scopes/0/enable', 1]) # start continuous triggering
        
    def collectData(self):
        self.logger.debug("{}: collectData called", self.getName())
        self.communicator.execute('scope')
        
    def waitWhileBusy(self):
        self.logger.trace("{}: Waiting for acquire to finish...", self.getName());
        while self.getStatus() == Detector.BUSY:
            sleep(0.1)
        self.logger.trace("{}: Acquiring finshed.", self.getName());
     
    def getStatus(self):
        if self.communicator.progress('scope') < 1:
            return Detector.BUSY
        return Detector.IDLE
    
    def createsOwnFiles(self):
        return False
    
    def atScanStart(self):
        self.super__atScanStart()
        self.firstReadoutInScan=True
        
    def atScanEnd(self):
        self.super__atScanEnd()
        self.firstReadoutInScan=False
        
    def atCommandFailure(self):
        self.super__atCommandFailure()
        self.stop()
    
    def stop(self):
        self.super__stop()
        self.communicator.stopModuleCommandExecution('scope')
        
    def readout(self):
        self.logger.debug("{}: readout called.", self.getName())

        #dynamics readout
        data_d = self.communicator.poll(self.getCollectionTime(), 10, 0, True) # poll demodulator outputs 
        x = data_d[self.dataPath]['x'][:-100].mean() # mean of demodulator output in the last 100 samples (1 s)
        y = data_d[self.dataPath]['y'][:-100].mean()
        
        #statics readout
        data_s = self.communicator.read('scope', True)
        static = data_s[self.staticsPath][0][0]['wave'].flatten().mean() * data_s[self.staticsPath][0][0]['channelscaling'][0]
        print static, x, y
        data = NXDetectorData(self)
        #set data to plot during scan
        data.setPlottableValue("x", x)
        data.setPlottableValue("y", y)
        data.setPlottableValue("static", static)
        #add data to be written to file
        data.addData(self.getName(), 'x', NexusGroupData(x), "")
        data.addData(self.getName(), 'y', NexusGroupData(y), "")
        data.addData(self.getName(), 'static', NexusGroupData(static), "")
        if self.firstReadoutInScan:
            self.logger.debug("Adding metadata for file writter")
            data.addElement(self.getName(), "count_time", NexusGroupData(self.getCollectionTime()), "sec", False)
            self.firstReadoutInScan=False
        return data
            
        
    
    