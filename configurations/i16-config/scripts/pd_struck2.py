from gda.epics import CAClient 
from gda.device.scannable import ScannableMotionBase

class Struck2(ScannableMotionBase):
	'''
	dev=Struck(name,EpicsPVroot,channel_list)
	input: count-time (sec)
	extra output: counts in channels specified by channel_list
	PD to control Stuck counter-timer
	'shownames()' method displays names of all available channels
	'showselected()' method displays names of channels in use
	'setname(chan,name)' sets a name
	'setchans(channel_list)' selects the SCA channel numbers to use'
	'''
	def __init__(self, name,pv,channellist):
		self.setName(name)
		self.pvstring =pv
		self.channellist=channellist
		self.number_of_channels=32
		self.setallnames()
		self.restart()

	def restart(self):
		self.setInputNames(['counttime'])
		self.setLevel(9)

		fmt='%.0f'
		nchans=len(self.channellist)
		self.setExtraNames([])

		self.setOutputFormat(['%.2f']+[fmt]*nchans)


		self.chan_name[1]='Preset value for timer'

		extranames=[]
		self.clients=[] 

		for ii in range(nchans):
			#create list of channel names and CA clients for reading channel values
			extranames+=[self.chan_name[self.channellist[ii]]]
			cli=CAClient(self.pvstring +".S"+str(self.channellist[ii]))
			self.clients+=[cli]
			self.clients[-1].configure()
		#print extranames	
		self.setExtraNames(extranames)		

		self.str1 = self.pvstring+".CNT" 
		self.configstr=self.pvstring+'.RATE' 

		self.clock=CAClient(self.pvstring+".CNT")
		self.tp=CAClient(self.pvstring+".TP")			# preset the counting time
		self.gatepreset=CAClient(self.pvstring+".G1")		#Gate Control Preset clock
		self.ch1=CAClient(self.pvstring +".S1") 			# preset channel
		self.chgate1=CAClient(self.pvstring +".PR1")		# Logic, gate on the channel
		self.rate=CAClient(self.configstr)

		self.rate.configure()
#		self.rate.caput(60)
		self.rate.clearup()
		self.count_time=0


		self.ch1.configure()
		self.chgate1.configure()
		self.clock.configure()
		self.tp.configure()
		self.clock.configure()

	
	def getPosition(self):
		counts=[]
		for cli in self.clients:
			counts+=[float(cli.caget())]
		return [self.count_time]+counts

	def isBusy(self):
			if self.clock.caget()=='0':
				return 0
			if self.clock.caget()=='1':
				return 1 
			
	def asynchronousMoveTo(self,new_position):
		if new_position!=self.count_time:
			self.count_time=new_position	# new count time
			self.tp.caput(new_position)
		self.clock.caput("1")

	def stop(self):
		try:		
			self.clock.caput("0")
		except:
			print "Struck::stop failure"

	def setallnames(self):
		# default names
		self.chan_name=['']*(self.number_of_channels+1)
		for i in range(1,self.number_of_channels+1):
			self.chan_name[i]='Ch'+str(i)

	def setname(self,chan,name):
		# set user defined name for a channel
		self.chan_name[chan]=name
		self.restart()

	def shownames(self):
		# display names
		for i in range(1,self.number_of_channels+1):
			print 'Channel ',str(i),': ', self.chan_name[i]

	def showselected(self):
		# display names
		for i in self.channellist:
			print 'Channel ',str(i),': ', self.chan_name[i]

	def setchans(self, channellist):
		self.channellist=channellist
		self.restart()

 

