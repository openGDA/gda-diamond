from gda.device.scannable import ScannableBase
from gdascripts.scannable.epics.PvManager import PvManager

class DetectorShield(ScannableBase):
    def __init__(self, name, pvManager):
        self.name = name
        self.pvManager = PvManager()
        self.pvManager = pvManager
        
        self.setName(name);
        self.setInputNames([name])
        self.setExtraNames([]);
        self.setOutputFormat(["%5.5g"])
        self.setLevel(1)
        self.state=-1
        
        self.verbose = True
        
        self.TIMEOUT=5
        
        self.OPEN=1
        self.OPENING=2
        self.CLOSED=3
        self.CLOSING=4

    def __repr__(self):
        return "%s(name=%r, pvManager=%r)" % (self.__class__.__name__, self.name, self.pvManager)

    # Either getPosition or rawGetPosition is required for default implementation of __str__():
    def getPosition(self):
        return self.pvManager['STA'].caget()

    def asynchronousMoveTo(self, position):
        if self.verbose:
            print "%s:%s() called with position=%r" % (self.name, self.pfuncname(), position)

    def atScanStart(self):
        self.pvManager['CON'].caput(self.TIMEOUT, 0)
        if self.verbose:
            print "%s:%s() called" % (self.name, self.pfuncname())

    def atScanEnd(self):
        self.pvManager['CON'].caput(self.TIMEOUT, 1)
        if self.verbose:
            print "%s:%s() called" % (self.name, self.pfuncname())

    def atCommandFailure(self):
        self.pvManager['CON'].caput(self.TIMEOUT, 1)
        if self.verbose:
            print "%s:%s() called" % (self.name, self.pfuncname())

    def stop(self): # This is required because Interrupt Scan Gracefully calls stop, but not atCommandFailure
        self.pvManager['CON'].caput(self.TIMEOUT, 1)
        if self.verbose:
            print "%s:%s() called" % (self.name, self.pfuncname())

    def isBusy(self):
        state = int(self.getPosition())
        if self.verbose and state != self.state:
            print "%s:%s() state transitioned from %r to %r" % (self.name, self.pfuncname(), self.state, state)
            self.state = state
        if state in (self.OPEN, self.CLOSED):
            return False
        elif state in (self.OPENING, self.CLOSING):
            return True
        raise Exception("%r is not %r, %r, %r, or %r" % (self.state, self.OPEN, self.CLOSED, self.OPENING, self.CLOSING))

    def pfuncname(self):
        import traceback
        return "%s" % traceback.extract_stack()[-2][2]
