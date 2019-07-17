'''
A Scannable that can be paused and resumed automatically depending on condition of event updated from 
 a MonitorListener or an IObserver if present.

Created on 20 Feb 2019

@author: fy65
'''

from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from org.slf4j import LoggerFactory
import math
from utils.ExceptionLogs import localStation_exception
import sys
from time import sleep
import weakref
from gdascripts.utils import caput, caget

GDA_PASUED_TTH_PV="BL21I-MO-ARM-01:TTH:GDA:PAUSED"

class PauseableScannable(ScannableMotionBase):
    '''
    make a Scannable object pause-able using position compare algorithm with set-able tolerance.
    An instance of this class supports pause and resume during a moving request irrespective of 
    whether the actual hardware pause-able or not. It also supports EPICS MonitorListener and/or 
    IObserver objects, if specified, which will pause and resume current request depending on 
    event updated from a given PV and/or from a given IObserver object.  
    '''

    def __init__(self, name, scannable, tolerance, monitoredPvs={}, observers={}):
        '''
        Constructor
        @param name:         name of this wrapper scannable
        @param scannable:    the scannable representing a hardware device
        @param tolerance:    the tolerance within which motor is regarded as reached its position
        @param monitoredPvs: a dictionary defining a named tuple specifying (PV_name, MonitorListener) pair
        @param observers:    a dictionary defining a named tuple specifying (IObservable, IObserver) pair
        @param parent:       the caller of this object - used to ensure monitors or observers are removed when this object is deleted.
        '''
        self.logger=LoggerFactory.getLogger("PauseableScannable")
        self.setName(name)
        self.setInputNames([name])
        self.setOutputFormat(scannable.getOutputFormat())
        self.setLevel(5)
        self.monitoredPvs=monitoredPvs
        self.observers=observers
        self.cacli={}
        self.ml={}
        if self.monitoredPvs:
            for key, value in monitoredPvs.iteritems():
                self.cacli[key]=CAClient(value[0])
                self.ml[key]=value[1].setScannable(self)
        self.monitors={}
        self.observers={}
        self.observables={}
        if self.observers:
            for key, value in observers.iteritems():
                self.observables[key]=value[0]
                self.observers[key]=value[1].setScannable(self)
        self.newLaserStatus=None
        self.scannable=scannable
        self.demandPosition=None
        self.currentPosition=None
        self._tolerance=tolerance
        self.stoppedByMe=False
        self.pausedByMe=False
        self.movedByme=False
        self.monitorsAddedAtScanStart=False
        self.parent=weakref.ref(self)
        
    def pause(self):
        '''pause the motion by calling EPICS motor to stop without stop this object
        '''
        self.pausedByMe=True
        try:
            caput(GDA_PASUED_TTH_PV, 1)
            self.scannable.stop() # stop the actual motor to emulate pause in this object
        except:
            self.pausedByMe=False
            self.logger.debug("{}: failed to stop epics motor", self.getName())
            raise
        
    def resume(self):
        '''resume the motion by reset EPICS motor to move to the original target position only if the motor is paused by this object.
        '''
        if self.pausedByMe:
            if self.getDemandPosition() is None:
                print "%s cannot resume motion as the demand position is None"
            else:
                caput(GDA_PASUED_TTH_PV, 0)
                self.scannable.asynchronousMoveTo(self.getDemandPosition())
            self.pausedByMe=False
        else:
            print "%s: cannot resume motion which is not stopped by myself." % self.getName()
            self.logger.debug("{}: Cannot resume motion which is not stopped be by myself.", self.getName())
        
    def setTolerance(self, tolerance):
        '''set the tolerance for motor position comparing. 
        '''
        self._tolerance=tolerance
        
    def getTolerance(self):
        '''return the tolerance for this scannable position
        '''
        return self._tolerance
     

    def addMonitorToPVs(self):
        '''add monitors listener to is corresponding PV for each of the keys and cache the monitors for each key for later remove
        '''
        try:
            if self.monitoredPvs :
                for key in self.cacli.iterkeys():
                    if not self.cacli[key].isConfigured():
                        #create channels
                        self.cacli[key].configure()
                        sleep(1.0) #need to wait channel creation to complete
                    #add monitors to the channel
                    print "add monitors for %s" % key
                    self.monitors[key] = self.cacli[key].camonitor(self.ml[key])
#                     print "monitors %s is added to %s " % (self.monitors[key], self.cacli[key])
        except:
            localStation_exception(sys.exc_info(), "add monitors error.")
#             typ, exception, traceback =sys.exc_info()
#             print  typ, exception, traceback
            raise
    
    def addObservers(self):
        if self.observers:
            for key in self.observers.iterkeys():
                print "add observer for %s" % key
                self.observables[key].addIObserver(self.observers[key])

    def atScanStart(self):
        self.addMonitorToPVs()
        self.addObservers()          
        self.monitorsAddedAtScanStart=True

    def removeMonitorFromPVs(self):
        '''remove monitors from corresponding PV for given keys
        '''
        if self.monitors:
            for key in self.monitors.iterkeys(): #remove monitors
                self.cacli[key].removeMonitor(self.monitors[key])
                if self.cacli[key].isConfigured(): #destroy channel
                    self.cacli[key].clearup()
            self.monitors = {}
            
    def removeObservers(self):
        if self.observers:
            for key in self.observers.iterkeys():
                self.observables[key].deleteIObserver(self.observers[key])
                
    def atScanEnd(self):
        self.removeMonitorFromPVs()
        self.removeObservers()
        self.monitorsAddedAtScanStart=False
        if caget(GDA_PASUED_TTH_PV)==1:
            caput(GDA_PASUED_TTH_PV, 0)

    def getPosition(self):
        try:
            self.currentPosition=float(self.scannable.getPosition())
            return self.currentPosition
        except:
            print "Error returning current position from motor '%s'" % self.getName()
            return 0
        finally:
            if self.movedByme and not self.isBusy(): #when is done
                self.removeMonitorFromPVs()
                self.removeObservers()
                self.movedByme=False
    
    def getDemandPosition(self):
        return self.demandPosition
    
    def asynchronousMoveTo(self,new_position):
        self.demandPosition=float(new_position) #cache the target position
        try:
            if not self.monitorsAddedAtScanStart:
                self.addMonitorToPVs()
                self.addObservers()
            sleep(1.0) #give time for monitor value to update
            self.movedByme=True
            #handling nitrogen is off or lase at Yellow zone at start of motion! 
            if self.pausedByMe: return
            self.stoppedByMe=False
            self.pausedByMe=False
            print "move %s to %f" % (self.getName(), self.demandPosition)
            self.scannable.asynchronousMoveTo(self.demandPosition)
        except:
            print "error moving to position: %f" % self.demandPosition
            if not self.monitorsAddedAtScanStart:
                self.removeMonitorFromPVs()
                self.removeObservers()
            self.movedByme=False

    def moveTo(self, new_position):
        self.asynchronousMoveTo(new_position)
        self.waitWhileBusy()
        if not self.monitorsAddedAtScanStart:
            self.removeMonitorFromPVs()
            self.removeObservers()
        self.movedByme=False
        
    def isBusy(self):
        if self.movedByme:
            if not self.pausedByMe and math.fabs(self.scannable.getMotor().getTargetPosition() - self.getDemandPosition()) > self._tolerance :
                if not self.stoppedByMe:
                    print "%s is stopped from outside GDA. remove monitors also." % self.getName()
                    self.removeMonitorFromPVs()
                    self.removeObservers()
                return False #someone changed motor position request in EPICS
            else:
                return (not (math.fabs(self.scannable.getPosition() - self.getDemandPosition()) <= self._tolerance)) or self.scannable.isBusy()
        else:
            return self.scannable.isBusy()
    
    def atCommandFailure(self):
        self.stop()
        
    def stop(self):
        try:
            #stop real motor
            self.stoppedByMe=True
            self.scannable.stop()
            #stop this scannable
            self.demandPosition=float(self.scannable.getPosition())
            if caget(GDA_PASUED_TTH_PV)==1:
                caput(GDA_PASUED_TTH_PV, 0)
        except:
            raise
        finally:    
            self.removeMonitorFromPVs()
            self.removeObservers()
            self.movedByme=False
            self.pausedByMe=False
            self.monitorsAddedAtScanStart=False
        
    def toFormattedString(self):
        return self.name + " : " + str(self.getPosition())
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print "remove monitors and observer if any"
        self.removeMonitorFromPVs()
        self.removeObservers()
        
    def __del__(self):
        print "remove monitors or observer if any on delete this object."
        self.removeMonitorFromPVs()
        self.removeObservers()

