'''
Created on 18 Sep 2024

@author: eir17846
'''
from gda.device.scannable import ScannableMotionBase
from gda.factory import Finder
import logging
logger = logging.getLogger('__main__')

pgm_mlg_position = "1200 l/mm ML"
cff_fitting_coeff = (1.06632, 0.000182282, 0.0000000890301, -0.00000000000611146)

class pgm_multilayer_grating(ScannableMotionBase):
	"""
pgm_energy_mlg - scannable that calculates and moves CFF before moving PGM energy.

- Double checks that PGM grating is set to multilayer grating
- Double checks that requested energy is more than 1000 eV

! pgm_energy_mlg.calculate_cff(energy) to check new CFF for given energy
! pgm_energy_mlg.getCoefficients() to check fitting coefficients
	"""

	def __init__(self, name, pgm_energy, pgm_cff, pgm_grating, unitstring, formatstring):
		self._busy = False
		self.setName(name);
		self.setInputNames([name])
		self.pgm_energy = pgm_energy
		self.pgm_cff = pgm_cff
		self.pgm_grating = pgm_grating
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(5)
		self.logger = logger.getChild(self.__class__.__name__)

	def calculate_cff(self, new_energy):
		new_cff_value = 0.0
		for i in range(len(cff_fitting_coeff)):
			new_cff_value += cff_fitting_coeff[i] * new_energy**(i)
		return new_cff_value

	def rawGetPosition(self):
		return pgm_energy.getPosition()

	def rawAsynchronousMoveTo(self, energy):
		new_energy = float(energy)
		# make sure PGM multilayer grating in place
		try:
			pgm_position = self.pgm_grating.getPosition()
			if (pgm_mlg_position not in pgm_position):
				print "PGM grating is not <<"+pgm_mlg_position+">>!  Please change to the correct grating"
				return None
		except Exception as e:
			print "Error getting PGM grating position! "+e

		# requested energy must be more than 1000eV
		if (new_energy<1000):
			print ("Requested energy is less than 1000 eV - not applicable to multilayer grating!")
			return None

		#Move cff and then pgm
		try:
			# move CFF first and wait until it is done - blocking!
			new_cff = self.calculate_cff(new_energy)
			print "Moving CFF to a new value: "+str(new_cff)
			self.pgm_cff.moveTo(new_cff)
			print "Moving CFF completed"
			# move PGM_ENERGY asynchronous
			print "Moving pgm energy to a new value: "+str(new_energy)
			self.pgm_energy.asynchronousMoveTo(new_energy)
		except Exception as e:
			print "Error moving pgm_energy and/or pgm_cff to a new position! " + e

	def isBusy(self):
		self._busy = False
		try:
			self._busy = (pgm_cff.isBusy() or pgm_energy.isBusy())
		except Exception as e:
			print "Error getting busy status from pgm_energy and/or pgm_cff! " + e
		return self._busy

	def stop(self):
		try:
			self.pgm_cff.stop()
			self.pgm_energy.stop()
		except Exception as e:
			print "Failed to stop pgm_cff and/or pgm_energy motor! "+e

	def getCoefficients(self):
		for i in range(len(cff_fitting_coeff)):
			print "A"+str(i)+": "+str(cff_fitting_coeff[i])+" "

	def toString(self):
			return self.name + ": " + str(pgm_energy.getPosition()) + "   " + "pgm_cff: " + str(pgm_cff.getPosition())

pgm_energy = Finder.find("pgm_energy")
pgm_cff = Finder.find("pgm_cff")
pgm_grating = Finder.find("pgm_grating")

pgm_energy_mlg = pgm_multilayer_grating("pgm_energy_mlg", pgm_energy, pgm_cff, pgm_grating, "", "%d")
