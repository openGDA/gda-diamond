from gda.device.scannable import ScannableMotionBase
import random


# The Class for changing the grating on I06 PGM
class DummyListScannable(ScannableMotionBase):

	def __init__(self, name, list_values=None, unit=None, format_string='%s'):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
		self.unit = unit;
		self.values = list_values
		self.setLevel(7);
		self.setOutputFormat([format_string]);
		self.value = None;

	# Scannable Implementations
	def getPosition(self):
		if self.value is None:
			self.value = random.choice(self.values)
		return self.value
	
	def asynchronousMoveTo(self, new_pos):
		if new_pos in self.values:
			self.value = new_pos;
		else:
			raise ValueError("Value %d is not in the supported list %r" % (new_pos, self.values))

	def isBusy(self):
		# sleep(60);
		return False

	def toFormattedString(self):
		if self.unit is not None:
			ss = self.getName() + " :  " + str(self.getPosition()) + " " + self.unit;
		else:
			ss = self.getName() + " :  " + str(self.getPosition())
		return ss;



