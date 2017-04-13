from gda.device.scannable import ScannableBase
from gdascripts.messages.handle_messages import simpleLog
from gdascripts.scannable.epics.PvManager import PvManager

class DetectorShield(ScannableBase):
    def __init__(self, name, pvManager):
        self.name = name
        self.pvManager = PvManager() # Just to get PyDev completion
        self.pvManager = pvManager
        
        self.setName(name);
        self.setInputNames([])
        self.setExtraNames([]);
        self.setOutputFormat([])
        self.setLevel(1)
        self.state=-1
        
        self.verbose = False
        self.ignoreFault = False
        
        self.TIMEOUT=10
        
        self.FAULT=0
        self.OPEN=1
        self.OPENING=2
        self.CLOSED=3
        self.CLOSING=4
        
        self.stateDescriptions = {
                self.FAULT:     "Fault",
                self.OPEN:      "Open",
                self.OPENING:   "Opening",
                self.CLOSED:    "Closed",
                self.CLOSING:   "Closing",
            }

    def __repr__(self):
        return "%s(name=%r, pvManager=%r)" % (self.__class__.__name__, self.name, self.pvManager)

    # Either getPosition or rawGetPosition is required for default implementation of __str__():
    def getPosition(self):
        return None

    def atScanStart(self):
        self.openDetectorShield(suppressWait=True)

    def openDetectorShield(self, suppressWait=False):
        self.pvManager['CON'].caput(self.TIMEOUT, 0)
        if self.verbose:
            simpleLog("%s:%s() called" % (self.name, self.pfuncname()))
        simpleLog("Detector Shield Opening...")
        if not suppressWait:
            self.waitWhileBusy(self.TIMEOUT*2)
            simpleLog("Detector Shield %s" % self.getDetectorShieldStatus())

    def atScanEnd(self):
        self.closeDetectorShield(suppressWait=True)

    def closeDetectorShield(self, suppressWait=False):
        self.pvManager['CON'].caput(self.TIMEOUT, 1)
        if self.verbose:
            simpleLog("%s:%s() called" % (self.name, self.pfuncname()))
        else:
            simpleLog("Detector Shield Closing...")
        if not suppressWait:
            self.waitWhileBusy(self.TIMEOUT*2)
            simpleLog("Detector Shield %s" % self.getDetectorShieldStatus())

    def atCommandFailure(self):
        self.pvManager['CON'].caput(self.TIMEOUT, 1)
        if self.verbose:
            simpleLog("%s:%s() called" % (self.name, self.pfuncname()))
        else:
            simpleLog("Detector Shield Closing after failure...")

    def stop(self): # This is required because Interrupt Scan Gracefully calls stop, but not atCommandFailure
        self.pvManager['CON'].caput(self.TIMEOUT, 1)
        if self.verbose:
            simpleLog("%s:%s() called" % (self.name, self.pfuncname()))
        else:
            simpleLog("Detector Shield Closing after stop...")

    def isBusy(self):
        # Note that if the detector shield fails to fully open or close, this
        #      will silently stay busy until manual intervention corrects it.
        #      Since this should never be busy for more than around 10 seconds,
        #      we should report it's state periodically.
        helptext = " Go to the 'Experimental Hutch' EPICS Synoptic, click on Det Shield (near the top) and reset it." + \
            "\n If Detector Shield is disconnected, do '%s.ignoreFault=True' to ignore fault conditions." % self.name
        state = int(self.pvManager['STA'].caget())
        if self.verbose and state != self.state:
            simpleLog("%s:%s() state transitioned from %r to %r" % (self.name, self.pfuncname(), self.state, state))
            self.state = state
        if state in (self.OPEN, self.CLOSED):
            return False
        elif state in (self.OPENING, self.CLOSING):
            return True
        elif state == self.FAULT:
            if self.ignoreFault:
                return False
            raise Exception("Problem with detector shield. EPICS reports a FAULT.\n" + helptext)
        raise Exception("Problem with detector shield. EPICS reports an invalid state. %r is not %r, %r, %r, or %r on %r\n%s" % (
                        state, self.OPEN, self.CLOSED, self.OPENING, self.CLOSING, self.pvManager['STA'].pvName, helptext))

    def getDetectorShieldStatus(self):
        state = int(self.pvManager['STA'].caget())
        return self.stateDescriptions.get(state, "INVALID STATE")

    def pfuncname(self):
        import traceback
        return "%s" % traceback.extract_stack()[-2][2]

'''
def openMarShield():
    """
    Open Detector shield
    """
    try:
        status = beamline.getValue(None,"Top","-RS-ABSB-06:CON")
        if (status == 0):
            simpleLog("Detector shield already open")
        else:
            beamline.setValue("Top","-RS-ABSB-06:CON", 0)
            
            # wait and check shield has opened
            sleep(3)
            status = beamline.getValue(None,"Top","-RS-ABSB-06:CON")
            if (status == 0):
                simpleLog("Detector shield opened")
            else:
                simpleLog("Detector shield failed to open - status is: " + `status`)
    except:
        typ, exception, traceback = sys.exc_info()
        handle_messages.log(None, "Problem opening Detector shield - ", typ, exception, traceback)

def closeMarShield():
    """
    Close Detector shield
    """
    try:
        status = beamline.getValue(None,"Top","-RS-ABSB-06:CON")
        if (status == 1):
            simpleLog("Detector shield already closed")
        else:
            beamline.setValue("Top","-RS-ABSB-06:CON", 1)
            
            # wait and check shield has closed
            sleep(3)
            status = beamline.getValue(None,"Top","-RS-ABSB-06:CON")
            if (status == 1):
                simpleLog("Detector shield closed")
            else:
                simpleLog("Detector shield failed to close - status is: " + `status`)
    except:
        typ, exception, traceback = sys.exc_info()
        handle_messages.log(None, "Problem closing mar shield - ", typ, exception, traceback)
'''