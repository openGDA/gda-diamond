#sperp and spara using rotation matrix method

class PerpStageMotionv(ScannableMotionBase):
	'''Device to move sample stage perpendicular or parallel to the beam when phi is not zero'''
	def __init__(self,name,_sx,_sy,help=None):
		self.setName(name)		
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help 
		self.setInputNames([name])
		self.setOutputFormat(['%4.4f'])
		self.Units=['mm']
		self.setLevel(5)

	def asynchronousMoveTo(self,value):
		# get new x position
		self.anticlock_x=sx.getPosition()*cos(phi.getPosition()/(180/pi))+sy.getPosition()*sin(phi.getPosition()/(180/pi))
		self.clock_x=self.anticlock_x*cos(phi.getPosition()/(180/pi))-value*sin(phi.getPosition()/(180/pi))
		self.clock_y=value*cos(phi.getPosition()/(180/pi))+self.anticlock_x*sin(phi.getPosition()/(180/pi))
		sy.asynchronousMoveTo(self.clock_y)
		sx.asynchronousMoveTo(self.clock_x)	
		
	def getPosition(self):
		return sy.getPosition()*cos(phi.getPosition()/(180/pi))-sx.getPosition()*sin(phi.getPosition()/(180/pi))
		
	def isBusy(self):
		return sx.isBusy() or sy.isBusy()

sperpv=PerpStageMotionv("sperpv", sx, sy, help="To move sample stage perpendicular to the beam.")

class ParaStageMotionv(PerpStageMotionv):
	'''Device to move sample stage parallel to the beam when phi is not zero'''
	def asynchronousMoveTo(self,value):

		self.anticlock_y=sy.getPosition()*cos(phi.getPosition()/(180/pi))-sx.getPosition()*sin(phi.getPosition()/(180/pi))
		self.clock_x=value*cos(phi.getPosition()/(180/pi))-self.anticlock_y*sin(phi.getPosition()/(180/pi))
		self.clock_y=self.anticlock_y*cos(phi.getPosition()/(180/pi))+value*sin(phi.getPosition()/(180/pi))	
		sy.asynchronousMoveTo(self.clock_y)
		sx.asynchronousMoveTo(self.clock_x)
			
	def getPosition(self):
		return sx.getPosition()*cos(phi.getPosition()/(180/pi))+sy.getPosition()*sin(phi.getPosition()/(180/pi))
		
sparav=ParaStageMotionv("sparav",sx,sy,help="To move sample stage parallel to the beam.")
