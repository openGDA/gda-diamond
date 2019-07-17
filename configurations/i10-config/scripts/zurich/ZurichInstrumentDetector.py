'''
Created on 10 Jun 2019

@author: fy65
'''
from gda.device.detector import DetectorBase
from zurich import ziPythonClientMessager
from gda.device import Detector
import time

class ZurichDetector(DetectorBase):
    '''
    classdocs
    '''


    def __init__(self, name, ipaddress, port, terminator, separator):
        '''
        Constructor
        '''
        self.setName(name)
        self.length=1
        self.collectionTime=None
        self.communicator=ziPythonClientMessager(ipaddress, port, terminator, separator)
        self.dataPath='/dev4206/demods/0/sample'
        self.staticsPath='/dev4206/scopes/0/wave'
     
    def setCollectionTime(self, t):
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
        self.communicator.execute('scope')
        
    def getStatus(self):
        if self.communicator.progress('scope') < 1:
            return Detector.BUSY
        
    def readout(self):
        # collect data

        for i in range(20):
            time.sleep(1.1) # wait while collecting data
            
            #dynamics readout
            data_d = self.communicator.poll(self.getCollectionTime(), 10, 0, True) # poll demodulator outputs 
            x = data_d[self.dataPath]['x'][:-100].mean() # mean of demodulator output in the last 100 samples (1 s)
            y = data_d[self.dataPath]['y'][:-100].mean()
            
            #statics readout
            data_s = self.communicator.read(True)
            static = data_s[self.staticsPath][0][0]['wave'].flatten().mean() * data_s[self.staticsPath][0][0]['channelscaling'][0]
            return static, x, y
    
    