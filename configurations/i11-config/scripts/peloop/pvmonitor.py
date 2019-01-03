'''
Created on 15 Feb 2011

@author: fy65
'''
from gov.aps.jca.event import MonitorListener
from gda.device.scannable import ScannableMotionBase
from savepedata import SaveData
from adc import adc

class PVMonitor(ScannableMotionBase, MonitorListener):
    def __init__(self, name):
        self.setName(name)
        self.setInputNames([])
        self.setExtraNames(["filename"])
        self.counter=0
        self.numberofgates=0
        self.filename=None
        self.filenames=[]
        self.collectionNumber=0

    def resetCounter(self):
        self.counter=0
        
    def resetRepetition(self):
        self.collectionNumber=0
        
    def setNumberOfGates(self, num):
        self.numberofgates=num
        
    def setFilename(self, filename):
        self.filename=filename
        
    def atScanStart(self):
        self.resetCounter()
        self.resetRepetition()
        
    def atScanEnd(self):
        pass
        
    def atPointStart(self):
        self.resetCounter()
        self.resetRepetition()
        
    def atPointEnd(self):
        pass
    
    def getExtraNames(self):
        repetition=[]
        for i in range(self.collectionNumber):
            repetition[i]="collectionNumber-"+str(i)
        return repetition

    def rawGetPosition(self):
        return self.filenames
    
    def rawAsynchronousMoveTo(self,position):
        pass
    
    def rawIsBusy(self):
        return False
    
    def monitorChanged(self, mevent):
        datasets={}
        if self.counter < self.numberofgates:
            if self.counter not in datasets:
                datasets[self.counter]=[]
            datasets[self.counter] = [float(val) for val in mevent.getDBR().getDoubleValue()]
            self.counter += 1
        if self.counter == self.numberofgates-1:
            self.filenames[self.collectionNumber]=self.filename+"-"+self.getName()+"-"+str(self.collectionNumber)
            #kick off a thread to process and save data so not to block monitor event process here.
            savedata=SaveData(name=self.getName()+"-"+str(self.collectionNumber), args=(self.filenames[self.collectionNumber]+".dat", "w"), kwargs=datasets)
            savedata.start()
            self.collectionNumber+=1
            self.resetCounter()
            