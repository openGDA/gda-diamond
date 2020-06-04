from gda.device.scannable import ScannableMotionBase
from time import sleep

class cryostream_700(ScannableMotionBase):
	'''Device to control the Cryostream 700, 
             if you want to change the ramprate or read it back use:
             tset.setRampRate(value)
             tset.getRampRate()	
	'''
	def __init__(self, name, pvcryostream,  unitstring, formatstring,help=None):
		self.setName(name)
		self.setInputNames(['tetarget'])
		self.setExtraNames(['teset']);
		self.setOutputFormat([formatstring]*2)
		self.unitstring=unitstring
		self.setLevel(9)

		self.gasT=CAClient(pvcryostream+'TEMP')
		self.gasT.configure()

		self.setpoint=CAClient(pvcryostream+'SETPOINT')
		self.setpoint.configure()

		self.ramprate=CAClient(pvcryostream+'RAMPRATE')
		self.ramprate.configure()

		self.targettemp=CAClient(pvcryostream+'TARGETTEMP')
		self.targettemp.configure()

		self.writeramprate=CAClient(pvcryostream+'RRATE')
		self.writeramprate.configure()

		self.writeramptargettemp=CAClient(pvcryostream+'RTEMP')
		self.writeramptargettemp.configure()

		self.processramp=CAClient(pvcryostream+'RAMP.PROC')
		self.processramp.configure()

		self.phase=CAClient(pvcryostream+'PHASE')
		self.phase.configure()
		
		self.runmode = CAClient(pvcryostream+'RUNMODE')
		self.runmode.configure()

	def getPosition(self):
		return [float(self.targettemp.caget()),float(self.setpoint.caget())]


	def asynchronousMoveTo(self,new_position):
		sleep(.5)
		self.writeramptargettemp.caput(new_position)
		while int(self.phase.caget()) is 3:
			sleep(.5)
			self.processramp.caput(1)
			self.writeramptargettemp.caput(new_position)

	def isBusy(self):
		""" needs to be checked """
#		if self.mode == 'Ramp': 
		return 0
#		else:
#		return 1

	def setRampRate(self,ramprate):
		self.writeramptargettemp.caput(float(self.setpoint.caget()))
		self.writeramprate.caput(ramprate)
		self.processramp.caput(1)

	def getRampRate(self):
		return self.ramprate.caget()


tgas=DisplayEpicsPVClass('tgas','BL16I-EA-TEMPC-02:TEMP','K','%6f')
#del tset
tset=cryostream_700('tset','BL16I-EA-TEMPC-02:','K','%6f')
addmeta tset
addmeta tgas
