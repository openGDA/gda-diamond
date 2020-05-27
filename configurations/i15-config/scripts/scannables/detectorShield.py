from gda.device.scannable import ScannableBase
from gdascripts.messages.handle_messages import simpleLog
from gdascripts.parameters import beamline_parameters
from gdascripts.scannable.epics.PvManager import PvManager
from org.slf4j import LoggerFactory
from time import sleep

class DetectorShield(ScannableBase):
    def __init__(self, name, pvManager):
        self.logger = LoggerFactory.getLogger("DetectorShield")

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
        self.suppressOpenDetectorShieldAtScanStart = False
        self.suppressCloseDetectorShieldAtScanEnd = False
        
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
        if self.suppressOpenDetectorShieldAtScanStart:
            simpleLog("""%s
              Detector Shield open is suppressed.""" % "DetectorShield: ".ljust(80, "*"))
            simpleLog("*"*80)
        else:
            self.openDetectorShield(suppressWaitForOpen=True)

    def openDetectorShield(self, suppressWaitForOpen=False):
        if self.verbose:
            simpleLog("%s:%s() called" % (self.name, self.pfuncname()))

        suppressOpenDiode, suppressOpenWhenDiodeAbove, suppressOpenWhenDiodeBelow = self._parameters()
        if suppressOpenDiode:
            zebraFastShutter = beamline_parameters.JythonNameSpaceMapping().zebraFastShutter
            simpleLog("Forcing fast shutter open...")
            zebraFastShutter.forceOpen()
            self.waitForDiodeState(suppressOpenDiode, suppressOpenWhenDiodeAbove, suppressOpenWhenDiodeBelow)
            zebraFastShutter.forceOpenRelease()
            simpleLog("...Released fast shutter from being forced open")

        simpleLog("Detector Shield Opening...")

        self.pvManager['CON'].caput(self.TIMEOUT, 0)

        if not suppressWaitForOpen:
            self.waitWhileBusy(self.TIMEOUT*2)
            simpleLog("Detector Shield %s" % self.getDetectorShieldStatus())

    def waitForDiodeState(self, suppressOpenDiode, suppressOpenWhenDiodeAbove, suppressOpenWhenDiodeBelow):
        diodeValue=suppressOpenDiode.getPosition()
        print "%r %r " % (suppressOpenWhenDiodeBelow >= diodeValue, diodeValue >= suppressOpenWhenDiodeAbove)
        while (suppressOpenWhenDiodeBelow > diodeValue or diodeValue > suppressOpenWhenDiodeAbove):
            msg = "The value of diode %r is %r which is outside of the range %r to %r, waiting before opening Detector Shield...\n%s\n%s\n%s\n%s" % (
                suppressOpenDiode.name, diodeValue, suppressOpenWhenDiodeBelow, suppressOpenWhenDiodeAbove,
                "If Experimental Hutch lights are enough to exceed threshold, ensure they are switched off.",
                "If the beamstop is not aligned, please stop this script/scan and align it before continuing.",
                "To stop the scan/script use the grey stop button, Not the Red button.", "*"*80)
            self.logger.info(msg)
            print msg
            sleep(10)
            diodeValue=suppressOpenDiode.getPosition()

        self.logger.info("The value of diode %r is %r which is within the range %r to %r, opening Detector Shield..." % (
                suppressOpenDiode.name, diodeValue, suppressOpenWhenDiodeBelow, suppressOpenWhenDiodeAbove))

    def _parameters(self):
        suppressOpenDiode=self._parameter("exposeDetectorShieldSuppressOpenDiode",
            " to define the diode which determines whether the detector shield can open.")
        suppressOpenWhenDiodeAbove=self._parameter("exposeDetectorShieldSuppressOpenWhenDiodeAbove",
            " to define the largest value which allows the detector shield to open.")
        suppressOpenWhenDiodeBelow=self._parameter("exposeDetectorShieldSuppressOpenWhenDiodeBelow",
            " to define the smallest value which allows the detector shield to open.")

        if suppressOpenDiode==None and suppressOpenWhenDiodeAbove==None and suppressOpenWhenDiodeBelow==None:
            msg = "No exposeDetectorShieldSuppressOpen parameters are defined, so the Detector shield will always open"
            self.logger.warn(msg)
            print msg
            return None, None, None

        elif suppressOpenDiode==None or suppressOpenWhenDiodeAbove==None or suppressOpenWhenDiodeBelow==None:
            msg = "All three exposeDetectorShieldSuppressOpen parameters must be defined if any are"
            self.logger.error(msg)
            print msg
            raise Exception(msg)

        return suppressOpenDiode, suppressOpenWhenDiodeAbove, suppressOpenWhenDiodeBelow

    def _parameter(self, parameter, help_text):
        jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
    
        if jythonNameMap[parameter] == None:
            msg = "%s not defined, please add %s='xx' to localStationUser.py%s" % (
                parameter, parameter, help_text)
            self.logger.warn(msg)
            print msg
            return None

        if isinstance(jythonNameMap[parameter], str) or isinstance(jythonNameMap[parameter], unicode):
            if jythonNameMap[jythonNameMap[parameter]]==None:
                raise Exception('Cannot find %s in the jython namespace when trying to lookup %s' % (jythonNameMap[parameter], parameter))
            self.logger.trace("Returning scannable defined by %s as '%s': %s" % (parameter, jythonNameMap[parameter], jythonNameMap[jythonNameMap[parameter]].name))
            return jythonNameMap[jythonNameMap[parameter]]
    
        if isinstance(jythonNameMap[parameter], ScannableBase):
            self.logger.trace("Returning scannable defined by %s as %s" % (parameter, jythonNameMap[parameter].name))
        else:
            self.logger.trace("Returning value defined by %s as %r" % (parameter, jythonNameMap[parameter]))

        return jythonNameMap[parameter]

    def atScanEnd(self):
        if self.suppressCloseDetectorShieldAtScanEnd:
            simpleLog("""%s
              Detector Shield close is suppressed.
              You MUST ensure the shield is closed manually after your scan:
              >>> %s.closeDetectorShield()""" % ("DetectorShield: ".ljust(80, "*"), self.name))
            simpleLog("*"*80)
        elif self.suppressOpenDetectorShieldAtScanStart:
            simpleLog("""%s
              Detector Shield open was suppressed.""" % "DetectorShield: ".ljust(80, "*"))
            simpleLog("*"*80)
        else:
            self.closeDetectorShield(suppressWaitForClose=True)

    def closeDetectorShield(self, suppressWaitForClose=False):
        if self.verbose:
            simpleLog("%s:%s() called" % (self.name, self.pfuncname()))
        else:
            simpleLog("Detector Shield Closing...")
        self.pvManager['CON'].caput(self.TIMEOUT, 1)
        if not suppressWaitForClose:
            self.waitWhileBusy(self.TIMEOUT*2)
            simpleLog("Detector Shield %s" % self.getDetectorShieldStatus())

    def atCommandFailure(self):
        if self.suppressCloseDetectorShieldAtScanEnd:
            simpleLog("Detector Shield close after failure suppressed...")
            return
        if self.verbose:
            simpleLog("%s:%s() called" % (self.name, self.pfuncname()))
        else:
            simpleLog("Detector Shield Closing after failure...")
        self.pvManager['CON'].caput(self.TIMEOUT, 1)

    def stop(self): # This is required because Interrupt Scan Gracefully calls stop, but not atCommandFailure
        if self.suppressCloseDetectorShieldAtScanEnd:
            simpleLog("Detector Shield close after stop suppressed...")
            return
        if self.verbose:
            simpleLog("%s:%s() called" % (self.name, self.pfuncname()))
        else:
            simpleLog("Detector Shield Closing after stop...")
        self.pvManager['CON'].caput(self.TIMEOUT, 1)

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
