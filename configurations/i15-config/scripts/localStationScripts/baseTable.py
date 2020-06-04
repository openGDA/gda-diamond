from gda.device import DeviceException
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient

class BaseTable(ScannableMotionBase):
	'''
	PD for moving all three base jacks of diffractometer together 
	'''
	def __init__(self, name, beamline, root, j1, j2, j3, tol):
		self.setName(name)
		self.pvRoot = root
		self.tol = tol
		self.j1 = j1
		self.j2 = j2
		self.j3 = j3
		self.beamline = beamline

	def isBusy(self):
		"""
		Is busy if at least one of j1, j2 or j3 is busy
		"""
		return ( self.j1.isBusy() or self.j2.isBusy() or self.j3.isBusy() )

	def getPosition(self):
		"""
		Returns the height at the centre of the table
		"""
		self._calculateHeightAndOffsets()
		error = self._checkPositionError()
		
		if not error is None:
			print error

		return self.averageHeight

	def asynchronousMoveTo(self, newPos):
		"""
		Moves j1, j2 and j3 at same time, maintaining relative jack offsets
		"""
		self._calculateHeightAndOffsets()
		error = self._checkPositionError()

		if not error is None:
			raise DeviceException(error)
		
		self.setVelocities()
		
		self.j1.asynchronousMoveTo(newPos + self.j1offset)
		self.j2.asynchronousMoveTo(newPos + self.j2offset)
		self.j3.asynchronousMoveTo(newPos + self.j3offset)

	def _calculateHeightAndOffsets(self):
		j1 = self.j1.getPosition()
		j2 = self.j2.getPosition()
		j3 = self.j3.getPosition()
		
		# Note that j1 & j2 are at one end of the table, but j3 is at the other
		# end, so the average height is not a simple average of the three.
		self.averageHeight = ( (j1 + j2) / 2 + j3 ) / 2
		
		self.j1pos = j1
		self.j2pos = j2
		self.j3pos = j3
		self.j1offset = self.j1pos - self.averageHeight
		self.j2offset = self.j2pos - self.averageHeight
		self.j3offset = self.j3pos - self.averageHeight

	def _checkPositionError(self):
		
		if (abs(self.j1offset) <= self.tol and abs(self.j2offset) <= self.tol
										   and abs(self.j3offset) <= self.tol ):
			return None
			
		return("Error: %s, %s and %s (at %f, %f, %f) " %
			(self.j1.getName(), self.j2.getName(), self.j3.getName(),
			self.j1pos, self.j2pos, self.j3pos) +
			"must be within tolerance %f before using %s (at %f)" %
			(self.tol, self.getName(), self.averageHeight ) )

	def setVelocities(self):
		"""
		Ensure all velocities are the same by setting all to the minimum of the 3
		"""
		minVel = min( [self.beamline.getValue(None, "Top", self.pvRoot + "Y1.VELO"), 
					   self.beamline.getValue(None, "Top", self.pvRoot + "Y2.VELO"), 
					   self.beamline.getValue(None, "Top", self.pvRoot + "Y3.VELO")] )
		
		self.beamline.setValue("Top", self.pvRoot + "Y1.VELO", minVel)
		self.beamline.setValue("Top", self.pvRoot + "Y2.VELO", minVel)
		self.beamline.setValue("Top", self.pvRoot + "Y3.VELO", minVel)


