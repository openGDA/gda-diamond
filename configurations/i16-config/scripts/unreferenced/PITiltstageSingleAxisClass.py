#from gda.epics import CAClient 
#from java import lang
#from gda.device.scannable import ScannableMotionBase
#


class PITiltstageSingleAxisClass(ScannableMotionBase):

	'''Control single axis of PI tilt stage using Asyn Record
	'''
	def __init__(self, name, asynrecordname, portname, axisnumber, unit, format, help=None):
		#example.: asynrecordname='BL16I-EA-DET-03:asyn'
		self.setName(name);
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.setInputNames([name])
		#self.setExtraNames();
		self.Units=[unit]
		self.setOutputFormat([format])
		self.setLevel(5)
		self.movecommand=str(int(axisnumber))+'ma'
		self.getposcommand=str(int(axisnumber))+'tp\\x0a'
		self.servoloopcommand=str(int(axisnumber))+'sl1'
		self.urad2deg=180/pi/1000000
		
		self.processcli=CAClient(asynrecordname+'.PROC')	#command to process string
		self.readcli=CAClient(asynrecordname+'.TINP')           #read string
		self.writecli=CAClient(asynrecordname+'.AOUT')          #write string
		#self.processcli.configure()
		self.readcli.configure()
		self.writecli.configure()

		self.writecli.caput(self.servoloopcommand)		#turn servoloop on


		cli=CAClient(asynrecordname+'.PORT')	
		cli.configure()
		cli.caput(portname)
		cli.clearup()
		
		cli=CAClient(asynrecordname+'.IEOS')	
		cli.configure()
		cli.caput('\\x0a')				#terminator for return string
		cli.clearup()

		cli=CAClient(asynrecordname+'.FCTL')	
		cli.configure()
		cli.caput(2)		#hardware handshaking		
		cli.clearup()

		cli=CAClient(asynrecordname+'.TMOT')	
		cli.configure()
		cli.caput(.1)		#timeout		
		cli.clearup()

		self.writecli.caput(str(int(axisnumber))+'sl1\\x0a')	#start servo loop on axis
		sleep(0.3)
		self.writecli.caput('1sl1\\x0a')	#enable z
		sleep(0.3)
		self.writecli.caput('1ma100\\x0a')	#move z to mid-range

		self.readcli.clearup()
		self.writecli.clearup()

	def getPosition(self):
		self.writecli.configure()
		self.readcli.configure()
		self.writecli.caput(self.getposcommand)
		#self.processcli.caput(0);
		sleep(.1)	#wait for new string to be returned
		self.outstr=self.readcli.caget()
		#print self.outstr
		self.writecli.clearup()
		self.readcli.clearup()
		return self.urad2deg*float(self.outstr) 

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newPosition):
		self.writecli.configure()
 		self.movestring=self.movecommand+str(newPosition/self.urad2deg)+'\\x0a'
		self.writecli.caput(self.movestring)
		#self.processcli.caput(0) 
         		self.writecli.clearup()
		sleep(0.2)  
		return


xtilt=PITiltstageSingleAxisClass('xtilt','BL16I-CS-SPARE-01:asyn','Serial8',2,'deg','%.5f',help='PI tilt stage x-tilt (deg)')
ytilt=PITiltstageSingleAxisClass('ytilt','BL16I-CS-SPARE-01:asyn','Serial8',3,'deg','%.5f',help='PI tilt stage y-tilt (deg)')


