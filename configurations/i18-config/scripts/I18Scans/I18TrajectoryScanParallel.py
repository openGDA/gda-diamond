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
from gda.scan import EpicsTrajectoryScanController
from gda.scan import  Trajectory
import os
class I18ContinuousMapClass(ScriptBase):
	
	def __init__(self, datafileNo="default"):
		print "constructor"
		self.scannableNamesVector=Vector()
		self.scannableNamesVector.add(MicroFocusSampleX)
		self.scannableNamesVector.add(MicroFocusSampleY)
		self.detectorNamesVector=Vector()
		self.detectorNamesVector.add(counterTimer01)
		self.detectorNamesVector.add(finder.find("mapdetector"))
		# Find the script controller 
		self.controller = finder.find("MicroFocusController")	
		#
		self.xmotor=finder.find("sample_x_motor")
		self.tracController = finder.find("epicsTrajectoryScanController")
		self.trajectory = Trajectory()
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
		self.setWindows('/dls_sw/i18/software/gda/config/default.scas')
		self.setDetectorForExternalTrigger(1)

	def rastermapscan(self,startx,stopx,nxsteps,rowtime,starty,stopy, nysteps):
		lock =0
		try:
			scanStart = time.asctime()
			print 'locking express'
			#lock  = self.xspress.tryLock(5,java.util.concurrent.TimeUnit.SECONDS)
			print "the lock value is " + str(lock)
		   # if not lock:
			   # print "Xspress detector is already locked"
			   # self.controller.update(None, "STOP")
			   # return
			self.checkForInterrupt()
			ystepSize = (stopy - starty)/nysteps
			ymoveto = starty
			## build the trajectory
			self.tracController.setM1Move(0)
			self.tracController.setM2Move(0)
			self.tracController.setM3Move(0)
			self.tracController.setM4Move(0)
			self.tracController.setM5Move(0)
			self.tracController.setM6Move(0)
			self.tracController.setM7Move(0)
			self.tracController.setM8Move(0)
				
			##set the x motor to move
			self.tracController.setM3Move(1)
			self.trajectory.setTotalElementNumber(nxsteps)
			self.trajectory.setTotalPulseNumber(nxsteps)
			path = self.trajectory.defineCVPath(startx, stopx, rowtime)
			print "the total pulses is " + str(self.trajectory.getPulseNumbers())
			print "the total traj elements " + str(self.trajectory.getElementNumbers())
			print "the traj path is " + str(len(path))
			print path
			self.tracController.setM3Traj(path)
			
			self.tracController.setNumberOfElements((int)(self.trajectory.getElementNumbers()))
			self.tracController.setNumberOfPulses((int) (self.trajectory.getPulseNumbers()))
			self.tracController.setStartPulseElement((int) (self.trajectory.getStartPulseElement()))
			self.tracController.setStopPulseElement((int) (self.trajectory.getStopPulseElement()))
		
			if (self.tracController.getStopPulseElement() != (int) (self.trajectory.getStopPulseElement())): 
				self.tracController.setStopPulseElement((int) (self.trajectory.getStopPulseElement()))		  
			self.tracController.setTime((self.trajectory.getTotalTime()))
		   
			
			self.tracController.build()
			while(self.tracController.getBuild() != 0):
				##wait for the build to finsih
				sleep(0.5)
			##check the build status from epics
			if(self.tracController.getBuildStatusFromEpics() != 1):
				print "Unable to buld the trajectory"
				##abort the ccan if the build failed
				self.controller.update(None, "STOP")
				return
			#return
			for i in range(nysteps):
				self.ymotor.moveTo(ymoveto)
				self.checkForInterrupt()
				##prepare the detectors for collecting per row
				self.prepareDetectorForRow(nxsteps, (rowtime )/nxsteps)
				##execute the trajectory and wait for it to finish
				self.tracController.execute()
				while (self.tracController.getExecute() != 0): 
					self.checkForInterrupt()
					sleep(1.0)
				
				##check the exceute status
				if(self.tracController.getExecuteStatusFromEpics() != 1):
					print "Error while executing the trajectory"
					self.controller.update(None, "STOP")
			   
				## start the read  of actual trajectory path from the controller
				self.tracController.read()
				while (self.tracController.getRead() != 0): 
					self.checkForInterrupt()
					sleep(1.0)
				###check the read status from the controller
				if (self.tracController.getReadStatusFromEpics() != 1):
					print "Error while reading the actual trajectory path"
					self.controller.update(None, "STOP")
				actualPulses = self.tracController.getActualPulses()
				##get the actual xpositions
				xpositions = self.tracController.getM3Actual()
				##write the data from the detector
				nameoffset= []
				xposLen = len(xpositions)
				print "the actual number of pulses is " + str(actualPulses)
				print "actual x positions are " 
				print xposLen
				print str(xpositions[0]) + " " + str(xpositions[xposLen -1]) + " " +str(xpositions[nxsteps -1])
				##write the detector files for a row . can be done in a thread
				counterTimer01.stop()
				self.writeDetectorFiles(i, nxsteps)
				##for recording the data xposiitons should start from the xstart point
				realx = [startx, ]				
				for x in xpositions:
					realx.append(x)
				sdpStorage = ScanDataPointStorage(actualPulses)
				executor = java.util.concurrent.Executors.newFixedThreadPool(10)
				for execIndex in range(actualPulses):
					executor.execute(DetectorReader(execIndex, realx[execIndex], i,ymoveto,self.mcaList[execIndex],execIndex, sdpStorage,self.mcarootname, self.datafilename))
				executor.shutdown()
				executor.awaitTermination(long(100.0), java.util.concurrent.TimeUnit.SECONDS)
				self.writeDataFile(sdpStorage.getSDPStorage(), actualPulses)
				##at the end of the row increment ymoveto position
				ymoveto  = ymoveto + ystepSize
			scanEnd = time.asctime()
			print "scan start time ", scanStart
			print "scan end time ", scanEnd
			self.controller.update(None, "STOP")
		finally:
			if(lock):
				print 'unlocking xpress'
				self.xspress.unlock()
				
			
		print "scan"
		
  #====================================================
	#
	# Prepare the detector and tfg
	# Detector memory is wiped
	# Then  
	#
	#====================================================
	def prepareDetectorForRow(self,noOfFrames,collectionTime):
		self.das.sendCommand("disable 0")
		self.das.sendCommand("clear 0")
		self.das.sendCommand("enable 0")
		self.setupTFGForRow(noOfFrames,collectionTime)


	#==================================================
	#
	# Produces the tfg setup-groups used for kscans
	# In kscans you may want a time increase from start to finish
	# This method produces a series of individual tfg time frames for each time step in the scan
	#==================================================
	def setupTFGForRow(self,noOfFrames,collectionTime):
		counterTimer01.clearFrameSets()
		deadTime=1.0e-3
		counterTimer01.addFrameSet(noOfFrames,deadTime,collectionTime,0,7,0,8)
		counterTimer01.loadFrameSets()	
		counterTimer01.start()
	def writeDetectorFiles(self,yindex,nx):
		self.das.sendCommand("disable 0")
		for i in range(nx):
			name = "%s_yindex_%d_xindex_%d.xsp" % (self.mcarootname,yindex,i)
			sname = "%s_yindex_%d_xindex_%d_scalar.xsp" % (self.mcarootname,yindex,i)
			self.mcaList.append(name)
			command = "read 0 0 %d 4096 9 1 from 0 to-local-file \"%s\" raw" % ( i, name)
			self.das.sendCommand(command)
			command = "read 0 0 %d 4 9 1 from 1 to-local-file \"%s\" raw intel" % ( i, sname)
			self.das.sendCommand(command)
	

	def writeDataFile(self, sdpDict, nxPoints):
		fid = open(self.datafilename, 'a')
		for i in range(nxPoints):
			sdp = sdpDict.get(i)
			detectorVector = sdp.getDetectorData()
			ionData = detectorVector[0]
			line = str(val) + "\t" + str(currenty) + "\t" + str(pointTime) + "\t" + str(ionchamberData[1]) + "\t" + str(ionchamberData[2]) + "\t" + str(ionchamberData[3]) + "\t" + str(self.mcaList[i])
			print >> fid, line
			self.controller.update(None, sdp)
		fid.close()
			
		

	def writeSummary(self,currenty,yindex,xpositions, nxpoints):
		# lets window this mofo
		fid = open(self.datafilename,'a')
		print "actual x points is " + str(len(xpositions))
		for i in range(nxpoints):
			ionchamberData=counterTimer01.readFrame(0,4,i)
			val=xpositions[i]
			print 'ic data again',i,ionchamberData,self.mcaList
			##tfg read in 10ns blocks , converting to milli seconds
			pointTime = ionchamberData[0] * 10e-06
			line=str(val)+"\t"+str(currenty)+"\t"+str(pointTime)+"\t"+str(ionchamberData[1])+"\t"+str(ionchamberData[2])+"\t"+str(ionchamberData[3])+"\t"+str(self.mcaList[i])
			print >> fid,line
			
			print (val),currenty,pointTime,ionchamberData[1],ionchamberData[2],ionchamberData[3],self.mcaList[i]
			# SDP Stuff
			detectorVector = Vector()
			detectorVector.add([ionchamberData[1],ionchamberData[2],ionchamberData[3]])
			detectorVector.add(self.mcaList[i])
			positionVector = Vector()
			positionVector.add(str(val))
			positionVector.add(str(currenty))
			positionVector.add(str(pointTime))
			#sdp = ScanDataPoint("MicroFocus StepMap",self.scannableNamesVector,self.detectorNamesVector,None,None,None,None,positionVector,detectorVector,None,"Panel Name","I18 Custom SDP","Header String",str(self.mcaList[0]),0)
			sdp = ScanDataPoint()
			sdp.setUniqueName("MicroFocus StepMap")
			for s in self.scannableNamesVector:
				sdp.addScannable(s)
			for d in self.detectorNamesVector:
				sdp.addDetector(d)
			for p in positionVector:
				sdp.addScannablePosition(p,["%.4f"] )
			sdp.addDetectorData(ionchamberData,["%5.2g","%5.2g","%5.2g"])
			sdp.addDetectorData(self.mcaList[i],["%s"] )
			sdp.setCurrentFilename(self.datafilename)
			sdp.setScanIdentifier(str(self.fileno))
			sdp.setScanIdentifier(str(self.fileno))
			self.controller.update(None, sdp)
			mcafileIndex =  i+ (yindex *nxpoints)
			print 'Reading and windowing:',self.mcaList[mcafileIndex]
			frameData=Xspress2Utilities.interpretDataFile(self.mcaList[mcafileIndex],0)
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
			
	def windowData(self,data,startw,endw):
		#print 'HERE!!',startw,endw	
		sum=0.0	
		for i in range(startw,endw):
			sum=sum+data[i]
		return sum	
			
	#====================================================
	#
	#  Checks to see if stop has been pressed and trys to nicely stop the script
	#
	#====================================================
	def checkForInterrupt(self):
		
		if(self.interrupted):
			print 'Stopping map:Writing out data taken'
			# write the data we have so far and return
			#self.stopDetector()	
			resetMicroFocusPanel()
			self.interrupted=Boolean(0)
			self.paused=Boolean(0)
			self.xmotor.stop()
			self.ymotor.stop()
			JythonServerFacade.getInstance().setScriptStatus(Jython.IDLE)
			print  'Now the nasty bit: throw an exception to stop running'
			self.controller.update(None, "STOP")
			raise lang.InterruptedException()

	def setDetectorForExternalTrigger(self, trigger):
		if(trigger == 1):
			self.das.sendCommand("tfg setup-trig start ttl0")
			finder.find("tfg").setAttribute("Ext-Start", trigger == 1)
		else:
			finder.find("tfg").setAttribute("Ext-Start", trigger == 1)


class DetectorReader(java.lang.Runnable):
	def __init__(self, xindex, xposition, yindex, yposition, mcaFileName, pointNumber, sorter, mcarootname, datafilename):
		self.xindex = xindex
		self.xposition = xposition
		self.yindex = yindex
		self.yposition = yposition
		self.mcarootname = mcarootname
		self.datafilename = datafilename
		self.pointNumber = pointNumber
		self.mcaFileName = mcaFileName
		self.sorter = sorter
	def run(self):
		self.writePointSummary(self.yposition, self.yindex, self.xposition, self.xindex)
	def writePointSummary(self, currenty, yindex, xposition, xindex, nxpoints):
		
		ionchamberData = counterTimer01.readFrame(0, 4, xindex)
		val = xposition
		print 'ic data again', xindex, ionchamberData, self.mcaFileName
		##tfg read in 10ns blocks , converting to milli seconds
		pointTime = ionchamberData[0] * 10e-06
		line = str(val) + "\t" + str(currenty) + "\t" + str(pointTime) + "\t" + str(ionchamberData[1]) + "\t" + str(ionchamberData[2]) + "\t" + str(ionchamberData[3]) + "\t" + str(self.mcaFileName)
				
		print (val), currenty, pointTime, ionchamberData[1], ionchamberData[2], ionchamberData[3], self.mcaFileName
		# SDP Stuff
		detectorVector = Vector()
		detectorVector.add([ionchamberData[1], ionchamberData[2], ionchamberData[3]])
		detectorVector.add(self.mcaFileName)
		positionVector = Vector()
		positionVector.add(str(val))
		positionVector.add(str(currenty))
		positionVector.add(str(pointTime))
		#sdp = ScanDataPoint("MicroFocus StepMap",self.scannableNamesVector,self.detectorNamesVector,None,None,None,None,positionVector,detectorVector,None,"Panel Name","I18 Custom SDP","Header String",str(self.mcaList[0]),0)
		sdp = ScanDataPoint()
		sdp.setScanIdentifier("MicroFocus StepMap")
		sdp.setUniqueName(str(self.fileno))
		for s in self.scannableNamesVector:
			sdp.addScannable(s)
		for d in self.detectorNamesVector:
			sdp.addDetector(d)
		for p in positionVector:
			sdp.addScannablePosition(p, ["%.4f"])
		ionchamberData = ionchamberData[1:]
		sdp.addDetectorData(ionchamberData, ["%5.2g", "%5.2g", "%5.2g"])
		sdp.addDetectorData(self.mcaFileName, ["%s"])
		sdp.setCurrentFilename(self.datafilename)
		mcafileIndex = xindex + (yindex * nxpoints)
		sdp.setCurrentPointNumber(mcafileIndex)
		##self.controller.update(None, sdp)
		self.sorter.register(self.pointNumber, sdp)		
		print 'Reading and windowing:', self.mcaFileName
		frameData = Xspress2Utilities.interpretDataFile(self.mcaFileName, 0)
		windowsums = [0.0] * len(self.windowName)
		for j in range(len(self.windowName)):
			totalw = 0.0
			windowedData = [0.0] * 9
			for k in range(9):
				sumgrades = frameData[k]
				windowedData[k] = windowedData[k] + self.windowData(sumgrades, self.windowValues[j][k][0], self.windowValues[j][k][1])
			for k in range(9):
				totalw = totalw + windowedData[k]
			#
			# now set the data arrays with these values
			#
			windowsums[j] = totalw
		print 'writing windowed data', windowsums, len(self.windowName)
	
		
class ScanDataPointStorage():
	def __init__(self, noOfPoints):
		self.totalPoints = noOfPoints
		self.sdpDict={}
	def register(self, pointIndex, sdp):
		self.sdpDict[pointIndex] = sdp
		#self.tryUpdatingListeners()
	def getSDPStorage(self):
		return self.sdpDict