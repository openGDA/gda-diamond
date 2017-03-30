# Class to control the DCM "Freeze Y & Z" function

# The control is Shown as "FreezeY & Z" in the DCM screen.
# If Freeze is not set, a change to "Energy (compound)" will cause small compensatory adjustments to 
# "Perpendicular offset" and "Parallel offset". If freeze is set, the two offsets will not change.

#  GDA should write 0/1 to USERIN (0 = don't freeze, 1 = freeze) and read from RBV.

from epics_scripts.pv_scannable_utils import caput, caget

class EpicsDcmFreezeYZ:
    
    def __init__(self, base_pv):
        self.input_pv = base_pv + ':USERIN'
        self.readback_pv = base_pv + ':RBV'

    def get_state(self):
        return caget(self.readback_pv)

    def set_state(self, value):
        try:
            caput(self.input_pv, value)
        except Exception, ex:
            print 'Error in DcmFreezeYZ.set_state()' %(str(ex))

class DummyDcmFreezeYZ:
    currState = 0

    def get_state(self):
        return self.currState

    def set_state(self, value):
        if value < 0 or value > 1:
            print 'Error in DcmFreezeYZ.set_state(): value must be 0 or 1'
        else:
            self.currState = value


class DcmFreezeYZ:
    implementation = None
    
    def __init__(self, live, basePV):
        if live:
            self.implementation = EpicsDcmFreezeYZ(basePV)
        else:
            self.implementation = DummyDcmFreezeYZ()

    def setFrozen(self):
        self.implementation.set_state(1)

    def setUnfrozen(self):
        self.implementation.set_state(0)

    def isFrozen(self):
        return float(self.implementation.get_state()) == 1