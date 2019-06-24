from gda.device.scannable import ScannableBase
from gda.epics import CAClient
from gda.jython.commands.GeneralCommands import alias
from Diamond.PseudoDevices.EpicsDevices import EpicsMonitorClass
from peem.usePEEM import uvimaging, uvpreview
from peem.usePEEM_tcpip import uv

print "-"*100
print "Enable KB Mirror objects: m4bend1g,m4bend2g,m5bend1g,m5bend2g,kbpiezoh,kbpiezov,kbraster,vertFactor,horizFactor,kbpreview,kbimaging,kboff,kbfov"
m4bend1g=EpicsMonitorClass('m4bend1gauge', 'BL06I-OP-KBM-01:HFM:USG:POLLVALUE', 'N', '%.3f');
m4bend2g=EpicsMonitorClass('m4bend2gauge', 'BL06I-OP-KBM-01:HFM:DSG:POLLVALUE', 'N', '%.3f');
m5bend1g=EpicsMonitorClass('m5bend1gauge', 'BL06I-OP-KBM-01:VFM:USG:POLLVALUE', 'N', '%.3f');
m5bend2g=EpicsMonitorClass('m5bend2gauge', 'BL06I-OP-KBM-01:VFM:DSG:POLLVALUE', 'N', '%.3f');

class KBMirrorPiezoDeviceClass(object):

	def __init__(self, rootPV='BL06I-OP-KBM-01:VFM:FPITCH', freqPV='BL06I-OP-KBM-01:VFM:FPITCH:FREQ', freqDivPV='BL06I-OP-KBM-01:HFM:FPITCH:FREQDIVISOR'):
		
		self.freq=None;
		self.freqdiv=None;
		self.amp=None;
		self.offset=None;

		self.chFreq=CAClient(freqPV);
		self.chFreq.configure();
		
		self.chFreqDiv=CAClient(freqDivPV);
		self.chFreqDiv.configure();

		self.chAmp=CAClient(rootPV+':AMPL');
		self.chAmp.configure();

		self.chOffset=CAClient(rootPV+':OFF');
		self.chOffset.configure();

		self.fovFactor=100.0;
		
	def setFovFactor(self, newFovFactor):
		self.fovFactor=newFovFactor*1.0;
		
	def __del__(self):
		self.cleanChannel(self.chFreq);
		self.cleanChannel(self.chFreqDiv);
		self.cleanChannel(self.chAmp);
		self.cleanChannel(self.chOffset);

	def configChannel(self, channel):
		if not channel.isConfigured():
			channel.configure();

	def cleanChannel(self, channel):
		if channel.isConfigured():
			channel.clearup();

	def setFreq(self, freq):
		self.chFreq.caput(freq)

	def getFreq(self):
		self.freq=float( str(self.chFreq.caget()))
		return self.freq; 
	
	def setFreqDiv(self, div):
		self.chFreqDiv.caput(div);
			
	def getFreqDiv(self):
		self.freqdiv= float( str(self.chFreqDiv.caget()))
		return self.freqdiv;
		
	def setAmplitude(self, ampl):
		self.chAmp.caput(ampl)

	def getAmplitude(self):
		self.amp=float( str(self.chAmp.caget()))
		return self.amp

	def setOffset(self, offset):
		self.chOffset.caput(offset);

	def getOffset(self):
		self.offset=float( str(self.chOffset.caget()))
		return self.offset;

	def update(self):
		self.getFreq();
		self.getFreqDiv();
		self.getAmplitude();
		self.getOffset();
		print "Frequency = %f \nFrequencyDivisor = %f \nAmplitude = %f \nOffset = %f" %(self.freq, self.freqdiv, self.amp, self.offset);

class KBMirrorRasteringClass(ScannableBase):

	MODE=['vertical', 'horizontal']

	def __init__(self, name, hfm, vfm):
		self.setName(name);
		self.setInputNames([name])
		self.setExtraNames([])
		
		self.hfm=hfm;
		self.vfm=vfm;
		
		self.mirror=self.vfm;
		
		self.fov=10;
		
		self.mode='vertical';

	def setMode(self, newMode):
		nm=(str(newMode)).lower();
		if nm in KBMirrorRasteringClass.MODE:
			self.mode = nm;
		else:
			print "Please chose 'Vertical' or 'Horizontal' for VFM or HFM rastering";
			raise ValueError('Raster mode setting Error!')
		
		if self.mode == 'vertical':
			self.mirror=self.vfm;
		elif self.mode == 'horizontal':
			self.mirror=self.hfm;
		else:
			print "Please chose 'Vertical' or 'Horizontal' for VFM or HFM rastering";

		self.setFOV(self.fov);
		
	def setFreq(self, freq):
		if freq > 10 or freq <0:
			print"Rastering Frequence should be between 0 and 10 Hz"
			return;
		else:
			self.vfm.setFreq(freq)

	def getFreq(self):
		return self.vfm.getFreq();
	
	def setFreqDiv(self, div):
		self.hfm.setFreqDiv(div);
			
	def getFreqDiv(self):
		return self.hfm.getFreqDiv();
	
	def setAmplitude(self, newAmp):
		if self.mode == 'vertical':
			self.hfm.setAmplitude(0);
			self.vfm.setAmplitude(newAmp);
		elif self.mode == 'horizontal':
			self.vfm.setAmplitude(0);
			self.hfm.setAmplitude(newAmp);
		else:
			print "Please chose 'Vertical' or 'Horizontal' for VFM or HFM rastering";
		return;

	def setFovFactor(self, newFovFactor):
		self.mirror.setFovFactor(newFovFactor);

	def getFovFactor(self):
		return self.mirror.fovFactor;
		
	def update(self):
		freq=self.getFreq();
		freqdiv=self.getFreqDiv();

		amp=self.mirror.getAmplitude();
		offset=self.mirror.getOffset();
		
		print "Mode: " + self.mode;
		print "Frequency = %f \nFrequencyDivisor = %f" %(freq, freqdiv);
		print "\nAmplitude = %f \nOffset = %f" %(amp, offset);
		print "\nFOV = %f \nFOV factor = %f" %(self.fov, self.getFovFactor());
	
	def off(self):
		self.vfm.setAmplitude(0)
		self.hfm.setAmplitude(0)
	
	def setFOV(self, newFOV):
#		allowedFOV = [80, 50, 40, 30, 20, 15, 10, 6]
		allowedFOV = range(0, 101, 1)
		if not (newFOV in allowedFOV):
			print "Wrong FOV. Possible value: 80, 50, 40, 30, 20, 15, 10, 6";
			return;
		self.fov=newFOV;
		amplitude = newFOV/self.getFovFactor()
		self.setAmplitude(amplitude);
		
	#Scannable Implementation
	def getPosition(self):
		return self.mode;

	def asynchronousMoveTo(self,newMode):
		self.setMode(newMode);

	def isBusy(self):
		return False;

kbpiezoh = KBMirrorPiezoDeviceClass('BL06I-OP-KBM-01:HFM:FPITCH')
kbpiezov = KBMirrorPiezoDeviceClass('BL06I-OP-KBM-01:VFM:FPITCH')

kbraster = KBMirrorRasteringClass('kbraster', kbpiezoh, kbpiezov);
kbraster.setFreq(10);
kbraster.setFreqDiv(1);

vertFactor = 100
horizFactor = 100
kbraster.setMode('vertical')
kbraster.setFovFactor(vertFactor)
kbraster.setMode('horizontal')
kbraster.setFovFactor(horizFactor)

def kbimaging(collectionTime=1.0):
	kbraster.setFreq( 1.0/collectionTime )
	kbraster.setFreqDiv( 1.0 )
	uvimaging()
	uv.setCollectionTime(collectionTime)

def kbpreview():
	kbraster.setFreq( 10 )
	kbraster.setFreqDiv( 1.0 )
	uvpreview()
		

def kboff():
	kbraster.off();

def kbfov(newFOV):
	kbraster.setFOV(newFOV);

alias("kbpreview")
alias("kbimaging")
alias("kbfov")
alias("kboff")

