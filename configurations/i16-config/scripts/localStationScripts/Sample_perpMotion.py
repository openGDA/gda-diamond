#sperp and spara using rotation matrix method
#15/10/2012 implemented horizontal scattering mode (mu different from zero)
from gda.device.scannable import ScannableMotionBase

class PerpStageMotion(ScannableMotionBase):
	'''Device to move sample stage perpendicular or parallel to the beam when phi and mu are not zero'''
	def __init__(self,name,_sx,_sy,help=None):
		self.setName(name)		
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help 
		self.setInputNames([name])
		self.setOutputFormat(['%4.4f'])
		self.Units=['mm']
		self.setLevel(5)

	def asynchronousMoveTo(self,value):
		murad=mu()*(pi/180)
		phirad=phi()*(pi/180)
		self.anticlock_x=sx()*cos(phirad-murad)+sy()*sin(phirad-murad)
		self.clock_x=self.anticlock_x*cos(phirad-murad)-value*sin(phirad-murad)
		self.clock_y=value*cos(phirad-murad)+self.anticlock_x*sin(phirad-murad)
		sy.asynchronousMoveTo(self.clock_y)
		sx.asynchronousMoveTo(self.clock_x)	
		
	def getPosition(self):
		murad=mu()*(pi/180)
		phirad=phi()*(pi/180)
		return sy()*cos(phirad-murad)-sx()*sin(phirad-murad)
		
	def isBusy(self):
		return sx.isBusy() or sy.isBusy()

sperp=PerpStageMotion("sperp", sx, sy, help="To move sample stage perpendicular to the beam.")

		
class ParaStageMotion(PerpStageMotion):
	'''Device to move sample stage parallel to the beam when phi and mu are not zero'''
	def asynchronousMoveTo(self,value):
		murad=mu()*(pi/180)
		phirad=phi()*(pi/180)
		self.anticlock_y=sy()*cos(phirad-murad)-sx()*sin(phirad-murad)
		self.clock_x=value*cos(phirad-murad)-self.anticlock_y*sin(phirad-murad)
		self.clock_y=self.anticlock_y*cos(phirad-murad)+value*sin(phirad-murad)	
		sy.asynchronousMoveTo(self.clock_y)
		sx.asynchronousMoveTo(self.clock_x)
			
	def getPosition(self):
		murad=mu()*(pi/180)
		phirad=phi()*(pi/180)
		return sx()*cos(phirad-murad)+sy()*sin(phirad-murad)

spara=ParaStageMotion("spara", sx, sy, help="To move sample stage parallel to the beam.")
