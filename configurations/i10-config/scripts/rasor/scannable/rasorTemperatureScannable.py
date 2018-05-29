"""
To control the temperature in rasor

use instead of ls340 scannable which has problems setting the position when decreasing tempearature.

David Burn
"""


from gda.device.scannable import ScannableBase
from gda.epics import CAClient
from java.lang import Thread, Runnable
import time

class rasorTemperatureScannable(ScannableBase):
    def __init__(self, name):
        self.setName(name);
        self.setInputNames(['sample_temp']);
        self.setExtraNames(['cryo_temp']);
        self.setOutputFormat(["%3.3f","%3.3f"]);
        self.Units=['Kelvin'];

        self.ca = CAClient();
        
        self.iambusy = 0 
        self.runningThread = False
        
        self.setPoint = 300
        self.threshold = 0.2 # K
        self.timeWithinThreshold = 30 # s


    def atScanStart(self):
        return;

    def atScanEnd(self):
        return;
      
        
    def asynchronousMoveTo(self,newPos):
        self.iambusy = 1
        self.setPoint = float(newPos)
        self.ca.caput("ME01D-EA-TCTRL-01:RAMPST_S", 0)              # ramp off
        time.sleep(1)                                             # message does not get through epics if there is no wait
        self.ca.caput("ME01D-EA-TCTRL-01:RANGE_S", 5)               # heater at 50 W
        time.sleep(1)
        self.ca.caput("ME01D-EA-TCTRL-01:SETP_S", float(newPos))    # set set point
        
        newThread = checkTemperatureThread(self)
        t = Thread(newThread)
        t.start()
        
    def getPosition(self):
        return [float(self.ca.caget("ME01D-EA-TCTRL-01:KRDG0")), float(self.ca.caget("ME01D-EA-TCTRL-01:KRDG1"))]
        
    def isBusy(self):
        return self.iambusy  
    
    
        

class checkTemperatureThread(Runnable):
    def __init__(self, myparent):
        self.parent = myparent
        self.parent.runningThread = True
        self.stableStartTime = 0

    def run(self):
        while self.parent.runningThread:
            if (abs(self.parent.getPosition() - self.parent.setPoint) > self.parent.threshold ):
                self.stableStartTime = time.time()
            elif ((time.time() - self.stableStartTime) > self.parent.timeWithinThreshold):
                self.parent.runningThread = False
                self.parent.iambusy = 0
                break
                
