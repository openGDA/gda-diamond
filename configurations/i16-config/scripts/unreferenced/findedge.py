#from gda.epics import CAClient 
#from java import lang
#from gda.device.scannable import ScannableMotionBase
#connect 

class findedge(ScannableMotionBase):
	'''

	'''
	def __init__(self, name, help=None):
		#example.: asynrecordname='BL16I-EA-DET-03:asyn'
		asynrecordname='BL16I-EA-SPARE-04:asyn'
		self.setName(name)
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.setExtraNames(['xtilt', 'ytilt','rtilt','temp'])
		self.setInputNames([])		
		self.Units=['deg','deg','deg','degC']
		self.setOutputFormat(['%.5f',' %.5f', '%.5f','%.1f'])
		self.setLevel(9)
		self.processcli=CAClient(asynrecordname+'.PROC')	#command to process string
		self.readcli=CAClient(asynrecordname+'.TINP')
		cli=CAClient(asynrecordname+'.PORT')	
		cli.configure()
#		cli.caput('Serial6')
		cli.caput('Spare4')				#terminator for return string
		cli.clearup()
		cli=CAClient(asynrecordname+'.IEOS')	
		cli.configure()
		cli.caput('\\x03')				#terminator for return string
		cli.clearup()
		cli=CAClient(asynrecordname+'.AOUT')	
		cli.configure()
		cli.caput('\\x16\\x02N0C1 W N 050\\x03\\x0d\\x0a')	#command string to set no. of samples (more than ~80 will take longer than 1 sec timeout)
		cli.clearup()
		self.processcli.configure()
		self.processcli.caput(0);				#send send command stirng
		sleep(2)
		cli=CAClient(asynrecordname+'.AOUT')	
		cli.configure()
		cli.caput('\\x16\\x02N0C1 G A\\x03\\x0d\\x0a')	#command string to read all
		cli.clearup()
		cli=CAClient(asynrecordname+'.TMOT')		#set timeout
		cli.configure()
		cli.caput(5)
		cli.clearup()

	def atScanStart(self):
		if not self.processcli.isConfigured():
			self.processcli.configure()
		if not self.readcli.isConfigured():
			self.readcli.configure()

	def atScanEnd(self):
		self.processcli.clearup()	
		self.readcli.clearup()

	def getPosition(self):
		if not self.processcli.isConfigured():
			self.atScanStart()
		self.processcli.caput(0);
		sleep(2)	#wait for new string to be returned
		if not self.readcli.isConfigured():
			self.atScanStart()
		self.outstr=self.readcli.caget()
		#print self.outstr
		mrad2deg=180/pi/1000
		self.xdeg=mrad2deg*float(self.outstr[15:21])
		self.ydeg=mrad2deg*float(self.outstr[24:30])
		self.rdeg=sqrt(self.xdeg**2+self.ydeg**2)
		self.degC=float(self.outstr[33:99])
		return [self.xdeg,self.ydeg,-self.rdeg,self.degC]


	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newPosition):
		return

nivel=NivelViaAsynRecord('nivel','BL16I-EA-SPARE-04:asyn',help='Connect to x32 serial and port Spare4')
