from gda.epics import CAClient 
from java import lang
from time import sleep

#
#
#   Struck used when using an external pulse to trigger counting, i.e. using a hardware trigger to read 
#    the vortex detector and ion chambers
#   This class does does not set collection times etc.... it simply reads the 
#   counts of a given set of scalar channels
#
class StruckIonChambers(ScannableBase):
	def __init__(self, name,pv1,pv2,channels,formatstring):
		self.pvstring =pv1
		self.mcastring =pv2
		# EPICS interface - configure scaler bits
		self.clock=CAClient(self.pvstring+".CNT");self.clock.configure()
		# Set external triggering on
		self.extMode=CAClient(self.pvstring+":CH1_REF");self.extMode.configure();self.extMode.caput('0');self.extMode.clearup()
		# status 
		self.status=CAClient(self.pvstring+".SS");self.status.configure()
		# Set up the pvs for channel counts
		self.counts=[]
		for i in range(len(channels)):
			str1 = self.pvstring +".S"+str(channels[i])    # counts in the channel
			self.counts.append(CAClient(str1))
			self.counts[-1].configure()
		# Set the update rate to 60Hz
		self.rate=CAClient(self.pvstring+'.RATE' );self.rate.configure();self.rate.caput(60);self.rate.clearup()
		
		self.das=finder.find("daserver")
		name='IO It Idrain'
		self.setName(name)
		self.setInputNames([])
		self.setExtraNames(['ionchamber1','ionchamber2','ionchamber3'])
		self.setOutputFormat(["%6.6g","%6.6g","%6.6g"])
		self.setLevel(9)
                     # MCA Setup
		# Need to set the count time to zero so it counts until it gets a pulse
		self.mcaCountTime=CAClient(self.mcastring+":PresetReal");self.mcaCountTime.configure();self.mcaCountTime.caput(0.000);self.mcaCountTime.clearup()
		self.mcaDwellTime=CAClient(self.mcastring+":Dwell");self.mcaDwellTime.configure();self.mcaDwellTime.caput(0.000);self.mcaDwellTime.clearup()
		# Channel advance set to external so it shifts recording to next channel on a tfg pulse
		self.mcaChAdv=CAClient(self.mcastring+":ChannelAdvance");self.mcaChAdv.configure();self.mcaChAdv.caput(1);self.mcaChAdv.clearup()
		# Erase/Start and Stop PVs
		self.mcaErsStrt=CAClient(self.mcastring+":EraseStart");self.mcaErsStrt.configure()
		self.mcaStopPV=CAClient(self.mcastring+":StopAll");self.mcaStopPV.configure()
		self.mcaStatus=CAClient(self.mcastring+":Acquiring");self.mcaStatus.configure()
		self.mcalist=[]
		self.mcabusy = False
		for i in range(len(channels)):
			str1 = self.mcastring +":mca"+str(channels[i])    # counts in the channel
			self.mcalist.append(CAClient(str1))
			self.mcalist[-1].configure()

	#
	# Return counts....Warning....this can read while still collecting....
	#
	def getPosition(self):
		value=[]	
		try:
			for i in range(len(self.counts)):           
				if not self.counts[i].isConfigured():
					self.counts[i].configure()
					val=float(self.counts[i].caget())
					value.append(val)
					self.counts[i].clearup()
				else:
					val=float(self.counts[i].caget())
					value.append(val)
			print 'value',value
			return value
		except:
			print "Error returning position"
			return 0

	#
	# Returns state of the struck
	#
	def isBusy(self):
		return self.mcabusy
			
	#
	# start collection
	#
	def start(self):
		try:
			if not self.clock.isConfigured():
				self.clock.configure()
				self.clock.caput(1)
				self.clock.clearup()
			else:
				self.clock.caput(1)
		except:
			print "Struck::Start failure"
	
	def getStatus(self):
		return int(self.clock.caget())


	def getMCAStatus(self):
		return int(self.mcaStatus.caget())

	def isClear(self):
		if(float(self.counts[0].caget())==0.0):
			return 1
		else:
			return 0

	def clearAndPrepare(self):
		self.stop()
		self.start()

	#
	# Stop collection
	# 
	def stop(self):
		try:
			if not self.clock.isConfigured():
				self.clock.configure()
				self.clock.caput(0)
				self.clock.clearup()
			else:
				self.clock.caput(0)
		except:
			print "Struck::stop failure"

	def collectMCA(self,collectionTime=500.):
		try:
			self.mcabusy = True
			self.stop()
			self.start()
			while(self.isClear()==0 or self.getStatus()==0):
				print 'ionchambers struck not ready: Waiting to clear'
				sleep(0.50)
				self.clearAndPrepare()
				sleep(0.50)
			#sleep(0.5)
			self.das.sendCommand("tfg init")
			command = "tfg setup-groups cycles 1\n1 1.0E-7 %f 0 15 0 0\n-1 0 0 0 0 0 0 " %(collectionTime/1000.0)
			#print command
			self.das.sendCommand(command)
			self.das.sendCommand("tfg start")
			sleep(collectionTime/1000.0)
			self.das.sendCommand("tfg wait")
			#sleep(0.5)
			self.stop()
			self.mcabusy = False
		except:
			self.mcabusy = False
		
	def asynchronousMoveTo(self,newPosition):
		self.collectMCA(newPosition)

	#
	# Erase MCAs and start collecting
	#
	def mcaEraseAndStart(self):
		try:
			if not self.mcaStopPV.isConfigured():
				self.mcaStopPV.configure()
				self.mcaStopPV.caput(1)
				self.mcaStopPV.clearup()
			else:
				self.mcaStopPV.caput(1)
		except:
			print "Struck::Start stop mca failure"
		try:
			if not self.mcaErsStrt.isConfigured():
				self.mcaErsStrt.configure()
				self.mcaErsStrt.caput(1)
				self.mcaErsStrt.clearup()
			else:
				self.mcaErsStrt.caput(1)
		except:
			print "Struck::Start Erase and Start mca failure"

	#
	# Stop the mcas collecting
	#
	def mcaStop(self):
		try:
			if not self.mcaStopPV.isConfigured():
				self.mcaStopPV.configure()
				self.mcaStopPV.caput(1)
				self.mcaStopPV.clearup()
			else:
				self.mcaStopPV.caput(1)
		except:
			print "Struck::Start stop mca failure"

	#
	# Return the MCA data from 1 to some length
	# I am ignoring 0 as is rastering this has rubbish
	#
	def getMCAData(self,length):
		mydata=[]
		for mca in self.mcalist:
			arr=mca.cagetArray()[0:length]
			arr=map(float,arr)
			mydata.append(arr)
		return mydata
	#
	# Return the MCA data from 1 to some length
	# I am ignoring 0 as is rastering this has rubbish
	#
	def getMCADataAtIndex(self,index):
		mydata=[]
		for mca in self.mcalist:
			mydata.append(mca.cagetArray()[index:index+1])
		mydata=map(float,mydata)
		return mydata


ionChambers=StruckIonChambers('ionChambers','BL18I-EA-DET-03:SCALER','BL18I-EA-DET-03:MCA',[6,7,8],"%4.4f")
