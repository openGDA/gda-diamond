from gda.epics import CAClient
from java.lang import *
from gda.device.scannable import ScannableBase
from gda.device import Scannable
from org.python.modules.math import *
from time import sleep
from java.lang import *
from java.util import Vector
import jarray
from gda.scan import ScanDataPoint
from gda.jython import ScriptBase
from java.util import Date
from java.text import SimpleDateFormat
from gda.data import PathConstructor
import thread
import time
#from gda.data.fileregistrar import FileRegistrarHelper
#====================================================
#
#   A step map scan
#
#   Usage:
#   pdq=I18StepMapClass()
#                                 xstart     xend    xstep        ystart     yend   ystep    time(ms)
#   pdq.stepmapscan(-7.474,  -6.613,   0.01,     6.178,   6.86,   0.01,  3000)#    
#
#
#   Does not plot as it runs but will produce a .dat file. You can use the load command in GDA Microfocus window 
#   to produce a map from the .dat file later
#====================================================

class I18ContinuousMapClass(ScriptBase):
	#====================================================
	#
	# Setup the I18 Step map class
	#
	#====================================================
	def __init__(self, datafileNo="default"):
		# Create some data vectors to hold the scan data (and names)
		self.scannableNamesVector=Vector()
		self.scannableNamesVector.add("MicroFocusSampleX")
		self.scannableNamesVector.add("MicroFocusSampleY")
		self.detectorNamesVector=Vector()
		self.detectorNamesVector.add("counterTimer01")
		self.detectorNamesVector.add("counterTimer02")
		# Find the script controller 
		self.controller = finder.find("MicroFocusController")	
		#
		self.xmotor=finder.find("sample_x_motor")
		self.xpos_start=CAClient("BL18I-MO-TABLE-01:X:START")
		self.xpos_start.configure()
		self.xpos_end=CAClient("BL18I-MO-TABLE-01:X:END")
		self.xpos_end.configure()
		self.xpos_steps=CAClient("BL18I-MO-TABLE-01:X:STEPS")
		self.xpos_steps.configure()
		self.xpos_send = CAClient("BL18I-MO-TABLE-01:X:SEND.PROC")
		self.xpos_send.configure()
		self.xpos_enable=CAClient("BL18I-MO-TABLE-01:X:ENABLE")
		self.xpos_enable.configure()
		self.ymotor=MicroFocusSampleY
		self.das=finder.find("daserver")
		self.mcaList=[]
		self.pointTime=[]
		self.ionchambers=ionChambers
		self.ionchamberData=[]
		# Windowing data
		self.windowValues=[]
		self.windowName=[]
		self.windowArrays=[]
		# Basically take 4 seconds to accelerate the stage up to speed
		# Use this time to work out what distance this is based on
		# collection time and speed set for the motor....
		self.overShootTime=5.0
		
		if(datafileNo == "default"):
			self.runs=NumTracker("tmp")
			self.fileno=self.runs.getCurrentFileNumber()+1
			self.runs.incrementNumber()
		else:
			self.fileno = datafileNo
		self.runext='.dat'
		self.datadir=LocalProperties.get("gda.data.scan.datawriter.datadir")
		self.datafilename=self.datadir+'/'+str(self.fileno)+self.runext
		#
		# Make a directory to store the mca files in
		#
		self.mcadir=self.datadir+'/mca/'+str(self.fileno)+'/'
		self.mcarootname=self.mcadir+str(self.fileno)
		#
		if not os.path.isdir(self.mcadir):
			os.mkdir(self.mcadir)
		self.tag=1
		self.createFile()
		# Set default windows
		self.setWindows('/dls/i18/software/gda/config/default.scas')
#		self.archiveFileList=[]
#		self.archiveFileList.append(self.datafilename)
		self.xspress = finder.find("xspress2system")


	#
	# Raster a map
	#
	def rastermapscan(self,startx,stopx,nxsteps,rowtime,starty,stopy,nysteps):
		global mapRunning
		lock=0
		try:
			if(rowtime<10.0):
				print 'Time is too short...must be at least 10 seconds'
				self.controller.update(None, "STOP")
				return
			print 'locking express'
			lock  = self.xspress.tryLock(5,java.util.concurrent.TimeUnit.SECONDS)
			print "the lock value is " + str(lock)
			if not lock:
				print "Xspress detector is already locked"
				self.controller.update(None, "STOP")
				return
			self.checkForInterrupt()
			stepx=abs(stopx-startx)/nxsteps
			##Note the nysteps -1 is to make sure the map is plotted correctly in GDA
			stepy = abs(stopy - starty) / (nysteps - 1)
			timestep=rowtime/nxsteps	
			overshootx=int((self.overShootTime/timestep)+0.5)*stepx
			# Move the motor to the start
			try:
				MicroFocusSampleY.moveTo(starty)
			except:
				self.interrupted = 1
			self.checkForInterrupt()
			currentypos=starty
			# Set ion chambers to collect for 10 seconds for a good average....	
			self.checkForInterrupt()
			print 'nxsteps ', nxsteps
			print 'nysteps ',nysteps
			print 'timestep ',timestep
			print 'stepx ', stepx
			print 'stepy ', stepy
			for i in range(nysteps):
				#
				# How to split up if topup is coming
				#
				self.checkForInterrupt()
				scanSections=[]
				topuptime=BeamMonitor.timeBeforeTopup()
				print 'topuptime',topuptime,rowtime
				# If you've got less than 10 seconds to wait for topup just wait it out....
				print 'topup wait1',(topuptime <rowtime),(topuptime<=10.0)
				if(topuptime<=10.0):
					self.checkForInterrupt()
					print 'topup wait'
					try:
						sleep(toptuptime)
					except:
						self.interrupted =1
					self.checkForInterrupt()
					while(BeamMonitor.collectBeforeTopupTime(timestep) == 1):
						try:
							sleep(1.0)
						except:
							self.interrupted =1
						self.checkForInterrupt()
				elif(topuptime>10.0 and topuptime <rowtime):
					#
					# Split up the scan if required
					#
					# topup will occur before end of the row
					nsteps1=int((topuptime-2.0)/timestep)-2
					nsteps2=int(nxsteps-(topuptime-2.0)/timestep)+2
					startx1=startx
					stopx1=startx1+nsteps1*stepx
					startx2=stopx1
					stopx2=stopx
					scanSections.append([nsteps1,startx1,stopx1])
					scanSections.append([nsteps2,startx2,stopx2])
					self.checkForInterrupt()
				else:
					scanSections.append([nxsteps,startx,stopx])
				sectionindex=0
				print 'topup wait2',scanSections
				section=scanSections[0]
				self.setPositionCompare(float('%.3f' %section[1]),float('%.3f' %section[2]),float('%.3f' %section[0]),time) 
				self.disablePositionCompare()
				for section in scanSections:
					self.windowArrays = []
					for j in range(len(self.windowName)):
						self.windowArrays.append(self.initArray1D(int(section[0]))) 
					self.checkForInterrupt()
					#
					# clear detector and set to collect nsteps + 2
					# Detector goes straight into a paused state...i.e. starts collecting in frame 1 
					# So the first motor step will stop this collecting and jump forward.
					# also add another point to the end. 
					#
					# Move the motor to the start - step
					# Set the speed to maximum
					try:
						self.xmotor.setSpeed(1.0)
				
					
					# Move to start - 50 microns
					except:
						self.interrupted =1
					self.checkForInterrupt()
					try:
						print 'a'
						MicroFocusSampleX.moveTo(section[1]-overshootx)
						self.setRunSpeed(startx,stopx,rowtime)
						self.checkForInterrupt()
						print 'b'
						#self.setPositionCompare(section[1],section[2],section[0],time) 
						self.enablePositionCompare()
						while(int(self.xpos_enable.caget())==0):
							print 'waiting for xps enable'
							try:
								sleep(0.050)
								self.enablePositionCompare()								
							except:
								self.interrupted=1

						print 'c'
						self.checkForInterrupt()
						print 'd'
						self.prepareDetectorForRastering(section[0]+3)
						self.checkForInterrupt()
						print 'e'
						self.ionchambers.mcaStop()
						while(self.ionchambers.getMCAStatus()==1):
							print 'ionchambers struck not ready: Waiting to start'
							try:
								sleep(0.050)
								self.ionchambers.mcaStop()
							except:
								self.interrupted=1

						print 'f'
						self.ionchambers.mcaEraseAndStart()
						while(self.ionchambers.getMCAStatus()==0):
							print 'ionchambers struck not ready: Waiting to start'
							try:
								sleep(0.050)
								self.ionchambers.mcaEraseAndStart()
							except:
								self.interrupted=1
						print 'g'
						self.checkForInterrupt()
						print 'Section',section
						print 'h'
						#self.checkForInterrupt()
						# Move the motor to one step past the end
						# This will account for any motor servo control at end so all points
						# have roughly same dwell time.
						# May have to tune this it depends on the data.........
						#
						print 'moving motor'
						MicroFocusSampleX.asynchronousMoveTo(section[2]+overshootx)
						print 'i'
						self.checkForInterrupt()
						print 'j'
						self.writeoutDetectorDataRow(startx,stopx,stepx,currentypos,i,section[0],sectionindex)
						print 'k'
						self.checkForInterrupt()
						print 'waiting'
						MicroFocusSampleX.waitWhileBusy()
						print 'finished waiting'
						self.checkForInterrupt()
						#
						# make sure motor has stopped (testing only)
						#
						# disable the detector and readout
						self.ionchambers.mcaStop()
						self.stopDetector()
						self.checkForInterrupt()
						self.disablePositionCompare()
						self.checkForInterrupt()
						self.xmotor.setSpeed(1.0)
						self.checkForInterrupt()
						print 'moveto'
						MicroFocusSampleX.asynchronousMoveTo(section[1]-overshootx)
						print 'moveto neg'
						self.checkForInterrupt()
						#
						# process output
						#
						print 'write out data'
						self.ionchamberData=self.ionchambers.getMCAData(section[0]+1)
						self.writeSummary(currentypos,i,section[1],stepx,section[0],sectionindex)
						self.checkForInterrupt()
						sectionindex=section[0]
						MicroFocusSampleX.waitWhileBusy()
						self.checkForInterrupt()
					except:
						self.interrupted =1
					self.checkForInterrupt()
					#
					# Write out the detector data 
					#
				currentypos=currentypos+stepy
				self.checkForInterrupt()
				# Move the y motor to its next position
				try:
					MicroFocusSampleY.moveTo(currentypos)
				except:
					self.interrupted =1
				self.checkForInterrupt()
			self.controller.update(None, "STOP")
		finally:
			if(lock):
				print 'unlocking xpress'
				self.xspress.unlock()
			self.xmotor.setSpeed(1.0)
			print "list of files to be archived are "
#			print self.archiveFileList
			print 'scan complete'
#			FileRegistrarHelper.registerFiles(self.archiveFileList)


	def prepareDetectorForRastering(self,noOfFrames):
		self.das.sendCommand("disable 0")
		self.das.sendCommand("clear 0")
		self.das.sendCommand("enable 0")
		self.das.sendCommand("tfg init")
		command = "tfg setup-groups ext-start cycles 1 \n%d 1.0E-6 1.0E-6 0 7 0 8\n-1 0 0 0 0 0 0"  %(noOfFrames)
		self.das.sendCommand(command)
		self.das.sendCommand("tfg start")

	#====================================================
	#
	# Stop the tfg and disable the detector
	#
	#====================================================
	def stopDetector(self):
		self.das.sendCommand("tfg stop")
		
	#====================================================
	#
	# Creates an srs data file
	#
	#====================================================
	def createFile(self):
		fid=open(self.datafilename,'w')
		# get datetime
		rightNow = Calendar.getInstance()
		year = rightNow.get(Calendar.YEAR)
		month = rightNow.get(Calendar.MONTH)
		day = rightNow.get(Calendar.DAY_OF_MONTH)
		hour = rightNow.get(Calendar.HOUR)
		minute = rightNow.get(Calendar.MINUTE)
		second = rightNow.get(Calendar.SECOND)
		print "Writing data to file:"+self.datafilename
		print "Writing mca file to:"+self.mcadir
		# write datetime
		line =' &SRS'
		line=' &END'
		print>>fid,line
		print>>fid,'   '
		print>>fid,'   '
		fid.close()

	#====================================================
	#
	#  Checks to see if stop has been pressed and trys to nicely stop the script
	#
	#====================================================
	def checkForInterrupt(self):
		
		if(self.interrupted):
			print 'Stopping map:Writing out data taken'
			# write the data we have so far and return
			self.stopDetector()	
			resetMicroFocusPanel()
			self.interrupted=Boolean(0)
			self.paused=Boolean(0)
			self.xmotor.stop()
			self.ymotor.stop()
			JythonServerFacade.getInstance().setScriptStatus(Jython.IDLE)
			print  'Now the nasty bit: throw an exception to stop running'
			self.controller.update(None, "STOP")
			raise lang.InterruptedException()

	#====================================================
	#
	#  Checks to see if the pause script button has been pressed
	#
	#====================================================
	def checkForPause(self):
		if(self.paused):
			JythonServerFacade.getInstance().setScriptStatus(Jython.PAUSED)
			while(self.paused):
				try:
					java.lang.Thread.sleep(10000)
					print 'Pausing at start of a row-awaiting resume'
				except:
					self.checkForInterrupt()


	#====================================================
	#
	#  Store rgb file
	#
	#====================================================
	def createRGBfile(self):
		newdatafilename=self.datadir+'/'+str(self.fileno)+".rgb"
		self.archiveFileList.append(newdatafilename)
		print 'RGB file name',newdatafilename
		fid=open(newdatafilename,'w')
		mystr='row  column  time  i0  it  idrain  '
		for k in range(len(self.windowName)):
			mystr=mystr+self.windowName[k]
			if(k<(len(self.windowName)-1) ):
				mystr=mystr+"  "
		print >> fid,mystr
		fid.close()	

	#====================================================
	#
	#  Store rgb file
	#
	#====================================================
	def appendToRGB(self,xindex,yindex,times,totalion,windowsums):
		newdatafilename=self.datadir+'/'+str(self.fileno)+".rgb"
		fid=open(newdatafilename,'a')
		mystr=str(times)+" "+str(self.ionchamberData[0][xindex])+" "+str(self.ionchamberData[1][xindex])+" "+str(self.ionchamberData[2][xindex])+" "
		for k in range(len(windowsums)):
			mystr=mystr+str(windowsums[k])
			if(k<(len(windowsums)-1)):
				mystr=mystr+" "
		print >> fid,yindex,xindex,mystr
		fid.close()

	#====================================================
	#
	#  Set the windows
	#
	#====================================================
	def setWindows(self,filename):
		infile=open(filename,'r')
		while infile:
			a=infile.readline()
			if(a.find("IONCHAMBER")>=0):
				continue    
			n = len(a)
			if n == 0:
				break
			temp=a.split('\t')
			tmpwindowValues=[[0,4095]]*9
			tmpwindowName=temp[0].strip().replace(' ','')
			print 'window name',tmpwindowName
			for j in range(len(temp)-1):
				index=j+1
				mytemp=temp[index].strip().replace('[','').replace(']','').split(',')
				mytemp=[int(mytemp[0]),int(mytemp[1])]
				tmpwindowValues[j]=mytemp 
				print 'window values chosen :',j,tmpwindowValues[j]
			self.windowValues.append(tmpwindowValues)
			self.windowName.append(tmpwindowName)

	#====================================================
	# return a 2D list filled with zeros
	#====================================================
	def initArray2D(self,rows,columns):
		a = []
		for x in range(rows):
			a.append([0.0] * columns)
		return a	

	#
	# return a 1D list filled with zeros		
	#
	def initArray1D(self,rows):
		a = []
		for x in range(rows):
			a.append(0.0)
		return a

	def setPositionCompare(self,start,stop,steps,time):
		# set motor start stop step for pulses
		self.disablePositionCompare()
		self.xpos_start.caput(start)
		self.xpos_send.caput(1)
		self.xpos_end.caput(stop)
		self.xpos_send.caput(1)
		self.xpos_steps.caput(steps)
		self.xpos_send.caput(1)
		self.enablePositionCompare()

	def setRunSpeed(self,start,stop,time):
		speed=abs(stop-start)/time
		if(speed>1.0):
			print 'Max speed of x stage motor is 1.0mm per second and you are requesting %fmm/sec'%(speed)
			print 'I am setting the max speed of the x motor to 1.0mm/sec' 
			speed=1.0
		self.xmotor.setSpeed(speed)
		

	def disablePositionCompare(self):
		# set motor start stop step for pulses
		self.xpos_enable.caput(0)
		self.xpos_send.caput(1)

	def enablePositionCompare(self):
		# set motor start stop step for pulses
		self.xpos_enable.caput(1)
		self.xpos_send.caput(1)

	#
	# Stop the detector and clear the tfg
	#
	def stopDetector(self):
		self.das.sendCommand("tfg init")
		self.das.sendCommand("disable 0")


	#
	# To update the GUI etc.
	#
	def update(controller, msg, exceptionType=None, exception=None, traceback=None, Raise=False):
		handle_messages.log(controller, "I18ContinuousScan:"+msg, exceptionType, exception, traceback, Raise)


	#
	#
	# This method writes out the detector data and records the time from the time scaler from the detector
	# 
	#
	def writeoutDetectorDataRow(self,startx,stopx,stepx,currenty,yindex,noofxpoints,nameoffset):
		#
		# Threaded readout of files 
		#
		currentpoint=1
		self.mcaList=[]
		self.pointTime=[]
		while(currentpoint!=noofxpoints+1):
			print 'current point',currentpoint,noofxpoints+1
			while(self.das.sendCommand("tfg read frame")<(2+currentpoint*2)):
				print 'sleep 1'
				sleep(1.0)
			print 'read scalar'
			scalerTimeData=self.readScalarData(currentpoint)[3]
			timesum=0.0
			print 'time sum'
			for i in range(len(scalerTimeData)):
				timesum=timesum+scalerTimeData[i]
			timesum=12.5E-6*timesum/9.0
			self.pointTime.append(timesum)
			print 'write point'
			files=self.writeDetectorPointFile(yindex,currentpoint,nameoffset)
			currentpoint=currentpoint+1




	#
	# Write the mca and scaler data out at frame xindex and set the name using the yindex and xindex information
	#
	def writeDetectorPointFile(self, yindex,xindex,nameoffset):
		name = "%s_yindex_%d_xindex_%d.xsp" % (self.mcarootname,yindex,xindex+nameoffset-1)
		sname = "%s_yindex_%d_xindex_%d_scalar.xsp" % (self.mcarootname,yindex,xindex+nameoffset-1)
		self.mcaList.append(name)
		command = "read 0 0 %d 4096 9 1 from 0 to-local-file \"%s\" raw" % (xindex, name)
		self.das.sendCommand(command)
		command = "read 0 0 %d 4 9 1 from 1 to-local-file \"%s\" raw intel" % (xindex, sname)
		self.das.sendCommand(command)
#		self.archiveFileList.append(name)
#        self.archiveFileList.append(sname)
		return [name,sname]


	#==============================================================
	# Read the scaler data from memory
	#==============================================================
	def readScalarDataNoRetry(self,point):
		scalarData=[]
		scalarstring=''
		command = "read 0 0 %d 4 9 1 from 1" % (point)
		scalarString=self.das.getData(command)
		if scalarString =="" :
			time.sleep(1)
			scalarString=self.das.getData(command)
		try:
			for j in range(4):
				scalarData.append(range(9))
			k=0
			for i in range(9):
				for j in range(4):
					scalarData[j][i]=int(scalarString[k])
					k=k+1
			return scalarData
		except:
			type, exception, traceback = sys.exc_info()
			self.readError = self.readError + 1
			self.readErrorList.append(point)
			handle_messages.log(None,"Error in readScalarDataNoRetry - scalarString = " + `scalarString` + " readErrorList = " + `self.readErrorList`, type, exception, None, True)

	#
	# VN routine to read scalar data
	# 
	def readScalarData(self,point):
		try:
			data = self.readScalarDataNoRetry(point)
			return data
		except:
			type, exception, traceback = sys.exc_info()
			handle_messages.log(None,"Error in readScalarData - retrying", type, exception, traceback, False)
		try:
			return self.readScalarDataNoRetry(point)
		except:
			type, exception, traceback = sys.exc_info()
			handle_messages.log(None,"Error in readScalarData - Giving up after 4 retries, returning zeroes", type, exception, traceback, False)
			scalarData=[]
			for j in range(4):
				scalarData.append(range(9))
				for i in range(9):
					for j in range(4):
						scalarData[j][i]=0                    
			return scalarData

    #====================================================
    #
    # Write out the data
    #
    #====================================================
	def writeSummary(self,currenty,yindex,startx,stepx,nx,offset):
		# lets window this mofo
		fid = open(self.datafilename,'a')
		for i in range(nx):
			val=(startx+(i*stepx))
			#print 'ic data again',i,self.ionchamberData,self.pointTime,self.mcaList
			line=str(val)+"\t"+str(currenty)+"\t"+str(self.pointTime[i])+"\t"+str(self.ionchamberData[0][i])+"\t"+str(self.ionchamberData[1][i])+"\t"+str(self.ionchamberData[2][i])+"\t"+str(self.mcaList[i])
			print >> fid,line
			print (startx+(i*stepx)),currenty,self.pointTime[i],self.ionchamberData[0][i],self.ionchamberData[1][i],self.ionchamberData[2][i],self.mcaList[i]
			# SDP Stuff
			detectorVector = Vector()
			detectorVector.add([self.ionchamberData[0][i],self.ionchamberData[1][i],self.ionchamberData[2][i]])
			detectorVector.add(self.mcaList[i])
			positionVector = Vector()
			positionVector.add(str(startx+(i*stepx)))
			positionVector.add(str(currenty))
			positionVector.add(str(self.pointTime[i]))
			sdp = ScanDataPoint("MicroFocus StepMap",self.scannableNamesVector,self.detectorNamesVector,None,None,None,None,positionVector,detectorVector,None,"Panel Name","I18 Custom SDP","Header String",str(self.mcaList[0]),0)
			sdp.setScanIdentifier(str(self.fileno))
			self.controller.update(None, sdp)
			print 'Reading and windowing:',self.mcaList[i]
			frameData=Xspress2Utilities.interpretDataFile(self.mcaList[i],0)
			windowsums=[0.0]*len(self.windowName)
			for j in range(len(self.windowName)):
				totalw=0.0
				windowedData=[0.0]*9
				for k in range(9):
					sumgrades=frameData[k]
					windowedData[k]=windowedData[k]+self.windowData(sumgrades,self.windowValues[j][k][0],self.windowValues[j][k][1])
				for k in range(9):
					totalw=totalw+windowedData[k]
				#
				# now set the data arrays with these values
				#
				windowsums[j]=totalw
			print 'writing windowed data',windowsums,len(self.windowName)
			self.appendToRGB(i,yindex,self.pointTime[i],self.ionchamberData,windowsums)
		fid.close()


	#====================================================
	#
	#  Window the data
	#
	#====================================================
	def windowData(self,data,startw,endw):
		#print 'HERE!!',startw,endw	
		sum=0.0    
		for i in range(startw,endw):
			sum=sum+data[i]
		return sum    


	def setupGUI(xstart,xend,xstep,ystart,yend,ystep,collectionTime):
		global mapRunning
		# print command_server.getScriptStatus()
		while(mapRunning):
			sleep(5)
		mapRunning = 1
		scandata=Vector()
		# Type of scan
		scandata.add("MapScan")
		continuous = Boolean(1)
		fluscan  =Boolean(1)
		detectorToUse = gda.gui.microfocus.i18.I18MicroFocusPanel.XSPRESS
		scanstring = str(xstart) + " "+ str(xstep) + " "+str(xend)+" "+str(ystart) + " "+str(ystep)+ " "+ str(yend) + " "+str(collectionTime) +" " + str(continuous)  + " "+ str(fluscan)
		scandata.add(scanstring)
		scandata.add(detectorToUse)
		controller = finder.find("MicroFocusController")
		controller.update(None,scandata)

	setupGUI = staticmethod(setupGUI)
