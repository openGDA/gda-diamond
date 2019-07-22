'''
Created on 10 Jun 2019

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from zurich.ziPythonClientMessager import ZiDAQServerMessager

class ZurichScannable(ScannableMotionBase):
    '''
    classdocs
    '''


    def __init__(self, name, ipaddress, port, terminator, separator):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.setOutputFormat(["%f"])
        self.path=None
        self.communicator=ZiDAQServerMessager(ipaddress, port, terminator, separator)
        
    def getPath(self):
        return self.path

    def setPath(self,path):
        self.path=path
    
    def getPosition(self):
        value=self.communicator.get(self.path)
        return value[self.path]['value'][0]
    
    def asynchronousMoveTo(self, newpos):
        if isinstance(newpos, (list, tuple)):
            self.path=newpos[0]
            self.setInputNames([self.path])
        else:
            raise ValueError("asynchronousMoveTo takes a path-value pair as list or tuple.")
        self.communicator.set(list(newpos))
    
    def isBusy(self):
        return False
    