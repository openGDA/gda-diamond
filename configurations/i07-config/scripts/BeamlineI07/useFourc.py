from gda.factory import Finder
from gdaserver import diff1delta, diff1gamma, diff1chi, diff1theta, diff1omega, diff2delta, diff2gamma, diff2alpha, diff2omega
from gda.device.scannable import ScannableBase
from gda.configuration.properties import LocalProperties
from exceptions import NotImplementedError

class read_only_fourc(ScannableBase):
    
    def getMotors(self):
        diffmode = LocalProperties.get('gda.active.diffractometer.mode')
        
        if diffmode not in {'eh1v', 'eh1h', 'eh2'} :
            raise ValueError("diffractometer mode not set, please run 'eh1h', 'eh1v' or 'eh2'")
        
        motor1 = {'eh1v' : diff1delta, 'eh1h' : diff1delta, 'eh2' : diff2delta}.get(diffmode)
        motor2 = {'eh1v' : diff1gamma, 'eh1h' : diff1gamma, 'eh2' : diff2gamma}.get(diffmode)
        motor3 = {'eh1v' : diff1theta, 'eh1h' : diff1chi, 'eh2' : diff2alpha}.get(diffmode)
        motor4 = {'eh1v' : diff1omega, 'eh1h' : diff1theta, 'eh2' : diff2omega}.get(diffmode)
        
        return motor1, motor2, motor3, motor4
    
    def rawGetPosition(self):
        motor1, motor2, motor3, motor4 = self.getMotors()
        
        return (motor1.getPosition(), motor2.getPosition(), motor3.getPosition(), motor4.getPosition())
    
    def getInputNames(self):
        motor1, motor2, motor3, motor4 = self.getMotors()
        
        return (motor1.getName(), motor2.getName(), motor3.getName(), motor4.getName())
        
    def rawAsynchronousMoveTo(self, pos=None):
        raise NotImplementedError(
            "fc is read only and motors will not move.  Please use fourc or individual motor names." )

    def isBusy(self):
        return False

    def getOutputFormat(self):
        return ("%9.5f", "%9.5f", "%9.5f", "%9.5f")

fc = read_only_fourc()
fc.setName("fc")
