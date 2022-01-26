from gda.epics import CAClient
from java import lang
from gda.device.scannable import ScannableMotionBase
from time import sleep

#The Class for creating a Monitor directly from EPICS PV
class MonitorEpicsPVClass(ScannableMotionBase):
	def __init__(self, name, strPV, strUnit, strFormat):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames([name]);
		self.Units=[strUnit]
		self.setOutputFormat([strFormat])
		self.setLevel(7)
		self.cli=CAClient(strPV)
		print " " + name,

	def atScanStart(self):
		if not self.cli.isConfigured():
			self.cli.configure()

	def getPosition(self):
		if self.cli.isConfigured():
			return float(self.cli.caget())
		else:
			self.cli.configure()
			return float(self.cli.caget())

	def isBusy(self):
		return 0
	
	def atScanEnd(self):
		if self.cli.isConfigured():
			self.cli.clearup()


print "Setting up extra PV monitors:",

#print 'Using iMBS2 for the Beam intensity on MBS2'
imbs2=MonitorEpicsPVClass('imbs2', 'BL07I-AL-SLITS-03:INTEN', 'uA', '%.10f');

#print 'Using iMBS1 for the Beam intensity on MBS1'
imbs1=MonitorEpicsPVClass('imbs1', 'BL07I-AL-SLITS-02:INTEN', 'uA', '%.10f');

#print 'Using vac5p for presure on Vacum gauge 5'
vac5p=MonitorEpicsPVClass('vac5p', 'BL07I-VA-GAUGE-05:P', 'mBar', '%.10f');

#print 'Using d4i and d4s for Diode reading from D4'
#d4i=MonitorEpicsPVClass('d4i', 'BL07I-DI-PHDGN-04:INLINE:I', 'V', '%.6f');
#d4s=MonitorEpicsPVClass('d4s', 'BL07I-DI-PHDGN-04:SCATTER:I', 'V', '%.6f');

#print 'Using dcm1xtal1roll_lvdt for 1st crystal roll LVDT'
#dcm1xtal1roll_lvdt=MonitorEpicsPVClass('dcm1xtal1roll_lvdt', 'BL07I-OP-DCM-01:ROLL1:LVDT', 'mrad', '%.6f');

#print 'Using dcm1xtal1pitch_lvdt for 2nd crystal pitch LVDT'
#dcm1xtal2pitch_lvdt=MonitorEpicsPVClass('dcm1xtal2pitch_lvdt', 'BL07I-OP-DCM-01:PITCH2:LVDT', 'mrad', '%.6f');

#print 'Using dcm1xtal2roll_lvdt for 2nd crystal roll LVDT'
#dcm1xtal2roll_lvdt=MonitorEpicsPVClass('dcm1xtal2roll_lvdt', 'BL07I-OP-DCM-01:ROLL2:LVDT', 'mrad', '%.6f');

#print 'Using rc for the ring current'
rc=MonitorEpicsPVClass('rc', 'SR-DI-DCCT-01:SIGNAL', 'mA', '%.4f');

#print "Using ps for the port shutter (1 = open)"
ps=MonitorEpicsPVClass('ps', 'FE07I-PS-SHTR-01:STA', '', '%.0f');

#print "Using eh1shutterstatus for the EH1 shutter status (1 = open, 3 = closed)"
eh1shutterstatus=MonitorEpicsPVClass('eh1shutterstatus', 'BL07I-PS-SHTR-01:STA', '', '%.0f');

#print "Using eh1interlockstatus for the EH1 interlock status (0 = fail, 1 = OK/ready, 2 = OK/open)"
eh1interlockstatus=MonitorEpicsPVClass('eh1interlockstatus', 'BL07I-PS-SHTR-01:ILKSTA', '', '%.0f');

print ""
