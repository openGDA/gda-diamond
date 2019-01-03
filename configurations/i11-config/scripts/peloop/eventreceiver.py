'''
Created on 15 Feb 2011

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from gda.factory import FactoryException
from gov.aps.jca import CAException
import sys

#EPICS PVs
evrdelaypv="BL11I-EA-EVR-01:FRONT-DELAY:SET"
evrdelayrbv="BL11I-EA-EVR-01:FRONT-DELAY"
evrwidthpv="BL11I-EA-EVR-01:FRONT-WIDTH:SET"
evrwidthrbv="BL11I-EA-EVR-01:FRONT-WIDTH"
evrenablepv="BL11I-EA-EVR-01:FRONT-ENABLE:SET"
evrpolaritypv="BL11I-EA-EVR-01:FRONT-POLARITY:SET"

class EventReceiver(ScannableMotionBase):
    
    def __init__(self, name, delay=evrdelaypv, delayrbv=evrdelayrbv, width=evrwidthpv, widthrbv=evrwidthrbv, enable=evrenablepv, polarity=evrpolaritypv):
        self.setName(name)
        self.setInputNames(["delay", "width"])
        self.setExtraNames([])
        self.delay=CAClient(delay)
        self.delayrbv=CAClient(delayrbv)
        self.width=CAClient(width)
        self.widthrbv=CAClient(widthrbv)
        self._enable=CAClient(enable)
        self.polarity=CAClient(polarity)
    
    # function generator controls
    def enableField(self):
        try:
            if not self._enable.isConfigured():
                self._enable.configure()
            self._enable.caput(1)
        except FactoryException, e:
            print "create channel error (%s): %s" % (self._enable.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self._enable.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def disable(self):
        try:
            if not self._enable.isConfigured():
                self._enable.configure()
            self._enable.caput(0)
        except FactoryException, e:
            print "create channel error (%s): %s" % (self._enable.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self._enable.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def setWidth(self, width):
        try:
            if not self.width.isConfigured():
                self.width.configure()
            self.width.caput(width)
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.width.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.width.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getWidth(self):
        try:
            if not self.widthrbv.isConfigured():
                self.widthrbv.configure()
            return float(self.widthrbv.caget())
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.widthrbv.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.widthrbv.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def setDelay(self, delay):
        try:
            if not self.delay.isConfigured():
                self.delay.configure()
            self.delay.caput(delay)
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.delay.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.delay.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getDelay(self):
        try:
            if not self.delayrbv.isConfigured():
                self.delayrbv.configure()
            return float(self.delayrbv.caget())
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.delayrbv.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.delayrbv.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def normalPolarity(self):
        try:
            if not self.polarity.isConfigured():
                self.polarity.configure()
            self.polarity.caput(0)
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.polarity.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.polarity.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def invertPolarity(self):
        try:
            if not self.polarity.isConfigured():
                self.polarity.configure()
            self.polarity.caput(1)
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.polarity.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.polarity.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def atScanStart(self):
        '''enableField event channel'''
        self.enableField()
        
    def atScanEnd(self):
        '''disable event channel'''
        self.disable()
         
    def getPosition(self):
        try:
            return self.getDelay(), self.getWidth()
        except:
            print "failed to get (delay, width) tuple: ", sys.exc_info()[0]
            raise

    def getTargetPosition(self):
        delay=0.0
        width=0.0
        try:
            if not self.width.isConfigured():
                self.width.configure()
            width=float(self.width.caget())
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.width.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.width.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        try:
            if not self.delay.isConfigured():
                self.delay.configure()
            delay=float(self.delay.caget())
        except FactoryException, e:
            print "create channel error (%s): %s" % (self.delay.getChannel().getName(),e)
        except CAException, e:
            print "caput Error (%s): %s" % (self.delay.getChannel().getName(),e)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        return delay,width
       
    def asynchronousMoveTo(self,new_position):
        try:
            self.setDelay(new_position[0])
            #print "delay set"
            self.setWidth(new_position[1])
            #print "width set"
        except:
            print "error moving to position: (%s, %s)" % (new_position[0], new_position[1])
            raise

    def isBusy(self):
        #print abs(self.getPosition()[0] - self.getTargetPosition()[0])
        return (abs(self.getPosition()[0] - self.getTargetPosition()[0])>0.000001)

#    def toString(self):
#        return self.name + " : " + str(self.getPosition())
