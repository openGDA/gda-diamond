"""
To control the temperature in using LS340 in rasor and poms

David Burn

from poms.scannable.temperatureScannable import temperatureScannable
rasorTemp = temperatureScannable("rasor_temp")


September 2018
PID when using helium
p=65, i = 10, d = 0


#self.ca.caput("ME01D-EA-TCTRL-01:RANGE_S", 5)               # heater at 50 W

"""


from gda.device.scannable import ScannableBase
from gda.epics import CAClient
from java.lang import Thread, Runnable
import time





class temperatureScannable(ScannableBase):
    def __init__(self, name):
        self.setName(name);
        self.setInputNames(['sample_temp']);
        self.setExtraNames(['cryo_temp']);
        self.setOutputFormat(["%3.3f","%3.3f"]);
        self.Units=['Kelvin'];

        self.ca = CAClient();
        
        self.iambusy = False
        self.runningThread = False
        
        self.setPoint = 300
        self.threshold = 0.5 # K
        self.timeWithinThreshold = 30 # s
        
        self.controlSensor = 0 # 0=cryo, 1=sample
        self.rampRate = 5 #K / min


    def atScanStart(self):
        return;

    def atScanEnd(self):
        return;

    def asynchronousMoveTo(self,newPos):
        self.iambusy = True
        self.setPoint = float(newPos)
        #repeat as sometimes the message does not get through
        self.ca.caput("ME01D-EA-TCTRL-01:SETP_S", float(newPos))    # set set point
        time.sleep(4)
        self.ca.caput("ME01D-EA-TCTRL-01:SETP_S", float(newPos))    # set set point
        time.sleep(4)
        
        print "Set temperature to ", newPos
        
        mythread = Thread(checkTemperatureThread(self))
        mythread.start()
        
    def getPosition(self):
        return [float(self.ca.caget("ME01D-EA-TCTRL-01:KRDG0")), float(self.ca.caget("ME01D-EA-TCTRL-01:KRDG1"))]
        
    def isBusy(self):
        return self.iambusy  
    
    def stop(self):
        print "stopping temperature scannable"
        self.runningThread = False
        
    def getSpeed(self):
        return (self.rampRate / 60.0) #return speed in K / s

    def setupStepMode(self):
        while (self.ca.caget("ME01D-EA-TCTRL-01:RAMPST") != '0.0'):
            self.ca.caput("ME01D-EA-TCTRL-01:RAMPST_S", 1)
            time.sleep(2) 
            self.ca.caput("ME01D-EA-TCTRL-01:RAMPST_S", 0)
            time.sleep(4) 
        print "Temperature sweep disabled"

    def setupRampMode(self):
        while (self.ca.caget("ME01D-EA-TCTRL-01:RAMPST") != '1.0'):
            self.ca.caput("ME01D-EA-TCTRL-01:RAMPST_S", 0)
            time.sleep(2) 
            self.ca.caput("ME01D-EA-TCTRL-01:RAMPST_S", 1)
            time.sleep(4)
        print "Temperature sweep enabled"

        self.ca.caput("ME01D-EA-TCTRL-01:RAMP_S", self.rampRate)               # set the ramp rate in K / min
        time.sleep(1)


class checkTemperatureThread(Runnable):
    def __init__(self, myparent):
        self.parent = myparent
        self.parent.runningThread = True
        self.stableStartTime = 0

    def run(self):
        while self.parent.runningThread:
            if (abs(self.parent.getPosition()[self.parent.controlSensor] - self.parent.setPoint) > self.parent.threshold ):
                self.stableStartTime = time.time()
            else:
                if ((time.time() - self.stableStartTime) > self.parent.timeWithinThreshold):
                    self.parent.runningThread = False
                    self.parent.iambusy = False
                    break
                
