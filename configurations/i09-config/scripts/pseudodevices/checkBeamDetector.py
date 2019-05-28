'''
Created on 2 May 2019

@author: fy65
'''

from gda.device.scannable import ScannableMotionBase
from gov.aps.jca.event import MonitorListener
from time import sleep
from org.slf4j import LoggerFactory
from gda.epics import CAClient
from utils.ExceptionLogs import localStation_exception
import sys

class EpicsPVThresholdMonitorListener(MonitorListener):
    ''' a Threshold Monitor Listener used to monitor any PV value changes
    when the PV value falls below a given threshold it pauses the given detector;
    when the PV value rises above a given threshold it will resumes the paused detector after a specified number of seconds.  
    '''
    def __init__(self, name, thresold, secondsBetweenChecks=1.0, secondsToWaitAfter=5.0, detectorToControl=None):
        self.logger=LoggerFactory.getLogger("EpicsPVThresholdMonitorListener")
        self.name=name
        self.detector=detectorToControl
        self.threshold=thresold
        self.secondsToWaitAfter=secondsToWaitAfter
        self.secondsBetweenChecks=secondsBetweenChecks
        self.lastValue=600.0
        self.first=True
        self.pausedByMe=False
        
    def setScannable(self, s):
        self.detector=s
        return self
        
    def monitorChanged(self, mevent):
        newValue=float(mevent.getDBR().getDoubleValue()[0])
        if self.detector is None:
            raise ValueError("scannable to pause/resume detector is not set!")
        if (newValue - self.lastValue)>self.secondsBetweenChecks:
            if not self.detector.isPaused() and newValue <= self.threshold:
                print "'%s' is updated to %f which is below the threshold '%f' " % (self.name, newValue, self.threshold)
                if self.detector.isRunning():
                    self.detector.pause()
                    self.pausedByMe=True
                self.logger.info("'{}' is updated to {} which is below the threshold '{}' ", self.name, newValue, self.threshold)
            elif self.detecor.isPaused() and newValue > self.threshold:
                sleep(self.secondsToWaitAfter)
                print "'%s' is updated to %f which is above the threshold '%f' " % (self.name, newValue, self.threshold)
                if self.pausedByMe and self.detector.isRunning():
                    self.detector.resume()
                    self.pausedByMe=False
                self.logger.info("{}' is updated to {} which is above the threshold '{}' ", self.name, newValue, self.threshold)
            self.lastValue=newValue
        if self.first: #last value must be initialised when monitor is first added 
            self.lastValue=newValue
            self.first=False
            
class EpicsPVStateMonitorListener(MonitorListener):
    '''a State Monitor Listener used to monitor the state value of a PV
    when the PV state value fall inside the given readStates, it resumes the paused detector after a specified number of seconds;
    when the PV state value not in the given readyStates, it pauses the given detector. 
    '''
    def __init__(self, name, readyStates=['Open'], states_dict={0:'Fault', 1:'Open',2:'Opening',3:'Closed',4:'Closing'}, secondsBetweenChecks=1.0, secondsToWaitAfter=60.0, detectorToControl=None):
        self.logger=LoggerFactory.getLogger("EpicsPVStateMonitorListener")
        self.name=name
        self.detector=detectorToControl
        self.readyStates=readyStates
        self.states_dict=states_dict
        self.secondsToWaitAfter=secondsToWaitAfter
        self.pausedByMe=False
        
    def setScannable(self, s):
        self.detector=s
        return self
        
    def monitorChanged(self, mevent):
        newValue=int(mevent.getDBR().getEnumValue()[0])
        if self.detector is None:
            raise ValueError("scannable to pause/resume detector is not set!")
        print "%s' is updated to state '%s' " % (self.name, self.states_dict[newValue])
        self.logger.info("{}' is updated to state '{}' ", self.name, self.states_dict[newValue])
        if self.detector.isPaused() and self.states_dict[newValue] in self.readyStates:
            if self.pausedByMe and self.detector.isRunning():
                sleep(self.secondsToWaitAfter)
                self.detector.resume()
        elif not self.detector.isPaused() and not self.states_dict[newValue] in self.readyStates:
            if self.detector.isRunning():
                self.detector.pause()
                self.pausedByMe=True
   
PV_MonitorListener_Dictionary={'topup_time' : ("SR-CS-FILL-01:COUNTDOWN",EpicsPVThresholdMonitorListener('topup_time_listener', 5, secondsBetweenChecks=1.0, secondsToWaitAfter=5.0)),
                               'ring_current'  : ("SR-DI-DCCT-01:SIGNAL",EpicsPVThresholdMonitorListener('ring_current_listener', 190.0, secondsBetweenChecks=1.0, secondsToWaitAfter=5.0)),       
                               'FE_beam_permit'  : ("FE09I-CS-BEAM-01:STA",EpicsPVStateMonitorListener('FE_beam_permit_listener', secondsToWaitAfter=60.0))}  
      
class PauseDetectorScannable(ScannableMotionBase):
    '''
    a detector capable of pause/resume detector collection during scan depending on the states of given PVs.
    The detector must has pause/resume capability which accessible via PVs.
    '''

    def __init__(self, name, pvname, detector, monitoredPvs={}):
        '''
        Constructor
        '''
        self.logger=LoggerFactory.getLogger("PauseDetectorScannable")
        self.setName(name)
        self.detector=detector
        self.monitoredPvs=monitoredPvs
        self.setInputNames([])
        self.setExtraNames([name+"_paused"])
        self.setOutputFormat(['%.0f'])
        self.setLevel(6)
        self.cacli={}
        self.ml={}
        if self.monitoredPvs:
            for key, value in monitoredPvs.iteritems():
                self.cacli[key]=CAClient(value[0])
                self.ml[key]=value[1].setScannable(self)
        self.monitors={}
        #detector pause control PVs
        self.pvname=pvname
        self.incli=CAClient(pvname+"PAUSE")
        self.outcli=CAClient(pvname+"PAUSE_RBV")
        self.statecli=CAClient(pvname+"DetectorState_RBV") 
        self.incli.configure()
        self.outcli.configure()
        self.statecli.configure()
        
    def pause(self):
        if (int(self.statecli.caget())==1): #currently acquire
            self.incli.caput(1)
            print "%s: Pause '%s'" % (self.getName(), self.detector.getName())
            self.logger.info("{}: Pause '{}'", self.getName(), self.detector.getName())
       
    def resume(self):
        if (int(self.statecli.caget())==1): #currently acquire
            self.incli.caput(0)
            print "%s: Resume '%s'" % (self.getName(), self.detector.getName())
            self.logger.info("{}: Resume '{}'", self.getName(), self.detector.getName())
        
    def isPaused(self):
        return int(self.outcli.caget())==1
    
    def isRunning(self):
        return int(self.statecli.caget())==1
    
    def addMonitorToPVs(self):
        '''add monitors listener to is corresponding PV for each of the keys and cache the monitors for each key for later remove
        '''
        try:
            if self.monitoredPvs :
                for key in self.cacli.iterkeys():
                    if not self.cacli[key].isConfigured():
                        #create channels
                        self.cacli[key].configure()
                        sleep(1.0) #required to make sure channel is created before adding monitor listener
                    #add monitors to the channel
                    print "add monitor listener '%s' to '%s'" % (self.ml[key],key)
                    self.monitors[key] = self.cacli[key].camonitor(self.ml[key])
#                     print "monitors %s is added to %s " % (self.monitors[key], self.cacli[key])
        except:
            localStation_exception(sys.exc_info(), "add monitors error.")
            raise
        
    def removeMonitorFromPVs(self):
        '''remove monitors from corresponding PV for given keys
        '''
        if self.monitors:
            for key in self.monitors.iterkeys(): #remove monitors
                self.cacli[key].removeMonitor(self.monitors[key])
                deleted=self.monitors.pop(key, None)
                self.logger.debug("Delete '{}' listener = {}", key, deleted)
                if self.cacli[key].isConfigured(): #destroy channel
                    self.cacli[key].clearup()
            self.monitors = {}
            
    def atScanStart(self):
        self.addMonitorToPVs()
        
    def atScanEnd(self):
        self.removeMonitorFromPVs()
    
    def getPosition(self):
        return self.isPaused()
    
    def asynchronousMoveTo(self, new_pos):
        pass
    
    def isBusy(self):
        return False
    
    def stop(self):
        self.removeMonitorFromPVs()
        
    def atCommandFailure(self):
        self.removeMonitorFromPVs()
        
    def __del__(self):
        print "remove monitors if any on delete this object."
        self.removeMonitorFromPVs()

#detector_pause_scannable=PauseDetectorScannable("detector_pause_scannable", "BL09I-EA-DET-01:CAM:", ew4000, monitoredPvs=PV_MonitorListener_Dictionary)  # @UndefinedVariable