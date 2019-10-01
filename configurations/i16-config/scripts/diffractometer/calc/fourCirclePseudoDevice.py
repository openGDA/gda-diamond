from gda.device.scannable import PseudoDevice
from Jama import Matrix
import beamline_objects as BLobjects

from jarray import array
from java.lang import String

class fourCirclePseudoDevice(PseudoDevice):

	def __init__(self,name,euler):
		self.name = name
		self.euler = euler
		self.inputNames = array(['tth', 'phi','chi','eta'], String)

	def asynchronousMoveTo(self,new_position):
		new_tth_position = new_position[0]
		new_euler_position = [new_position[1],new_position[2],new_position[3]]
		BLobjects.getTth().asynchronousMoveTo(new_tth_position)
		self.euler.asynchronousMoveTo(new_euler_position)

	#
	# If the euler PD is busy then so is this device
	#
	def isBusy(self):
		return self.euler.isBusy() or BLobjects.getTth().isBusy()

	#
	# Returns the current Eulerian coordinates as an array
	#
	def getPosition(self):
		return [BLobjects.getTth().getPosition(),self.euler.getPosition()[0],self.euler.getPosition()[1],self.euler.getPosition()[2]]

	#string representation of the data in an object
	def toString(self):
		return self.getName() + ": tth:" + `BLobjects.getTth().getPosition()` + " euler:" + `self.euler.getPosition()`

