from gda.device.scannable import ScannableMotionBase
from gda.jython.commands.ScannableCommands import pos
from mathd import *
from operator import itemgetter, mod
import beamline_info as BLi


class PolarizationAnalyser(ScannableMotionBase):
	""" Class to set-up the polarization analyser.
          The methods available are:
          setDetector
          getDetector
          showCrystals	
          setCrystal
          getCrystal
          getPosition
          asynchronousMoveTo
          calcPos
          isBusy
          calibrate
          out 
          _in
          reset
          If you need help on the available methods type:
          help pol.method (e.g. pol.calibrate) 
	"""

	def __init__(self,name,rotmotor,thmotor,tthmotor,zpmotor,offset1,offset2,offset3,offset4,offset5,offset6,offset7):
		self.setName(name)
		self.setInputNames(['rotp'])
		self.setExtraNames(['thpcor','tthp'])
		self.setOutputFormat(["%4.4f","%4.4f","%4.4f"])

		self.pol = rotmotor
		self.thp=thmotor
		self.tthp=tthmotor
		self.zp=zpmotor

		self.offsets=None
		self.key = self.thp.getName()
		self.analyser = {'PG001':6.711,'Au111':2.3545,'LiF110':2.8638,'LiF001':4.05,'Cu111':2.0871,'Cu110':2.5561,'Mo100':3.147,'MgO':2.4347,'Si111':3.13553,'Ge111':3.2663,'InSb111':3.74,'Ni001':3.524,'Al110':2.866}
		self.analyser['Cu110']=2.5425 #measured 14/10/2007
		# The index is 0 if even, 1 if odd, 2 if both
		self.analyserorder = {'PG001':0,'Au111':2,'LiF110':0,'LiF001':0,'Cu111':2,'Cu110':2,'Mo100':0,'MgO':0,'Si111':1,'Ge111':1,'InSb111':2,'Ni001':0,'Al110':0}
		
# making crystal persistent
		self.offset6=offset6
		self.offset7=offset7
		try:
			cryst=self.analyser.keys()[int(self.offset6())]
			self.setCrystal(cryst,self.offset7())
		except:
			print "Warning: not able to retrieve the analyser crystal"
#		self.setCrystal('pg001',6)
		self.offset1=offset1 
		self.offset2=offset2 
		self.offset3=offset3  
		self.offset4=offset4
		self.offset5=offset5 
		self.oldpos=None


	def setDetector(self,countername=None):
		"""Sets roughly the offset in tthp corresponding to the detector you
		wish to use
		Available detectors are: vortex and apd 
	 	e.g.   pol.setDetector('Vortex')
		"""
		if countername == None:
			self.setDetector.__doc__
		if countername == 'Vortex':
			#self.offset5(-18.5)
			self.offset5(-17.5) #Feb2011
		elif countername == 'apd':
			self.offset5(-2.5)
		else:
			print "Failed to establish a detector offset"
			return
		print  countername+" selected"
		print "new det. offset=",self.offset5()
		return

	def getDetector(self):
		"""returns the name of the selected detector
	 	
		"""
		#if self.offset5() == -18.5:
		if self.offset5() == -17.5:
			self.countername='Vortex'
		if self.offset5() == -2.5:
			self.countername='apd'
		else:
			return "No valid detector selected"
		return self.countername
		
 	

	def showCrystals(self,tthval=90., lowlimit=80,highlimit=100,wl=None):	
		"""showCrystals(self,tthval=90., lowlimit=80,highlimit=100,wl=None)
	 	   Without argument returns the list of crystals and reflections closest to 
		   90 deg. 2theta angles (>80 and <100 deg) at the current wavelength

		"""
		crystallist=sorted(self.analyser.items(),key=itemgetter(1))
		if wl==None:
			wl = BLi.getWavelength()
		crystallistb=[];
		crystal_list_new=[];
		for indice in range(0,len(crystallist)):
			try:
				thbragg = 180/pi*asin(wl/(2*crystallist[indice][1]))
				crystallistb.append([crystallist[indice][0], crystallist[indice][1], 2*thbragg])
			except:
				pass
		print crystallistb
		for indice in range(0,len(crystallistb)):
			try:
				ordine1=int(round(tthval/crystallistb[indice][2]))
				for ordine in [ordine1-1,ordine1,ordine1+1]:
					if ordine>0:
						thbragg = 180/pi*asin(ordine*wl/(2*crystallistb[indice][1]))
#				print 2*thbragg, ordine, [crystallistb[indice][0] crystallistb[indice][1]/ordine 2*thbragg ordine]
						crystal_list_new.append([crystallistb[indice][0], round(crystallistb[indice][1]/ordine,4), round(2*thbragg,4), ordine, abs(tthval-2*thbragg)])
			except:
				pass
		crystal_list_new=sorted(crystal_list_new,key=itemgetter(4))
		print crystal_list_new
		print "Crystal, d-spacing, 2theta, refl. order"
		for indice in range(len(crystal_list_new)):
			if crystal_list_new[indice][2]>lowlimit and crystal_list_new[indice][2]<highlimit and mod(crystal_list_new[indice][-2],2)==self.analyserorder[crystal_list_new[indice][0]]:
				print crystal_list_new[indice][0:-1]
		return #crystal_list_new

	def setCrystal(self,crystal,nn):
		"""Sets the crystal and the order of the reflection.
	e.g.   pol.setCrystal('PG001',6)
		""" 
		self.crystal=crystal
		#self.nn=nn
		self.offset7(nn)
		self.offset6(self.analyser.keys().index(self.crystal))
		self.dspace = self.analyser[crystal]/nn

	def getCrystal(self):
		"""Returns the current crystal its d-space and the order of the reflection used 
		"""
		return self.crystal,self.dspace,self.offset7()

	def getPosition(self):
		"""Returns thp tthp and stokes including the offsets"""
		xxx1=self.pol()
		xxx2 = self.thp()
		xxx3 = self.tthp()-self.offset5()-self.offset4()
		if xxx3 > 68. and xxx3 < 72:
			print "WARNING:: Detector in the chamber pillar!!!"  
		if xxx3 < -63. and xxx3 > -67:
			print "WARNING:: Detector in the chamber pillar!!!"  
		self.currentOffset = cosd(self.pol())**2*self.offset2()+sind(self.pol())**2*self.offset3()		
		xxx2=xxx2-self.currentOffset-self.offset1()
		return [xxx1, xxx2, xxx3]

	def asynchronousMoveTo(self,newpol):
		"""Takes one real argument (the stokes value), moves the polarization analyser thp tthp and stokes """
		newoff=cosd(newpol)**2*self.offset2()+sind(newpol)**2*self.offset3()

#		newoff = cosd(newpol)*self.offset2()+sind(newpol)*self.offset3()
 
		wl = BLi.getWavelength()

		self.thbragg = 180/pi*asin(wl/(2*self.dspace))
		newthp=self.thbragg+self.offset1()+newoff
		newtthp=2*self.thbragg+self.offset5()+self.offset4()
		self.pol.asynchronousMoveTo(newpol)
		if newtthp > 103.0:
			print "Possible collision with Pilatus:: stop"
			print "tthp not moved"
		else:
			self.tthp.asynchronousMoveTo(newtthp)
		self.thp.asynchronousMoveTo(newthp)
		#print 2*self.thbragg+self.offset4()

	def calcPos(self,newpol):
		"""Takes one real argument, calculates for the given stokes value the polarization analyser thp and tthp """
		newoff = cosd(newpol)**2*self.offset2()+sind(newpol)**2*self.offset3()
		wl = BLi.getWavelength()
		self.thbragg = 180/pi*asin(wl/(2*self.dspace))
		newthp=self.thbragg+self.offset1()+newoff
		newtthp=2*self.thbragg+self.offset4()+self.offset5()
		print "stoke", newpol,"thp",newthp,"tthp",newtthp

	def isBusy(self):
		""" Returns Busy if either stokes or thp or tthp are busy"""
		if self.pol.isBusy() == 1 or self.thp.isBusy() == 1 or self.tthp.isBusy() == 1:
			return 1
		else:
			return 0

	def calibrate(self):
		""" Calibrate the PA at stoke=0 and 90 degrees
	use: when stoke = 0 and the reflection on the analiser centered call pol.calibrate() 
	use: when stoke = 90 and the reflection on the analiser centered call pol.calibrate()
	The set-up of the analyser is complete. 
		"""
		wl = BLi.getWavelength()
		if abs(self.pol()) <= 1:
			xxx=180/pi*asin( wl/(2*self.dspace)) - (self.thp()-self.offset1())
			self.offset2(-xxx)
			yyy=self.tthp()-2*180/pi*asin(wl/(2*self.dspace))-self.offset5()
			self.offset4(yyy)
		elif abs(self.pol()-90.) <=1:
			xxx=180/pi*asin( wl/(2*self.dspace)) - (self.thp()-self.offset1())
			self.offset3(-xxx)
		else:
			print "Can't calibrate at stoke=",self.pol()
		return [self.offset1(),self.offset2(), self.offset3(),self.offset4(),self.offset5()]

	def out(self,newtthp=None):
		self.oldpos=[self.pol(), self.thp(), self.tthp(), self.zp()]
		if newtthp==None:
			pos([self.pol, 0, self.thp, self.offset1(), self.zp, -10])
			#pos self.pol 0 self.thp self.offset1() self.zp -10
		else:
			#pos self.pol 0 self.thp self.offset1() self.tthp newtthp self.zp -10
			pos([self.pol, 0, self.thp, self.offset1(), self.tthp, newtthp, self.zp, -10])

	def reset(self):
		""" Resets all the offsets to zero before changing crystal """
		#pos self.offset1 0 self.offset2 0 self.offset3 0 self.offset4 0 self.offset5 0
		pos([self.offset1, 0, self.offset2, 0, self.offset3, 0, self.offset4, 0, self.offset5, 0]) 


	def _in(self): # in is a keyword in Jython2.5
		if self.oldpos==None:
			print 'no position is defined'
		else:
			pos([self.pol, self.oldpos[0], self.thp, self.oldpos[1], self.tthp, self.oldpos[2], self.zp, self.oldpos[3]])
			#pos self.pol self.oldpos[0] self.thp self.oldpos[1] self.tthp self.oldpos[2] self.zp self.oldpos[3]


