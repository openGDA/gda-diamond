import sys
import time
from gda.device.detector import DetectorBase
from gda.factory import Finder
from gda.configuration.properties import LocalProperties
from gda.epics import CAClient

from gdascripts.messages import handle_messages
from gdascripts.parameters import beamline_parameters
from threading import Thread
ca=CAClient()
# to read a floating point number from EPICS use
# float(ca.caget("PVNAME"))
# to set a value in EPICS use
# ca.put("PVNAME", value)


class toggle_DAC:
    def __init__(self, pvName, startVal, delay, endVal):
        self.done=True
        self.pvName = pvName
        self.startVal = startVal
        self.delay = delay
        self.endVal = endVal
        self.exceptionType=None
        self.exception=None
        self.traceback=None
        pass

    def __call__(self):
        try:
            self.exceptionType=None
            self.exception=None
            self.traceback=None
            ca.put(self.pvName, self.startVal)
            time.sleep(self.delay)
            ca.put(self.pvName, self.endVal)
        except:
            self.exceptionType, self.exception,self. traceback = sys.exc_info()
        finally:
            self.done = True
    

class DacHiLow(DetectorBase):
    def __init__(self, name, pvName, startVal, endVal ):
        self.name = name
        self.toggler = toggle_DAC(pvName, startVal, self.collectionTime, endVal)
        self.thread = None
        
    def createsOwnFiles(self):
        return False
    
    def collectData(self):
        if self.isBusy():
            raise Exception("DACHiLow collectData already active")
        self.toggler.delay = self.collectionTime
        self.thread = Thread(target=self.toggler, name="dacHiLow" )
        self.thread.start()

    def waitWhileBusy(self):
        if self.thread is not None:
            self.thread.join()
            self.thread = None
        
    def isBusy(self):
        return self.thread is not None  and self.thread.isAlive()
    
    def readout(self):
        return 1;

    def getDescription(self):
        return "DacHiLow:"+ self.toggler.pvName
    
    def getDetectorID(self):
        return "DacHiLow"
    
    def getDetectorType(self):
        return "DacHiLow"
    
