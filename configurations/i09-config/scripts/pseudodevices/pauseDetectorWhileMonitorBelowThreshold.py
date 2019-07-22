'''
extending check beam codes to pause and resume a pauseable detector during scan or data collection. 
Created on 1 May 2019

@author: fy65
'''
from gdascripts.scannable.beamokay import reprtime, WaitWhileScannableBelowThresholdMonitorOnly
from gda.epics import CAClient
from java.lang import Runnable, InterruptedException
from time import sleep
from gda.device import DeviceException
from java.util.concurrent import Executors, TimeUnit
from gda.device.scannable import ScannableMotionBase

class PauseResumeDetectorScannable(ScannableMotionBase, Runnable):
    '''
    pause acquisition of a given detector while any status of given scannables returns False, 
    and resume detector acquisition when the status of all monitored scannables returns True.
    
    An ExecutorService is used to run a check beam process at each data point during detector exposure period,
    and will pause or resume the given detector depending on the returns of checked scannables.
    
    Users can set the time in seconds between checks, the default value is 1.0 second.
    '''
    def __init__(self, name, detectorToControl, checkedDevices={}):  # @UndefinedVariable
        self.setName(name)
        self.setInputNames([name])
        self.setOutputFormat(['%f'])
        self.secondsBetweenChecks=1.0
        
        self.detector=detectorToControl
        self.checkedDevices=checkedDevices
        
        self.executor=None
        self.runThread=False
        self.lastStatus=True
        self.secondsToWaitAfterBeamBackUp=5.0
        self.lastStatusDict={}
        for k in checkedDevices.keys():
            self.lastStatusDict[k]=True
        self.shutterClosedByMe=None
            
    def isBusy(self):
        return False
    
    def asynchronousMoveTo(self, secondsBetweenChecks):
        self.secondsBetweenChecks=secondsBetweenChecks
        
    def getPosition(self):
        return self.secondsBetweenChecks
        
    def atScanStart(self):
        print "create a ExecutorService ... "
        self.executor=Executors.newSingleThreadExecutor()
        
    def atScanEnd(self):
        self.runThread=False
        self.shutdownExecutor()
        
    def stop(self):
        self.runThread=False
        self.shutdownExecutor()
        
    def atCommandFailure(self):
        self.runThread=False
        self.shutdownExecutor()
        
    def shutdownExecutor(self):
        if self.executor is not None:
            print " Suhutdown the ExecutorService ..."
            self.executor.shutdown()
            try:
                if not self.executor.awaitTermination(1000, TimeUnit.MILLISECONDS):
                    self.executor.shutdownNow()
            except InterruptedException:
                self.executor.shutdownNow()
            self.executor=None
            
    def __del__(self):
        #triggered when use 'reset_namespace'
        self.shutdownExecutor()
                
    def atPointStart(self):
        self.runThread=True
        if self.executor is None:
            raise Exception("ExecutorService is None!!!")
        self.future=self.executor.submit(self)
        
    def atPointEnd(self):
        self.runThread=False
        if not self.future.isDone():
            self.future.cancel(True)
            
    def handleStatusChange(self,statusdict):
        ## check for status change to provide feedback:
        status=all(statusdict.values())
        if status and self.lastStatus:
            pass # still okay

        if status and not self.lastStatus:
            if statusdict['Electron_Beam'] != self.lastStatusDict['Electron_Beam']:
                self.secondsToWaitAfterBeamBackUp=self.checkedDevices['Electron_Beam'].secondsToWaitAfterBeamBackUp
                print "*** Electron_Beam back up at: " + reprtime() + " . Resume detector exposure in " + str(self.secondsToWaitAfterBeamBackUp) + "s..."
            if statusdict['Top_up'] != self.lastStatusDict['Top_up']:
                self.secondsToWaitAfterBeamBackUp=self.checkedDevices['Top_up'].secondsToWaitAfterBeamBackUp
                print "*** Top_up finished at: " + reprtime() + " . Resume detector exposure in " + str(self.secondsToWaitAfterBeamBackUp) + "s..."
            if statusdict['Front_End_Permit'] != self.lastStatusDict['Front_End_Permit']:
                self.secondsToWaitAfterBeamBackUp=self.checkedDevices['Front_End_Permit'].secondsToWaitAfterBeamBackUp
                print "*** Front_End_Permit: ready in state at: " + reprtime() + " . Resume detector exposure in " + str(self.secondsToWaitAfterBeamBackUp) + "s..."
            self.lastStatus = True
            sleep(self.secondsToWaitAfterBeamBackUp)
            print "*** " + self.name + ":  Resume detector acquisition at: " + reprtime()
            if self.detector.isPaused():
                self.detector.resume()

        if not status and not self.lastStatus:
            pass # beam still down
        
        if not status and self.lastStatus:
            if statusdict['Electron_Beam'] != self.lastStatusDict['Electron_Beam']:
                print "*** Electron_Beam down at: " + reprtime() + " , will pause detector exposure..."
            if statusdict['Top_up'] != self.lastStatusDict['Top_up']:
                print "*** Top_up threshold reached at: " + reprtime() + " , will pause detector exposure..."
            if statusdict['Front_End_Permit'] != self.lastStatusDict['Front_End_Permit']:
                print "*** Front_End_Permit: not ready at: " + reprtime() + " , will pause detector exposure..."
            self.lastStatus = False
            print "*** " + self.name + ": Pause detector acquisition at: " + reprtime()
            if not self.detector.isPaused():
                self.detector.pause()
        self.lastStatusDict=statusdict.copy()
            
    def run(self):
        #TODOs - did not pause analyser tested with checkbeam_d
        status={}
        while (self.runThread):
            for k, v in self.checkedDevices.items():
                status[k] = v._getStatus()
            self.handleStatusChange(status)
            sleep(self.secondsBetweenChecks)

class WaitForScannableState2(WaitWhileScannableBelowThresholdMonitorOnly):
    '''Useful mainly for waiting for a shutter or beamline front-end to open
    '''
    
    def __init__(self, name, scannableToMonitor, secondsBetweenChecks, secondsToWaitAfterBeamBackUp=None, readyStates=['Open'], faultStates=['Fault']):
        WaitWhileScannableBelowThresholdMonitorOnly.__init__( self, name, scannableToMonitor, None, secondsBetweenChecks, secondsToWaitAfterBeamBackUp )
        self.readyStates = readyStates
        self.faultStates = faultStates
    
    def atScanStart(self):
        readyStatesString = self.readyStates[0] if len(self.readyStates)==1 else str(self.readyStates)
        print '=== Beam checking enabled: '+self.scannableToMonitor.getName()+' must be in state: ' + readyStatesString+', currently '+str(self._getStatus())
        self.statusRemainedGoodSinceLastGetPosition = True
        
    def getPosition(self):
        return WaitWhileScannableBelowThresholdMonitorOnly.getPosition(self)
        
    def _getStatus(self):
        pos = self.scannableToMonitor.getPosition()
        if type(pos) in (type(()), type([])):
            pos = pos[0]
        if pos in self.faultStates:
            raise DeviceException(self.name + " found " + self.scannableToMonitor.name + " to be in state: " + pos)
        return pos in self.readyStates

    def handleStatusChange(self, status):
        readyStatesString = self.readyStates[0] if len(self.readyStates)==1 else str(self.readyStates)
        ## check for status change to provide feedback:
        if status and self.lastStatus:
            pass # still okay
        if status and not self.lastStatus:
            delayReport = " . Resuming scan" if not self.secondsToWaitAfterBeamBackUp else (" . Resuming scan in " + str(self.secondsToWaitAfterBeamBackUp) + "s...")
            print "*** " + self.name + ": ready in state " + readyStatesString + " at: " + reprtime() + delayReport
            self.lastStatus = True
            if self.secondsToWaitAfterBeamBackUp:
                sleep(self.secondsToWaitAfterBeamBackUp)
                print "*** " + self.name + ": " + reprtime() + " . Resuming scan now."
        if not status and not self.lastStatus:
            pass # beam still down
        if not status and self.lastStatus:
            print "*** " + self.name + ": not ready: " + reprtime() + " . Pausing scan..."
            self.lastStatus = False
                        
class PauseableDetector():
    '''Implement pause and resume acquisition for a detector, e.g. VG Scienta electron analyser
    '''
    def __init__(self, name, pvname, fastshutters=[], secondsBetweenFastShutterDetector=2.0):
        self.name=name
        self.pvname=pvname
        self.incli=CAClient(pvname+"PAUSE")
        self.outcli=CAClient(pvname+"PAUSE_RBV")
        self.statecli=CAClient(pvname+"DetectorState_RBV") 
        self.pvcli=CAClient(pvname+"ACQ_MODE")
        self.incli.configure()
        self.outcli.configure()
        self.statecli.configure()
        self.pvcli.configure()
        self.fastshutters=fastshutters
        self.secondsBetweenFastShutterDetector=secondsBetweenFastShutterDetector
        self.shutterClosedByMe=None
        
    def pause(self):
        if (int(self.statecli.caget())==1): #currently acquire
            self.incli.caput(1) # pause detector acquisition
            if int(self.pvcli.caget())==0: #in Swept mode
                sleep(self.secondsBetweenFastShutterDetector)
                for shutter in self.fastshutters:
                    if shutter.getPosition() == 'Out':
                        print "Close fast shutter %s after pausing detector acquisition" % shutter.getName()
                        shutter.moveTo('In')
                        self.shutterClosedByMe=shutter            
        
    def resume(self):
        if (int(self.statecli.caget())==1): #currently acquire
            if self.shutterClosedByMe is not None and int(self.pvcli.caget())==0: #in Swept mode
                print "Open fast shutter %s before resuming detector acquisition" % self.shutterClosedByMe.getName()
                self.shutterClosedByMe.moveTo('Out')
                self.shutterClosedByMe=None
                sleep(self.secondsBetweenFastShutterDetector)
            self.incli.caput(0) # resume detector acquisition
        
    def isPaused(self):
        return int(self.outcli.caget())==1
            