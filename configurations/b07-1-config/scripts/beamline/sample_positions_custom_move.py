from gdascripts.scannable.sample_positions import SamplePositions
from gda.device import DeviceException #@UnresolvedImport

class B07C_Sample_Positions(SamplePositions):
	__doc__ = """

	This class overrides parent SamplePositions class.
	It first moves *_xp sample position to a safe intermediate position,
	then moves other motors and finally moves *_xp motor.
	""" + SamplePositions.__doc__

	xpsafety_margin=0.2
	xp_names_list=["sm_xp", "sm2_xp"]

	#@Override
	def asynchronousMoveTo(self, key):

		key = str(key)
		self.checkConfiguration()

		if len(self.getSavedPositions(remove_excluded=True).keys()) == 0:
			raise DeviceException("List of saved positions for {} is empty, please populate it first".format(self.name))

		if key not in self.getSavedPositions(remove_excluded=True):
			raise DeviceException("Requested position key {} is not in a saved list of keys: {}".format(key, self.getSavedPositions(remove_excluded=True).keys()))

		saved_positions = self.getSavedPositions(remove_excluded=True)[key]

		# First move *_xp scannable to a safe position


		xp_scannable = None
		for scannable in self.getScannables(remove_excluded=True):
			if ((scannable.getName() in self.xp_names_list) and (scannable.getName() in saved_positions)):
				xp_scannable = scannable

		if xp_scannable != None:
			new_scannable_pos = saved_positions[xp_scannable.getName()]
			if new_scannable_pos is None:
				raise DeviceException("New position cannot be None for key: {}, scannable: {}".format(new_scannable_pos, scannable.getName()))
			intermediate_position = min(new_scannable_pos, scannable.getPosition())-self.xpsafety_margin
			print("Moving {} to an intermediate position {}".format(scannable.getName(), intermediate_position))
			scannable.moveTo(intermediate_position) # must be blocking as needs to finish prior to other motors moving

		# Move all other scannables
		for scannable in self.getScannables(remove_excluded=True):
			if ((scannable.getName() not in self.xp_names_list) and (scannable.getName() in saved_positions)):
				new_scannable_pos = saved_positions[scannable.getName()]
				if new_scannable_pos is None:
					raise DeviceException("New position cannot be None for key: {}, scannable: {}".format(new_scannable_pos, scannable.getName()))
				print("Moving {} to a new position {}".format(scannable.getName(), new_scannable_pos))
				scannable.moveTo(new_scannable_pos)

		# Finally move *_xp scannable to a desired position
		if xp_scannable != None:
			new_scannable_pos = saved_positions[xp_scannable.getName()]
			print("Moving {} to a final position {}".format(xp_scannable.getName(), new_scannable_pos))
			xp_scannable.asynchronousMoveTo(new_scannable_pos) # must be blocking as needs to finish prior to other motors moving

		self.key = key
