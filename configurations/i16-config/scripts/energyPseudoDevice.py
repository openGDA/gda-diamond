from gda.device.scannable import PseudoDevice


import beamline_info as BLinfo

from Jama import Matrix


class energyPseudoDevice(PseudoDevice):

	def __init__(self,name,wavelength):
		self.name = name
		self.wavelength = wavelength # the wavelength pd

	def asynchronousMoveTo(self,new_position):
		BLinfo.setEnergy(new_position)

	#
	# If the euler PD is busy then so is this device
	#
	def isBusy(self):
		return self.wavelength.isBusy()

	#
	# Returns the current Eulerian coordinates as an array
	#
	def getPosition(self,tth=None,theta=None,chi=None,phi=None,UB=None,wl=None):
		return  BLinfo.getEnergy()

	#string representation of the data in an object
	#def toString(self):
	#	return self.getName() + ":" + `self.formatPosition(None,self.getPosition())`

	def __call__(self):
		return self.formatPosition(None,self.getPosition())
