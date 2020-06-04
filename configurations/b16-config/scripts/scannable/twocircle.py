import java
#import gda.device.scannable.ScannableMotionBase
import gda.device.scannable.ScannableMotionBase

"""
    Purpose:       TO-DO
    Author:        TO-DO
    Date:          TO-DO

    This class is a template for writing your own Psuedo Device.  It must contain
    at least a constructor and the  mandatory methods:
        isBusy(self)
        getPosition(self)
        asynchronousMoveTo(self,newPosition)
"""

class TwoCircle(gda.device.scannable.ScannableMotionBase):

    def __init__(self, name, theta, ttheta):
        self.name = name
        self.theta = theta
        self.ttheta = ttheta
        self.setInputNames(['theta'])
        self.setExtraNames(['ttheta'])
        self.setOutputFormat(['%.4f', '%.4f'])
        self.theta_offset = 0.0

    def setOffset(self, theta_offset=None):
        if theta_offset==None:
            self.theta_offset = self.theta.getPosition()
        else:
            self.theta_offset = theta_offset

    def isBusy(self):
        return self.theta.isBusy() or self.ttheta.isBusy()

    def getPosition(self):
        return [ self.theta.getPosition()-self.theta_offset, self.ttheta.getPosition()]

    def asynchronousMoveTo(self,newPosition):
        self.theta.asynchronousMoveTo(newPosition + self.theta_offset)
        self.ttheta.asynchronousMoveTo(2*newPosition)
