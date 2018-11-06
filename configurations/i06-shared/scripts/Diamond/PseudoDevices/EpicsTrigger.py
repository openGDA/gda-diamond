from gda.epics import CAClient;
from gda.device.scannable import ScannableMotionBase;
from time import sleep

#The Class for creating a Pseudo Device that can do Epics caput and caget
class EpicsTriggerClass(ScannableMotionBase):
    def __init__(self, name, pvSet, pvGet,pulseLength):
        self.setName(name);
        self.setInputNames([name]);
        
        self.delay=None;
        self.pulseLength = pulseLength;

        self.setupEpics(pvSet, pvGet);

    def __del__(self):
        self.cleanChannel(self.chSet);
        self.cleanChannel(self.chGet);
    
    def setupEpics(self, pvSet, pvGet):
#        Epics PVs for checking fast scan readiness:
        self.chSet=CAClient(pvSet);  self.configChannel(self.chSet);
        self.chGet=CAClient(pvGet);  self.configChannel(self.chGet);

        
    def configChannel(self, channel):
        if not channel.isConfigured():
            channel.configure();

    def cleanChannel(self, channel):
        if channel.isConfigured():
            channel.clearup();
    
    def setPulseLength(self, newLength):
        self.pulseLength = newLength;
    def setDelay(self, delay):
        self.delay = delay;

    def caget(self):
        try:
            result = float(self.chGet.caget())
        except:
            print "Error getting position"
        return result;

    def caput(self, new_position):
        try:
            self.chSet.caput(new_position);
        except:
            print "Error setting position"
    def trigger(self, pulseLength):
        self.triggerOn();
        sleep(pulseLength);
        self.triggerOff();

    def triggerOn(self):
        self.caput(1);

    def triggerOff(self):
        self.caput(0);
        
    def getPosition(self):
        return self.caget();

    def asynchronousMoveTo(self, newLength):
        if self.delay is not None:
            sleep(self.delay);
            
        self.pulseLength=newLength;
        self.trigger(self.pulseLength);


    def isBusy(self):
        return False;

#    def toFormattedString(self):
#        return self.name + " : " + str( self.getPosition() );

pvTriggerSet = "BL07I-EA-CCD-01:TRIGGER"
pvTriggerGet = pvTriggerSet
pulseLength = 0.1

try:
    del camTrigger
except:
    pass

camTrigger=EpicsTriggerClass('camTrigger', pvTriggerSet, pvTriggerGet, pulseLength);

