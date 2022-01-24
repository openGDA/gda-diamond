class PerpStageMotionh(PerpStageMotion):
	'''Device to move sample stage perpendicular to the beam when phi and mu are not zero'''
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

sperph=PerpStageMotionh("sperph", sx, sy, help="To move sample stage perpendicular to the beam.")
		
class ParaStageMotionh(PerpStageMotion):
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

sparah=ParaStageMotionh("sparah", sx, sy, help="To move sample stage parallel to the beam.")
