from time import sleep
from gda.device.scannable import ScannableMotionBase

"""
    Purpose: make detectors repeatable
"""
 
class Average(ScannableMotionBase):

   def __init__(self, name, scannable):
    self.setName(name)
    self.setInputNames([name])
    self.setOutputFormat(["%5.5g"])
    self.scannable = scannable
    self.setLevel(7)
    self.points=2
    self.sleeptime=0.1

   def isBusy(self):
    return self.scannable.isBusy()

   def getPosition(self):
       value=0
       for i in range(self.points):
          value = value + self.scannable.getPosition()
          sleep(self.sleeptime)
       return value/self.points

   def asynchronousMoveTo(self,newPosition):
       self.points=newPosition

# average_d7current=Average("average_d7current", d7current)
# average_dj7current=Average("average_dj7current", dj7current)
# average_d3current=Average("average_d3current", d3current)
