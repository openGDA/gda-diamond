# deleting PD
# display updating position

## define method to return ust input positions (function call with no args?)
##     dev1==dev2() moves dev1 to dev2 position etc
## chk function to check size of input and convert number to list/vector
#####how to handle scalar?? want output to be scalar??
# do we need all the function calls?

#how to combine function calls...


from java import lang

class PDBaseClass:
# input values are numbers or lists/vectors
# output positions are lists/vectors

 	def __init__(self):
		print 'Creating new ScannableMotionBase'
		self.ExtraNames=[]

	def asynchronousMoveTo(self,new_position):
		self.currentposition = new_position

	def MoveTo(self,new_position):
		self.asynchronousMoveTo(new_position)
		while self.isBusy():
			lang.Thread.currentThread().sleep(100)
		print self

	def asynchronousMoveBy(self,increment):	#accept number or list/vector
		currentpos=self.getPosition()
		# try as a list/vector
		try:
			newpos=[]
			for i in range(len(increment)):
				newpos=newpos+[currentpos[i]+increment[i]]
			self.currentposition = newpos
		except:
		# treat input as a number
			newpos=[currentpos+increment]
		self.asynchronousMoveTo(newpos)

	def MoveBy(self,increment):
		self.asynchronousMoveBy(increment)
		while self.isBusy():
			lang.Thread.currentThread().sleep(100)
		print self	
			
	def atScanStart(self):
		print "doing atScanStart()!"

	def atScanEnd(self):
		print "doing atScanEnd()!"

	def setInputNames(self, namelist):
		self.InputNames=namelist

	def getInputNames(self):
		return self.InputNames

	def setExtraNames(self, namelist):
		self.ExtraNames=namelist

	def getExtraNames(self, namelist):
		return self.ExtraNames

	def setLevel(self, level):
		self.level=level

	def getLevel(self):
		return self.level

	def getPosition(self):
		## retrun position as a vector/list
		extras=[99]
		return self.currentposition+extras

	def setUnits(self, units):
		self.units=units

	def getUnits(self, units):
		return self.units

	def isBusy(self):
		return 0
	
	def __call__(self,new_position):
		## call method does moveto
		self.MoveTo(new_position)

	def __repr__(self):
		values=self.getPosition()
		names=self.InputNames+self.ExtraNames
		s='' 
		for i in range(len(self.Formats)):
			format= '%20s  :  '+self.Formats[i]+'  %s \n'  
			s=s+  format % (names[i], values[i], self.Units[i])
		return s

	def __getitem__(self,key):
		return self.getPosition()[key]

	def __call__(self, position):
		self.MoveTo(position)
	
	def __gt__(self, moveby):
		###change to moveby
		self.MoveBy(moveby)

	def __lt__(self, movebyminus):
		###change to moveby
		moveby=[]
		for i in range(len(movebyminus)):
			moveby=moveby+[-movebyminus[i]]
		self.MoveBy(moveby)

	def __eq__(self, movebyplus):
		###change to moveby
		self.MoveTo(movebyplus)

	def __add__(self, other):
		#check that other is a PD object
		newpd=PDBaseClass()
		newpd.InputNames=self.InputNames+other.InputNames
		newpd.ExtraNames=self.ExtraNames+other.ExtraNames
		newpd.Units=self.Units+other.Units
		newpd.Formats=self.Formats+other.Formats
		newpd.Level=max(self.Level, other.Level)
		#newpd.getPosition()=lambda: 99
		#setattr(newpd,'getPosition()',lambda: ('[4,4,4]'))###########doesn't work...
		#def newpd.stop():
		#	print 'stopping 1'; self.stop
		#	print 'stopping 2'; other.stop
			
		return newpd

	def stop(self):
		print "Abort motion"


###create a PD#########
class pd1(PDBaseClass):
	def __init__(self):
		self.currentposition=[3,3]
		self.InputNames=['xpos','ypos']
		self.ExtraNames=['extra']
		self.Units=['mm','mm','deg']
		self.Formats=['%10.3f','%10.3f','%10.5f']
		self.Level=3

	def asynchronousMoveTo(self,new_position):
		self.currentposition = new_position

	def getPosition(self):
		extras=[99]
		return self.currentposition+extras

	def isBusy(self):
		return 0
#instantaite first device
dev1=pd1()
#instatiate and modify decond device
dev2=pd1()
dev2.setInputNames(['up','down'])
dev2.setExtraNames(['flying_around'])

#using the devices...

dev1([1,1])
a=dev1[0]
print a
dev1==[2,2]
dev1>[0.1 0]



#dir(dev1) displays attributes but not methods
