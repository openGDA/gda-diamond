from gda.device.scannable import PseudoDevice
from time import sleep
from pd_epics import DisplayEpicsPVClass
from pd_epics import SingleEpicsPositionerSetAndGetOnlyClass as sep

class OI503s(PseudoDevice):
	'''Device to control the pulsed tube temperature controlles, 
             if you want to change the ramprate or read it back use:	
	'''
	def __init__(self, name, pv,  unitstring, formatstring,help=None):
		self.setName(name)
		self.setInputNames(['tset'])
		self.setExtraNames(['error']);
		self.setOutputFormat([formatstring]*2)
		self.unitstring=unitstring
		self.setLevel(9)
		self.targetT=CAClient(pv+'TTEMP:SET')
		self.targetT.configure()
		self.readtarget=tsetdisplay
		self.error=tseterror

	def getPosition(self):
		return [float(self.readtarget()),float(self.error())]

	def asynchronousMoveTo(self,new_position):
		self.targetT.caput(new_position)
		sleep(1)

	def isBusy(self):
		sleep(.5) 
		return 0



lab84=False

#del gasflow,tset,tsam,tvti,pnv,tsetdisplay,tseterror
if lab84==True:
	gasflow=sep('gasflow',pvinstring='LA84R-EA-TEMPC-01:GFLOW:SET', pvoutstring='LA84R-EA-TEMPC-01:GFLOW', unitstring='mbar', formatstring='%6f',help=None,sleeptime=0)
	tsam=DisplayEpicsPVClass('tsam','LA84R-EA-TEMPC-01:STEMP','K','%6f')
	tvti=DisplayEpicsPVClass('tvti','LA84R-EA-TEMPC-01:STEMP2','K','%6f')
	pnv=DisplayEpicsPVClass('needlevalvepressure','LA84R-EA-TEMPC-01:STEMP3','mBar','%6f')
	tsetdisplay=DisplayEpicsPVClass('tsetdisplay','LA84R-EA-TEMPC-01:TTEMP','K','%6f')
	tseterror=DisplayEpicsPVClass('tseterror','LA84R-EA-TEMPC-01:TEMP:ERR','K','%6f')
	tset=OI503s('tset','LA84R-EA-TEMPC-01:','K','%6f')
#beamline
else:
	gasflow=sep('gasflow',pvinstring='BL16I-EA-TEMPC-01:GFLOW:SET', pvoutstring='BL16I-EA-TEMPC-01:GFLOW', unitstring='mbar', formatstring='%6f',help=None,sleeptime=0)
	tsam=DisplayEpicsPVClass('tsam','BL16I-EA-TEMPC-01:STEMP','K','%6f')
	tvti=DisplayEpicsPVClass('tvti','BL16I-EA-TEMPC-01:STEMP2','K','%6f')
	pnv=DisplayEpicsPVClass('needlevalvepressure','BL16I-EA-TEMPC-01:STEMP3','mBar','%6f')
	tsetdisplay=DisplayEpicsPVClass('tsetdisplay','BL16I-EA-TEMPC-01:TTEMP','K','%6f')
	tseterror=DisplayEpicsPVClass('tseterror','BL16I-EA-TEMPC-01:TEMP:ERR','K','%6f')
	tset=OI503s('tset','BL16I-EA-TEMPC-01:','K','%6f')


