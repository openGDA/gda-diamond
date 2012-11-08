from gda.device.scannable import PseudoDevice
def chif(PseudoDevice)	#
	# Constructor.  Must have six motors to control.
	#
   def __init__(self,name,storedAngles):
      self.setName(name)
      self.setInputNames(array(['chi_t'], String))
      self.setExtraNames()
      self.ekcm = EulerianKconversionModes.EulerianKconversionModes()
      self.storedAngles = storedAngles

      self.SO = 'SO'
      self.SO=ShelveIO.ShelveIO()
      self.SO.path=ShelveIO.ShelvePath+'SO'
      self.SO.setSettingsFileName('SO')
      self.Etaoff=None
      
