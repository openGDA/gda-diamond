from time import sleep
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient


#The Class for changing the ID Harmonic
#The PV is an Mbbinary elements that take the value "First" (1), "Third" (3) or "Fifth" (5)

class ID_HarmonicClass(ScannableMotionBase):
	"""
	The Class for changing the ID Harmonic
	The PV is an Mbbinary elements that take the value "First" (1), "Third" (3) or "Fifth" (5)
	"""
	
	HARMONIC_NUMBERS = [1, 3, 5];
	HARMONIC_STRINGS = ['First', 'Third', 'Fifth'];

	def __init__(self, name, pvHarmonic):
		self.setName(name);
		self.setInputNames([]);
		self.setExtraNames([name]);
#		self.Units=[strUnit];

		self.setLevel(7);
#		self.setOutputFormat(["%20.12f"]);
		self.chHarmonic = CAClient(pvHarmonic);
		self.configChannel(self.chHarmonic);
		
		self.harmonic=None;

	def __del__(self):
		self.cleanChannel(self.chHarmonic);
	
	def configChannel(self, channel):
		if not channel.isConfigured():
			channel.configure();

	def cleanChannel(self, channel):
		if channel.isConfigured():
			channel.clearup();

	def getHarmonic(self):
		self.chHarmonic.caget();
		self.harmonic = int( float( self.chHarmonic.caget() ) );
		return self.harmonic;

	def setHarmonic(self, newHarmonic):
		if newHarmonic in ID_HarmonicClass.HARMONIC_NUMBERS:
			harmonic_number = newHarmonic;
		elif newHarmonic in ID_HarmonicClass.HARMONIC_STRINGS:
			harmonic_number = ID_HarmonicClass.HARMONIC_NUMBERS[ID_HarmonicClass.HARMONIC_STRINGS.index(newHarmonic)];
		else:
			print "Wrong Harmonic, use either 1, 3, 5 or 'First', 'Third', 'Fifth' to change the ID harmonic";
			return;

		self.chHarmonic.caput(harmonic_number);


	#ScannableMotionBase Implementations
	def getPosition(self):
		return self.getHarmonic();
	
	def asynchronousMoveTo(self,newPos):
		self.setHarmonic(newPos);

	def isBusy(self):
		sleep(1);
		return False;


	def toString(self):
		ss = self.getName() + ": Current Harmonic is " + ID_HarmonicClass.HARMONIC_STRINGS[ID_HarmonicClass.HARMONIC_NUMBERS.index(self.getPosition())] + ". (Total three harmonic settings are: 'First', 'Third' and 'Fifth')" ;
		return ss;


#pvHarmonic = "BL06I-OP-IDD-01:HARMONIC";
#iddharmonic = ID_HarmonicClass("iddharmonic", pvHarmonic);

