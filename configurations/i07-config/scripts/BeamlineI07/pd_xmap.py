from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient 
from time import sleep

class DisplayEpicsPVClass(ScannableMotionBase):
	'''
	Create PD to display single EPICS PV
	dev=DisplayEpicsPVClass(name, pvstring, unitstring, formatstring)
	'''
	def __init__(self, name, pvstring, unitstring, formatstring):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames([name]);
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(8)
		self.cli=CAClient(pvstring)
		print self.name + " connecting to: " + pvstring
		self.cli.configure()

	def getPosition(self):
#		self.cli.configure()
		return float(self.cli.caget())
#		self.cli.clearup()

	def isBusy(self):
		return 0


class xmapcounter(ScannableMotionBase):
	def __init__(self, name, pv='ME13C-EA-DET-01:',formatstring='%6f'):
		self.setLevel(9)
		self.setOutputFormat([formatstring]*4)
		self.setName(name)	
		self.setInputNames([name])
		self.pvt=CAClient(pv+'EraseStart')
		self.rt=CAClient(pv+'PresetReal')
		self.rt.configure()
		self.pvt.configure()
		self.checkbusy=CAClient(pv+'ElapsedReal')
		self.checkbusy.configure()	
		self.setExtraNames(['xmroi1','xmroi2','xmroi3'])
		self.new_position=1


	def getPosition(self):
		w(.2)
		return [float(self.checkbusy.caget()),float(xmroi1.getPosition()),float(xmroi2.getPosition()),float(xmroi3.getPosition())]

	def asynchronousMoveTo(self,new_position):
		self.new_position=new_position
		self.rt.caput(self.new_position)
		self.pvt.caput(1)
		w(new_position+.5)

#
	def isBusy(self):
		while self.checkbusy.caget()<self.new_position:
			w(0.1)
			return 1
		else:
			return 0


xmroi1=DisplayEpicsPVClass('xmroi1','ME13C-EA-DET-01:MCA1.R0','counts','%6f')
xmroi2=DisplayEpicsPVClass('xmroi2','ME13C-EA-DET-01:MCA1.R1','counts','%6f')
xmroi3=DisplayEpicsPVClass('xmroi2','ME13C-EA-DET-01:MCA1.R2','counts','%6f')

xmapc=xmapcounter('xmapc')
