from gda.device.enumpositioner import EnumPositionerBase
from gda.device import DeviceException
from gdaserver import beam_selector_readback, imaging_hint_positioner

class BeamSelector(EnumPositionerBase):
    
    IMAGING = "Imaging"
    DIFFRACTION = "Diffraction"
    NO_BEAM = "No beam"
    
    def __init__(self, name, internal_positioner, internal_diffraction, internal_dark, internal_imaging):
   
        self.setName(name)
        self.internal_positioner = internal_positioner
        self.external_to_internal = {
            BeamSelector.IMAGING: internal_imaging,
            BeamSelector.DIFFRACTION: lambda: internal_diffraction,
            BeamSelector.NO_BEAM: lambda: internal_dark}
        
        self.setPositionsInternal([BeamSelector.DIFFRACTION, BeamSelector.IMAGING, BeamSelector.NO_BEAM])
        self.internal_positioner.addIObserver(lambda source, argument: self.notifyIObservers(self, argument))
        
    def rawAsynchronousMoveTo(self, position):
        internal_position = self.external_to_internal.get(position)
        try:
            self.internal_positioner.asynchronousMoveTo(internal_position())
        except:
            raise DeviceException("Unknown position requested for " + self.getName() + ": " + position)
    
    def rawGetPosition(self):
        internal_position = self.internal_positioner.getPosition()
        try:
            return next(key for key, value in self.external_to_internal.items() if value() == internal_position)
        except:
            return BeamSelector.NO_BEAM
    
    def isBusy(self):
        return self.internal_positioner.isBusy()
    
beam_selector_jy = BeamSelector("beam_selector_jy", beam_selector_readback, "Diffraction beam", "No beam", imaging_hint_positioner.getPosition)
