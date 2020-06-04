def setkthspeed(speed):
	#sleep(.5)
	caput('BL16I-MO-DIFF-01:SAMPLE:KTHETA.VELO',speed)
	#sleep(.5)

class IntegrateDetectorWhileMovingMotorPDClass(ScannableMotionBase):
	'''
	Experimental - do not use!!
	'''
	def __init__(self,help=None):
		self.setName('rocketa');
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.setInputNames(['range','speed'])
		self.setExtraNames(['counts']);
		self.setOutputFormat(['%.4f','%.4f','%.0f'])
		self.setLevel(9)
		[self.range, self.speed, self.counts]=[0,0,0]
		self.mot=finder.find('kth_motor')

	def asynchronousMoveTo(self,invec):
		[self.range, self.speed]=invec
		kthpos=kth()
		#self.mot.setSpeed(4) #no longer works
		setkthspeed(4)
		kth.r(-self.range/2)
		#self.mot.setSpeed(self.speed)
		setkthspeed(self.speed)
		print "start move"
#		mca1.stop()
#		mca1.erase()
#		mca1.start()
		ct3.asynchronousMoveTo(1000)
		kth.r(self.range)
		#kth.r(-self.range)
		#kth.r(self.range)
		#kth.r(-self.range)
		ct3.stop()
#		mca1.stop()
#		mca1.read()
		self.counts=ct3()
		#print ct3
		print "end move"
		#self.mot.setSpeed(4)
		setkthspeed(4)
		#kth(kthpos)

	def getPosition(self):
		return [self.range, self.speed, self.counts]
	
	def isBusy(self):
		return 0

	def stop(self):
		self.mot.stop()
		self.mot.setSpeed(4)
		
		


rocketa= IntegrateDetectorWhileMovingMotorPDClass()

class IntegrateDetectorWhileMovingMotorPDClass(ScannableMotionBase):
	'''
	Experimental - do not use!!
	'''
	def __init__(self,help=None):
		self.setName('rocketa');
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.setInputNames(['range','speed'])
		self.setExtraNames(['counts1','counts2','counts3','counts4']);
		self.setOutputFormat(['%.4f','%.4f']+4*['%.0f'])
		self.setLevel(9)
		[self.range, self.speed, self.counts]=[0,0,0]
		self.mot=finder.find('kth_motor')
		self.counts=4*[0]

	def asynchronousMoveTo(self,invec):
		[self.range, self.speed]=invec
		kthpos=kth()
		self.mot.setSpeed(4)
		kth.r(-self.range/2)
		self.mot.setSpeed(self.speed)

		ct3.asynchronousMoveTo(1000)
		kth.r(self.range)
		ct3.stop(); self.counts[0]=ct3()

		ct3.asynchronousMoveTo(1000)
		kth.r(-self.range)
		ct3.stop(); self.counts[1]=ct3()

		ct3.asynchronousMoveTo(1000)
		kth.r(self.range)
		ct3.stop(); self.counts[2]=ct3()

		ct3.asynchronousMoveTo(1000)
		kth.r(-self.range)
		ct3.stop(); self.counts[3]=ct3()

		self.mot.setSpeed(4)
		#kth(kthpos)

	def getPosition(self):
		return [self.range, self.speed]+self.counts
	
	def isBusy(self):
		return 0

	def stop(self):
		self.mot.stop()
		self.mot.setSpeed(4)

#rocketa4= IntegrateDetectorWhileMovingMotorPDClass()


class CountDetectorWhileMovingMotorPDClass(ScannableMotionBase):
	'''
	Experimental - do not use!!
	'''
	def __init__(self, angrange, speed, ctime, help=None):
		self.setName('rocketa');
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.setInputNames(['dummy'])
		self.range=angrange
		self.speed=speed
		self.ctime=ctime
		self.ncts=int(angrange/speed/ctime)
		self.cts=self.ncts*[0]
		self.extranames=self.ncts*['']
		for ii in range(self.ncts):
			self.extranames[ii]='counts'+str(ii)
		self.setExtraNames(['range','speed','ctime']+self.extranames);
		self.setOutputFormat(['%.0f','%.4f','%.4f','%.2f']+self.ncts*['%.0f'])	
		self.setLevel(9)
		self.mot=finder.find('kth_motor')
		
		

	def asynchronousMoveTo(self,dummy):
		self.mot.setSpeed(4)
		kth.r(-self.range/2)
		self.mot.setSpeed(self.speed)
		print "start move"
		
		kth.ar(self.range)
		ii=0
#		while not kth.isBusy():		
#			print kth.isBusy()
#			sleep(.1)
#		print ii, kth.isBusy(), ii<self.ncts
		while kth.isBusy() and ii<self.ncts:
#			print ii, kth.isBusy(), ii<self.ncts
			ct3(self.ctime); self.cts[ii]=ct3(); ii+=1;

		print "end move"
		self.mot.setSpeed(4)
		#kth(kthpos)

	def getPosition(self):
		return [ 1, self.range, self.speed, self.ctime]+self.cts
	
	def isBusy(self):
		return 0

	def stop(self):
		self.mot.stop()
		self.mot.setSpeed(4)
		

class CountDetectorWhileMovingMotorWithEncoderPDClass(ScannableMotionBase):
	'''
	Experimental - do not use!!
	'''
	def __init__(self, angrange, speed, ctime, help=None):
		self.setName('rocketa');
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.setInputNames(['dummy'])
		self.range=angrange
		self.speed=speed
		self.ctime=ctime
		self.ncts=int(angrange/speed/ctime)
		self.cts=self.ncts*[0]
		self.encoder=self.ncts*[0]
		self.fluo=self.ncts*[0]
		self.fluo2=self.ncts*[0]	
		self.ctsnames=self.ncts*['']
		self.encodernames=self.ncts*['']
		self.fluonames=self.ncts*['']
		self.fluonames2=self.ncts*['']	
		for ii in range(self.ncts):
			self.ctsnames[ii]='counts'+str(ii)
			self.encodernames[ii]='eta'+str(ii)
			self.fluonames[ii]='fluoA'+str(ii)
			self.fluonames2[ii]='fluoB'+str(ii)
		self.setExtraNames(['range','speed','ctime', 'fluo']+self.ctsnames+self.encodernames+self.fluonames+self.fluonames2);
		self.setOutputFormat(['%.0f','%.4f','%.4f','%.2f', '%.0f' ]+self.ncts*['%.0f']+self.ncts*['%.4f']+self.ncts*['%.0f']+self.ncts*['%.0f'])	
		self.setLevel(9)
		self.mot=finder.find('kth_motor')

		
		self.sis1=CAClient('BL16I-EA-DET-01:SCALER.S3')
		self.sis2=CAClient('BL16I-EA-DET-01:SCALER.S6')
		self.sis3=CAClient('BL16I-EA-DET-01:SCALER.S9')	
		self.sisTP=CAClient('BL16I-EA-DET-01:SCALER.TP')
		self.sisCNT=CAClient('BL16I-EA-DET-01:SCALER.CNT')
		self.sis1.configure()
		self.sis2.configure()
		self.sis3.configure()
		self.sisTP.configure()
		self.sisCNT.configure()	

	def __del__(self):
		self.sis1.clearup()
		self.sis2.clearup()
		self.sis3.clearup()
		self.sisTP.clearup()
		self.sisCNT.clearup()	

	def asynchronousMoveTo(self,dummy):
		self.mot.setSpeed(4)
		kth.r(-self.range/2)
		self.mot.setSpeed(self.speed)
		print "start move"
		
		kth.ar(self.range)
		ii=0
#		while not kth.isBusy():		
#			print kth.isBusy()
#			sleep(.1)
#		print ii, kth.isBusy(), ii<self.ncts
		self.fluototal=0;
		self.sisTP.caput(self.ctime);

		while kth.isBusy() and ii<self.ncts:
#			print ii, kth.isBusy(), ii<self.ncts
			self.enc1=kth();	#read encoder before count
			#ct3(self.ctime); 
			self.sisCNT.caput('1')
			while self.sisCNT.caget()=='1':
				pass
			
			self.cts[ii]=float(self.sis1.caget());
			self.fluo[ii]=float(self.sis2.caget());
			self.fluo2[ii]=float(self.sis3.caget()); 
			self.fluototal=self.fluototal+self.fluo[ii];
			self.enc2=kth();	#read encoder after
			self.encoder[ii]=(self.enc1+self.enc2)/2;
			ii+=1;

		while ii<self.ncts:
			self.encoder[ii]=0;
			self.cts[ii]=0;
			self.fluo[ii]=0;
			self.fluo2[ii]=0;
			ii+=1;		

		print "end move"
		self.mot.setSpeed(4)
		#kth(kthpos)

	def getPosition(self):
		return [ 1, self.range, self.speed, self.ctime, self.fluototal]+self.cts+self.encoder+self.fluo+self.fluo2
	
	def isBusy(self):
		return 0

	def stop(self):
		self.mot.stop()
		self.mot.setSpeed(4)



class CountDetectorWhileMovingMotorWithEncoderWithoutStoppingAndStartingTheTimerPDClass(ScannableMotionBase):
	'''
	Experimental - do not use!!
	'''
	def __init__(self, angrange, speed, ctime, help=None):
		self.setName('rocketa');
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.setInputNames(['dummy'])
		self.range=angrange
		self.speed=speed
		self.ctime=ctime
		self.ncts=int(angrange/speed/ctime)
		self.cts=self.ncts*[0]
		self.encoder=self.ncts*[0]
		self.times=self.ncts*[0]
		self.ctsnames=self.ncts*['']
		self.encodernames=self.ncts*['']
		self.timenames=self.ncts*['']
		for ii in range(self.ncts):
			self.ctsnames[ii]='counts'+str(ii)
			self.encodernames[ii]='eta'+str(ii)
			self.timenames[ii]='time'+str(ii)
		self.setExtraNames(['range','speed','ctime','ncts']+self.ctsnames+self.encodernames+self.timenames);
		self.setOutputFormat(['%.0f','%.4f','%.4f','%.2f','%.0f']+self.ncts*['%.0f']+self.ncts*['%.4f']+self.ncts*['%.4f'])	
		self.setLevel(9)
		self.mot=finder.find('kth_motor')

	def asynchronousMoveTo(self,dummy):
		self.mot.setSpeed(4)
		kth.r(-self.range/2)
		self.mot.setSpeed(self.speed)
		print "start move"
		ii=0;
		lastcnts=0;
		currentcnts=0;
		lasttime=0;
		currenttime=0;
		ct3.asynchronousMoveTo(1000);
		kth.ar(self.range)
#		while not kth.isBusy():		
#			print kth.isBusy()
#			sleep(.1)
#		print ii, kth.isBusy(), ii<self.ncts

		while kth.isBusy() and ii<self.ncts-1:
#			print ii, kth.isBusy(), ii<self.ncts
			sleep(self.ctime);
			currentcnts=ct3();
			currenttime=ct1(); 
			self.encoder[ii]=kth();
			self.cts[ii]=currentcnts-lastcnts;
			self.times[ii]=(currenttime-lasttime)/50000000;
			lastcnts=currentcnts;
			lasttime=currenttime;
			ii+=1;
		ct3.stop();
		self.cts[ii]=ct3()-lastcnts;
		self.times[ii]=(ct1()-lasttime)/50000000;
		self.encoder[ii]=kth();

		print "end move"
		self.mot.setSpeed(4)
		#kth(kthpos)

	def getPosition(self):
		return [ 1, self.range, self.speed, self.ctime, self.ncts]+self.cts+self.encoder+self.times
	
	def isBusy(self):
		return 0

	def stop(self):
		self.mot.stop()
		self.mot.setSpeed(4)

