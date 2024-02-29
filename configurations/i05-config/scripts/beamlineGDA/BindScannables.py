from time import sleep
'''
Created on 1 Dec 2013
Purpose: bind position of slave scannables to master scannable through linear dependence comprising offset of slave and step of slave per master unit
@author: i05user
'''
class BindScannables(ScannableMotionBase):
   """Binds two scannables, Slave against Master, via square polynom dependence"""
   def __init__(self, name, scannableMaster,scannableSlave):
    self.setName(name)
    self.setInputNames([name])
    self.setOutputFormat(["%5.5g"])
    self.Master = scannableMaster
    self.Slave = scannableSlave
    self.SlaveOffset = 0
    self.SlaveStep = 0
    self.SlaveSquare = 0
    self.setLevel(7)

   def isBusy(self):
    return self.Master.isBusy() or self.Slave.isBusy()

   def getPosition(self):
       return self.Master.getPosition()

   def asynchronousMoveTo(self,newPosition):
       self.Master.asynchronousMoveTo(newPosition)
       self.Slave.asynchronousMoveTo(self.getSlavePositionFor(newPosition))

   def getSlaveOffset(self):
        return self.SlaveOffset
   def setSlaveOffset(self,offset):
        self.SlaveOffset=offset
        
   def getSlaveStep(self):
        return self.SlaveStep
   def setSlaveStep(self,step):
        self.SlaveStep=step

   def getSlaveSquare(self):
        return self.SlaveOffset
   def setSlaveSquare(self,offset):
        self.SlaveOffset=offset
        
   def getSlavePositionFor(self,newpos):
        return self.SlaveOffset + self.SlaveStep*newpos + self.SlaveSquare*newpos*newpos


class BindScannablesISR(ScannableMotionBase):

   def __init__(self, name, scannableMaster,scannableSlave):
    self.setName(name)
    self.setInputNames([name])
    self.setOutputFormat(["%5.5g"])
    self.Master = scannableMaster
    self.Slave = scannableSlave
    self.SlaveOffset = 0
    self.SlaveStep = 0
    self.SlaveSquare = 0
    self.setLevel(7)

   def isBusy(self):
    return self.Master.isBusy() or self.Slave.isBusy()

   def getPosition(self):
       return self.Master.getPosition()

   def asynchronousMoveTo(self,newPosition):
       self.Master.asynchronousMoveTo(newPosition)
       self.Slave.asynchronousMoveTo(self.getSlavePositionFor(newPosition))

   def getSlaveOffset(self):
        return self.SlaveOffset
   def setSlaveOffset(self,offset):
        self.SlaveOffset=offset

   def getSlaveStep(self):
        return self.SlaveStep
   def setSlaveStep(self,step):
        self.SlaveStep=step

   def getSlavePositionFor(self,newpos):
        return self.SlaveOffset + self.SlaveStep/sqr(abs(newpos))

