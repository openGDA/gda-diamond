from gda.device.scannable import ScannableMotionBase, EpicsScannable

class KeithleyGain(ScannableMotionBase):
    
    def __init__(self, name, root_pv):
        """BL16B-DI-FEMTO-01
        """
        self.name = name
        self.inputNames = ['exponent']
        self.extraNames = ['gain_string', 'gain']
        self.outputFormat = ['%i', '%s', '%.0e']
        
        self._configure_epics_scannable(root_pv + ':Gain')
    
    def rawAsynchronousMoveTo(self, exponent):
        if exponent < 3 or exponent > 10:
            raise ValueError("Exponent must from 3 to 10 inclusive")
        self.epics_scn(int(exponent) - 3)
    
    def waitWhileBusy(self):
        self.epics_scn.waitWhileBusy()
        
    def isBusy(self):
        return self.epics_scn.isBusy()

    def rawGetPosition(self):
        return self.epics_scn() + 3, self.epics_scn.getValueAsString(), 10 ** (self.epics_scn()+3)
    
    def _configure_epics_scannable(self, pv):
        self.epics_scn = EpicsScannable()
        self.epics_scn.name = self.name + '_epics_scn'
        self.epics_scn.pvName = pv
        self.epics_scn.setUseNameAsExtraName(True)
        self.epics_scn.setHasUnits(False)
        self.epics_scn.setGetAsString(False)
        self.epics_scn.outputFormat = ['%i']
        self.epics_scn.configure()

