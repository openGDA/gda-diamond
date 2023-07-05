'''
class to work around Merlin detector hanging at 5 seconds exposure reported by beamline.https://jira.diamond.ac.uk/browse/I16-742 
our observation shows the hanging is a result of detector state out of sync between LabView and EPICS.
We don't understand the real cause of this!

Only 2 states of the detector : 0 Idle and 1 Acquire are used here!
    
Created on Jul 4, 2023

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from uk.ac.diamond.daq.concurrent import Async
from gov.aps.jca.event import MonitorEvent
from gov.aps.jca.event import MonitorListener
import time

class MerlinKickerWhenAcquisitionHangs(ScannableMotionBase, MonitorListener):

    def __init__(self, name, start_pv, state_pv):
        '''
        Constructor - require detector's start and state PV names
        '''
        self.setName(name)
        #overwrite default to make zero input extra names scannable
        self.setInputNames([])
        self.setExtraNames([])
        self.setOutputFormat([])
        self.start_channel = CAClient(start_pv)
        self.start_channel.configure()
        self.state_channel = CAClient(state_pv)
        self.state_channel.configure()
        self.monitor = None
        self.timeout = 10.0
        self.exposure_time = 5.0
        self.submit = None
        
    def atScanStart(self):
        if self.monitor is None:
            self.monitor = self.state_channel.camonitor(self)
        
    def atScanEnd(self):
        if self.monitor:
            self.state_channel.removeMonitor(self.monitor)
        self.monitor = None 
        
    def monitorChanged(self, mevent):
        '''monitor detector state 
        - on acquire, it spins up a time tracking thread which will kick detector start when hanging after exposure time plus timeout elapsed
        - on idle, it cancels the time tracking thread
        '''
        detector_state = int(mevent.getDBR().getEnumValue()[0])
        if detector_state == 1:
            self.start_time = time.time()
            self.submit = Async.submit(lambda : self.kick_detector_start_when_hang(), "Merlin state monitor thread from %1$s", self.getName())
        if detector_state == 0:
            if self.submit is not None and not self.submit.isDone():
                self.submit.cancel(True)
        
    def kick_detector_start_when_hang(self):
        while (time.time() - self.start_time) < (self.exposure_time + self.timeout):
            time.sleep(0.1)
        # try to kick start merlin again when hanging
        self.start_channel.caput(1)
        
    def stop(self):
        if self.submit is not None and not self.submit.isDone():
            self.submit.cancel(True)
        if self.monitor:
            self.state_channel.removeMonitor(self.monitor)
        self.monitor = None 
    
    def set_exposure_time(self, t):
        self.exposure_time = t
    
    def get_expsoure_time(self):
        return self.exposure_time
    
    def set_timeout(self, t):
        self.timeout = t
    
    def get_timeout(self):
        return self.timeout
    
    # implementation of zero input extra names scannable
    def getPosition(self):
        return None
    
    def asynchronousMoveTo(self, t):
        #zero input
        pass
    
    def isBusy(self):
        return False
    
merlin_watcher = MerlinKickerWhenAcquisitionHangs("merlin_watcher", "BL16I-EA-DET-13:Merlin2:Acquire", "BL16I-EA-DET-13:Merlin2:DetectorState_RBV")
    