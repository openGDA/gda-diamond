from gda.epics import CAClient
from java.lang import *
from gda.jython.scannable import ScannableBase
from gda.jython.scannable import Scannable
from org.python.modules.math import *
from gda.device.xspress import Xspress2Utilities
from gda.jython import ScriptBase
from time import sleep
from java.lang import *
from java.util import Calendar
from gda.data import NumTracker
from gda.jython import JythonServerFacade
from gda.jython import Jython
import gda.configuration.properties.LocalProperties
from gda.scan import ScanDataPoint
from java.io import DataInputStream
from java.io import FileInputStream
import os
import jarray

#
#  EXAFS SCAN
# run SlaveCounterTimer.py
# run I18ExafsClass.py
#
# This doesn't plot data, it just collects it. ion chambers and flu detector are synched via the tfg and adc.
#
#   Example of a full Pb scan
#
##stepScan=MultiRegionScan();stepScan.addScan(I18GridScan(comboDCM,8824.0,8739.460869565219,-3.8608695652174387,1000.0,"mDeg", #java.lang.Boolean(0)));stepScan.addScan(I18GridScan(comboDCM,8735.599999999999,8698.5,-0.6999999999999865,1000.0,"mDeg", #java.lang.Boolean(0)));stepScan.addScan(KScan(comboDCM,3.0,12.0,0.04,1000.0,1000.0,3,13.039848732586526,6.271000000000002));stepScan.getDataWriter().setHeader(scanheader);stepScan.run();
# Create the class
#	myscan=I18ExafsScanClass()
# Set the windows you want to use: defaults are ALL 0-4095
#	myscan.setWindows('/home/i18user/i18windows.windows','Pblalpha1')
# do and angle scan with the values from the configure button in the exafs panel
#
#	myscan.anglescan(8824.0,8739.460869565219,-3.8608695652174387,1000.0)
#
# do next angle scan
#
#	myscan.anglescan(8735.599999999999,8698.5,-0.6999999999999865,1000.0)
#
# Now do the kscan with the values from the configure button in the exafs panel
#
#	myscan.kscan(3.0,12.0,0.04,1000.0,1000.0,3,13.039848732586526,6.271000000000002)
#
#
#   Files
#  Pb_angle1_windows.dat
#  Pb_angle2_windows.dat
#  Pb_kscan_windows.dat
#
class I18ExafsScanClass(ScriptBase):
	def __init__(self):
		self.das=finder.find("daserver")
		self.ionchambers=SlaveCounterTimer()
		# default collect all
		self.windowValues=[[0,4095]]*9
		self.windowName='ALL'
		self.ionchamberData=[]
		self.mcaList=[]
		self.scalarList=[]
		self.runs=NumTracker("tmp")
		self.runprefix='i18exafs'
		self.runext='.dat'
		self.fileno=self.runs.getCurrentFileNumber()+1
		self.runs.incrementNumber()
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
		self.facade=JythonServerFacade.getInstance()


		
	#
	#  Read in a window to be used on the mca files 
	#
	def setWindows(self,filename,desiredWindow):
		infile=open(filename,'r')
		tmpwindowValues=[[0,4095]]*9
		tmpwindowName=''
		while infile:
			a=infile.readline()	
			n = len(a)
			if n == 0:
				break
			temp=a.split('\t')
			tmpwindowName=temp[0].strip().replace(' ','')
			if(tmpwindowName.lower().find(desiredWindow.lower())>=0):
				for j in range(len(temp)-1):
					index=j+1
					mytemp=temp[index].strip().replace('[','').replace(']','').split(',')
					mytemp=[int(mytemp[0]),int(mytemp[1])]
					tmpwindowValues[j]=mytemp 
					print 'window values chosen :',j,tmpwindowValues[j]
				self.windowValues= tmpwindowValues
				self.windowName= tmpwindowName

	#
	# Performs an angle scan in step mode
	# 
	def anglescan(self,start,end,step,collectionTime):
		if(self.interrupted):
			return
		self.mcaList=[]
		self.ionchamberData=[]
		self.scalarList=[]
		# find no of points
		difference = end - start
		if (difference < 0 and step > 0):
			step = -step
		npoints = int(difference / step)
		currentpos=start
		# Check to see if a user has asked to pause the script
		self.checkForPauses()
		print 'Clearing and Preparing Detector'
		self.prepareDetectorForCollection(npoints,collectionTime/1000.0)
		if(self.interrupted):
			return
		# Set the collection time
		# make no of channels bigger than actual collection period
		#self.ionchambers.setCollectionTimeNew(collectionTime)
		self.ionchambers.setCollectionTime(collectionTime)
		# loop over npoints
		print 'Starting angle scan'
		print 'Mono\tI0\t It\t'
		for i in range(npoints):
			# Move mono to start position
			comboDCM.asynchronousMoveTo(currentpos)
			#dcm_mono.asynchronousMoveTo(currentpos)
			ScannableBase.waitForScannable(comboDCM)
			#ScannableBase.waitForScannable(dcm_mono)
			#sleep(1.0)
			# Ready the ion chambers
			self.ionchambers.clearAndPrepare()
			#
			# may not be needed if we are doing mono move as should be enough time for
			# adc to be set	
			#
			#
			# tfg starts paused so tell it to continue
			#
			self.das.sendCommand("tfg cont")
			#
			# wait until it is finished running
			#
			while (self.das.sendCommand("tfg read status") == 'RUNNING'):
				sleep(0.1)
				pass
			#print 'currentpos',currentpos,step
			# read out the ion chambers
			while(self.ionchambers.isBusy()>=1):
				sleep(0.1)
				pass
			#sleep(1.0)
			#self.ionchamberData.append(self.ionchambers.collectDataNew())
			self.ionchamberData.append(self.ionchambers.collectData())
			# print out some progress
			#print comboDCM.getPosition(),self.ionchamberData[i][0][0],self.ionchamberData[i][1][0],self.ionchamberData[i][2][0]
			#print dcm_mono.getPosition(),self.ionchamberData[i][0][0],self.ionchamberData[i][1][0],self.ionchamberData[i][2][0]
			#print dcm_mono.getPosition(),self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2]
			print comboDCM.getPosition(),self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2]
			# Check to see if a user has asked to pause or halt the script
			self.checkForAnglePauseOrInterrupt(i,start,end,step)
			# Move the mono
			currentpos=currentpos+step

		#
		#  write out
		#		
		self.stopDetector()	
		self.writeSummary(npoints,start,end,step)
		self.tag=self.tag+1
		print 'Finished angle scan'

	#
	# In a scan you create a new scan object for each scan
	# You can  reuse the i18exafs scan
	#  This simply increments the file no.s etc.
	#
	def reset(self):
		self.fileno=self.runs.getCurrentFileNumber()+1
		self.runs.incrementNumber()
		self.datadir=LocalProperties.get("gda.data.scan.datawriter.datadir")
		self.datafilename=self.datadir+'/'+str(self.fileno)+self.runext
		self.mcadir=self.datadir+'/mca/'+str(self.fileno)+'/'
		self.mcarootname=self.mcadir+str(self.fileno)
		if not os.path.isdir(self.mcadir):
			os.mkdir(self.mcadir)
		self.tag=1
		self.createFile()
		self.interrupted=Boolean(0)
		

	#
	# Performs a kscan in step mode
	# 
	def kscan(self,start,end,step,kStartTime,kEndTime,kWeighting, edgeEnergy, twoD):
		if(self.interrupted):
			return
		self.mcaList=[]
		self.ionchamberData=[]
		self.scalarList=[]
		# check that step is negative when moving downwards to stop
		difference = end - start
		if (difference < 0 and step > 0):
			step = -step
		npoints = int(difference / step)

		currentpos=start
		# prepare detector for collection
		print 'Clearing and Preparing Detector'
		self.prepareDetectorForKScan(start,step,end,kWeighting,kEndTime,kStartTime)
		# loop over npoints
		if(self.interrupted):
			return

		print 'Starting k scan'
		print 'Mono\tI0\t It\t'
		for i in range(npoints):
			mdegPosition = self.mDegForK(currentpos,edgeEnergy,twoD)
			secTime = self.timeForK(currentpos,start,end,kWeighting,kEndTime,kStartTime)
			# Set the collection time
			self.ionchambers.setCollectionTime(secTime)
			# Move mono to start position

			#dcm_mono.asynchronousMoveTo(mdegPosition)
			#ScannableBase.waitForScannable(dcm_mono)
			comboDCM.asynchronousMoveTo(mdegPosition)
			ScannableBase.waitForScannable(comboDCM)

			# Ready the ion chambers
			self.ionchambers.clearAndPrepare()
			#
			# tfg starts paused so tell it to continue
			#
			self.das.sendCommand("tfg cont")
			#
			# wait until it is finished running
			#
			while (self.das.sendCommand("tfg read status") == 'RUNNING'):
				sleep(0.1)
				pass
			while(self.ionchambers.isBusy()>=1):
				sleep(0.1)
				pass

			#sleep(1.0)
			#self.ionchamberData.append(self.ionchambers.collectDataNew())
			self.ionchamberData.append(self.ionchambers.collectData())
			# print out some progress
			#print mdegPosition,self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2]
			print mdegPosition,self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2]
			# Check to see if a user has asked to pause or halt the script
			self.checkForKScanPauseOrInterrupt(i,start,end,step,edgeEnergy, twoD)
			# Move the mono
			currentpos=currentpos+step
				
		#
		#  write out at end
		#		
		self.stopDetector()	
		self.writeKScanSummary(npoints,start,end,step,edgeEnergy, twoD)
		self.tag=self.tag+1
		print 'Finished k scan'

	#
	#  Disables, Clears and enables the detector
	#  Sets up tfg for a given noOfFrames and  collectionTime
	#  pausing in the dead frame and dead port=1 for adc triggering
	#  and finally starts the tfg which means it sits waiting for a software based continue command
	#
	def prepareDetectorForCollection(self,noOfFrames,collectionTime):
		self.das.sendCommand("disable 0")
		self.das.sendCommand("clear 0")
		self.das.sendCommand("enable 0")
		self.das.sendCommand("tfg init")
		command = "tfg setup-groups cycles 1 \n %d 0.01 %f 0 1 1 0 \n -1 0 0 0 0 0 0"  %(noOfFrames,collectionTime)
		#command = "tfg setup-groups cycles 1 \n %d 0.01 %f 1 0 1 0 \n -1 0 0 0 0 0 0"  %(noOfFrames,collectionTime)
		self.das.sendCommand(command)
		self.das.sendCommand("tfg start")
	#
	#  Disables, Clears and enables the detector
	#  Sets up tfg for a set of possibly variable length time frames
	#  and finally starts the tfg which means it sits waiting for a software based continue command
	#
	def prepareDetectorForKScan(self,start,step,end,kWeighting,kEndTime,kStartTime):
		self.das.sendCommand("disable 0")
		self.das.sendCommand("clear 0")
		self.das.sendCommand("enable 0")
		self.das.sendCommand("tfg init")
		self.das.sendCommand("tfg auto-cont 0")
		command = self.getTFGCommandForKScan(start,step,end,kWeighting,kEndTime,kStartTime)
		self.das.sendCommand(command)
		self.das.sendCommand("tfg start")
	#
	# Stop the tfg and disable the detector
	#
	def stopDetector(self):
		self.das.sendCommand("tfg init")
		self.das.sendCommand("disable 0")


	def writeDetectorFile(self,npoints):
		#self.das.sendCommand("disable 0")
		for i in range(npoints):
			name = "%s_scan_%d_index_%d.dat" % (self.mcarootname,self.tag,i)
			sname = "%s_scan_%d_index_%d_scalar.dat" % (self.mcarootname,self.tag,i)
			print 'Writing scan point',i,'to',name
			self.mcaList.append(name)
			self.scalarList.append(sname)
			command = "read 0 0 %d 4096 9 1 from 0 to-local-file \"%s\" raw intel" % ( i, name)
			self.das.sendCommand(command)
			command = "read 0 0 %d 9 2 1 from 1 to-local-file \"%s\" raw intel" % ( i, sname)
			self.das.sendCommand(command)


	def writeSummary(self,npoints,start,end,step):
		self.writeDetectorFile(npoints)
		# lets window this mofo
		fid = open(self.datafilename,'a')
		current=start
		for i in range(npoints):
			windowedData=[0.0]*9
			print 'Reading and windowing:',self.mcaList[i]
			frameData=Xspress2Utilities.interpretDataFile(self.mcaList[i],0)
			totalw=0.0	
			for j in range(9):
				sumgrades=frameData[j]
				windowedData[j]=windowedData[j]+self.windowData(sumgrades,self.windowValues[j][0],self.windowValues[j][1])
			for j in range(9):
				totalw=totalw+windowedData[j]

			#
			# now read scalar data
			# 
			scalarData=[] 
			for j in range(2):
				scalarData.append(range(9))
			fis =FileInputStream(self.scalarList[i])
			dis =DataInputStream(fis)
			scalerBytes =jarray.zeros(18*4,'b')
			dis.read(scalerBytes, 0, 18*4)
			offset = 0
			for j in range(2):
				for l in range(0,36,4):
					scalarData[j][l/4]= (0x000000FF & scalerBytes[offset+l+0]) + ((0x000000FF & scalerBytes[offset+l+1])<<8)+((0x000000FF & scalerBytes[offset+l+2])<<16)+((0x000000FF & scalerBytes[offset+l+3])<<24)
				offset=offset+36			
			print >>fid,current,comboDCM.calcEnergy(current/1000.0),self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2],str(windowedData[0:]).strip('[]').replace(',',''), \
				totalw,str(scalarData[0:1]).strip('[]').replace(',',''),str(scalarData[1:2]).strip('[]').replace(',', '')
			# pdq added for plotting
			current=current+step
		fid.close()

	def writeKScanSummary(self,npoints,start,end,step,edgeEnergy,twoD):
		self.writeDetectorFile(npoints)
		current=start
		# lets window this mofo
		fid = open(self.datafilename,'a')
		current=start
		for i in range(npoints):
			windowedData=[0.0]*9
			print 'Reading and windowing:',self.mcaList[i]
			frameData=Xspress2Utilities.interpretDataFile(self.mcaList[i].strip(),0)
			totalw=0.0
			for j in range(9):
				#sumgrades=Xspress2Utilities.sumGrades(frameData[j], 0, 15)
				sumgrades=frameData[j]
				windowedData[j]=windowedData[j]+self.windowData(sumgrades,self.windowValues[j][0],self.windowValues[j][1])
			for j in range(9):
				totalw=totalw+windowedData[j]
			#
			# now read scalar data
			# 
			scalarData=[] 
			for j in range(2):
				scalarData.append(range(9))
			fis =FileInputStream(self.scalarList[i])
			dis =DataInputStream(fis)
			scalerBytes =jarray.zeros(18*4,'b')
			dis.read(scalerBytes, 0, 18*4)
			offset = 0
			for j in range(2):
				for l in range(0,36,4):
					scalarData[j][l/4]= (0x000000FF & scalerBytes[offset+l+0]) + ((0x000000FF & scalerBytes[offset+l+1])<<8)+((0x000000FF & scalerBytes[offset+l+2])<<16)+((0x000000FF & scalerBytes[offset+l+3])<<24)
				offset=offset+36			
			print>>fid,self.mDegForK(current,edgeEnergy,twoD),comboDCM.calcEnergy(self.mDegForK(current,edgeEnergy,twoD)/1000.0),\
				self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2],str(windowedData[0:]).strip('[]').replace(',',''), \
				totalw,str(scalarData[0:1]).strip('[]').replace(',',''),str(scalarData[1:2]).strip('[]').replace(',', '')

			#print >> fid,self.mDegForK(current,edgeEnergy,twoD),self.ionchamberData[i][0],self.ionchamberData[i][1],self.mcaList[i],str(windowedData[0:]).strip('[]').replace(',', '')
			#print >> fid,self.mDegForK(current,edgeEnergy,twoD),self.ionchamberData[i][0][0],self.ionchamberData[i][1][0],self.ionchamberData[i][2][0],str(windowedData[0:]).strip('[]').replace(',', ''),totalw,totalw/self.ionchamberData[i][0][0]
			#print >> fid,self.mDegForK(current,edgeEnergy,twoD),self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2],str(windowedData[0:]).strip('[]').replace(',', ''),totalw
			current=current+step
		fid.close()

	def windowData(self,data,start,end):
		sum=0.0	
		for i in range(start,end):
			sum=sum+data[i]
		return sum						
	#
	# mDegForK converts k value (in inverse angstroms) to mDeg by using the java
	# Converter class.
	#
	def mDegForK(self,k,edgeEnergy,twoD):
		return gda.gui.exafs.Converter.convert(k,gda.gui.exafs.Converter.PERANGSTROM, gda.gui.exafs.Converter.MDEG,edgeEnergy, twoD)

	#
	# timeForK calculates the appropriate counting time for a particular k value
	# 
	def timeForK(self,k,start,end,kWeighting,kEndTime,kStartTime):
		a = Math.pow(k - start, kWeighting)
		b = Math.pow(end - start, kWeighting)
		c = (kEndTime - kStartTime)
		time = kStartTime + (a * c) / b
		# round to nearest 10milliseconds as this is all the ion chambers can collect in
		time=Math.round(time/10.0) * 10.0
		return time
	#
	#
	# Produces the tfg setup-groups used for kscans
	# In kscans you may want a time increase from start to finish
	# This method produces a series of individual tfg time frames for each time step in the scan
	#
	def getTFGCommandForKScan(self,start,step,end,kWeighting,kEndTime,kStartTime):
		difference = end - start;
		if (difference < 0 and step > 0):
			step = -step
		npoints = int(difference / step)
		currentpos = start
		tfglist="tfg setup-groups cycles 1\r\n"
		for  j in range(npoints+1):
			secTime = self.timeForK(currentpos,start,end,kWeighting,kEndTime,kStartTime)
			tfglist = tfglist + "1 0.01 %f 0 1 1 0\r\n" %(secTime/1000.0)
			currentpos = currentpos + step
		tfglist=tfglist+"-1 0 0 0 0 0 0\r\n"
		return tfglist

	#
	#
	# If a user presses the halt or stop button on the gui
	# stops the scan
	#
	# def checkForInterupts(self):
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
		line = " I18_EXAFS_RUN="+ str(self.fileno)+" "+ str(year)+" "+str(month)+" "+ str(day)+" "+str(hour)+" "+str(minute)+" "+str(second) + "\n"
		print>>fid,line
		print>>fid,'comboDCM energy I0 It drain flu1 flu2 flu3 flu4 flu5 flu6 flu7 flu8 flu9 flutot'
		fid.close()


	def checkForAnglePauseOrInterrupt(self,npoints,start,end,step):
		if(self.paused):
			JythonServerFacade.getInstance().setScriptStatus(Jython.PAUSED)
			while(self.paused):
				try:
					java.lang.Thread.sleep(250)
				except lang.InterruptedException:
					print 'Stopping angle scan:Writing out data taken'
					# write the data we have so far and return
					self.stopDetector()	
					self.writeSummary(npoints,start,end,step)
					self.interrupted=Boolean(0)
					self.paused=Boolean(0)
					JythonServerFacade.getInstance().setScriptStatus(Jython.IDLE)
					print  'Now the nasty bit: throw an exception to stop running'
					raise lang.InterruptedException()
					#JythonServerFacade.getInstance().haltCurrentScript()

		if(self.interrupted):
			print 'Stopping angle scan:Writing out data taken'
			# write the data we have so far and return
			self.stopDetector()	
			self.writeSummary(npoints,start,end,step)
			self.interrupted=Boolean(0)
			self.paused=Boolean(0)
			JythonServerFacade.getInstance().setScriptStatus(Jython.IDLE)
			print  'Now the nasty bit: throw an exception to stop running'
			raise lang.InterruptedException()


	def checkForKScanPauseOrInterrupt(self,npoints,start,end,step,edgeEnergy, twoD):
		if(self.paused):
			JythonServerFacade.getInstance().setScriptStatus(Jython.PAUSED)
			while(self.paused):
				try:
					java.lang.Thread.sleep(250)
				except lang.InterruptedException:
					print 'Stopping angle scan:Writing out data taken'
					# write the data we have so far and return
					self.stopDetector()	
					self.writeSummary(npoints,start,end,step)
					self.interrupted=Boolean(0)
					self.paused=Boolean(0)
					JythonServerFacade.getInstance().setScriptStatus(Jython.IDLE)
					print  'Now the nasty bit: throw an exception to stop running'
					raise lang.InterruptedException()
					#JythonServerFacade.getInstance().haltCurrentScript()

		if(self.interrupted):
			print 'Stopping angle scan:Writing out data taken'
			# write the data we have so far and return
			self.stopDetector()	
			self.writeSummary(npoints,start,end,step)
			self.interrupted=Boolean(0)
			self.paused=Boolean(0)
			JythonServerFacade.getInstance().setScriptStatus(Jython.IDLE)
			print  'Now the nasty bit: throw an exception to stop running'
			raise lang.InterruptedException()

