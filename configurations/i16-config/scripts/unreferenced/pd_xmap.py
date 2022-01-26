from gda.device.scannable import ScannableMotionBase
from time import sleep
from pd_epics import DisplayEpicsPVClass
from pd_epics import SingleEpicsPositionerSetAndGetOnlyClass as sep


xmroi1=DisplayEpicsPVClass('xmroi1','BL16I-EA-XMAP-01:MCA1.R0','counts','%6f')
xmroi2=DisplayEpicsPVClass('xmroi2','BL16I-EA-XMAP-01:MCA1.R1','counts','%6f')
xmroi3=DisplayEpicsPVClass('xmroi2','BL16I-EA-XMAP-01:MCA1.R2','counts','%6f')

#energy.maxEnergyChangeBeforeMovingMirrors=0.00

class xmapcounter(ScannableMotionBase):
	def __init__(self, name, pv='BL16I-EA-XMAP-01:',formatstring='%6f'):
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



vortex=xmapc=xmapcounter('xmapc')



#tthp.vortex=-11.44 
