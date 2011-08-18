#@PydevCodeAnalysisIgnore
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
		self.scannableNamesVector = Vector()
		self.scannableNamesVector.add(MicroFocusSampleX)
		self.scannableNamesVector.add(MicroFocusSampleY)
		self.detectorNamesVector = Vector()
		self.detectorNamesVector.add(counterTimer01)
		self.detectorNamesVector.add(finder.find("mapdetector"))
		# Find the script controller 
		self.controller = finder.find("MicroFocusController")	
		#
		self.xmotor = finder.find("sample_x_motor")
		self.tracController = finder.find("epicsTrajectoryScanController")
		self.trajectory = Trajectory()
		self.ymotor = MicroFocusSampleY
		self.das = finder.find("daserver")
		self.mcaList = []
		self.pointTime = []
		self.ionchambers = ionChambers
		self.ionchamberData = []
		# Windowing data
		self.windowValues = []
		self.windowName = []
		self.windowArrays = []
			  
		if(datafileNo == "default"):
			self.runs = NumTracker("tmp")
			self.fileno = self.runs.getCurrentFileNumber() + 1
			self.runs.incrementNumber()
		else:
			self.fileno = datafileNo
		self.runext = '.dat'
		self.datadir = LocalProperties.get("gda.data.scan.datawriter.datadir")
		self.datafilename = self.datadir + '/' + str(self.fileno) + self.runext
		
		#
		# Make a directory to store the mca files in
		#
		self.mcadir=self.datadir+'/mca/'+str(self.fileno)+'/'
		self.mca_row_dir=self.mcadir	
		self.mcarootname=self.mcadir+str(self.fileno)
		if not os.path.isdir(self.mcadir):
			os.mkdir(self.mcadir)
		self.tag = 1
		self.createFile()
		# Set default windows
		self.setWindows('/dls_sw/i18/software/gda/config/default.scas')
		self.setDetectorForExternalTrigger(1)
		self.ionchamberData=[]

	def rastermapscan(self, startx, stopx, nxsteps, rowtime, starty, stopy, nysteps):
		lock = 0
		global mapRunning
		mapRunning = 1
		try:
			scanStart = time.asctime()
			print 'locking express'
			#lock  = self.xspress.tryLock(5,java.util.concurrent.TimeUnit.SECONDS)
			print "the lock value is " + str(lock)
		   # if not lock:
			   # print "Xspress detector is already locked"
			   # self.controller.update(None, "STOP")
			   # return
			totalPoints = nxsteps * nysteps
			self.checkForInterrupt()
			ystepSize = abs(stopy - starty) / (nysteps - 1)
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
				# Row by row data output directory
				self.mca_row_dir=self.mcadir+("row%d/" %i)
				if not os.path.isdir(self.mca_row_dir):
					os.mkdir(self.mca_row_dir)
				self.mcarootname=self.mca_row_dir+str(self.fileno)
				while(BeamMonitor.beamOn() == 0):
					print 'Beam lost : Pausing until resumed'
					try:
						sleep(60)
					except:
						self.interrupted = 1	
					self.checkForInterrupt()
					#
					# Check if detector is filling
					#
				while(BeamMonitor.isFilling() == 1):
				#while(False):
					self.checkForInterrupt()
					print 'Detector Filling : Pausing until completed'
					try:
						sleep(60)
					except:
						self.interrupted = 1					
						self.checkForInterrupt()
				self.ymotor.moveTo(ymoveto)
				self.checkForInterrupt()
				##prepare the detectors for collecting per row
				self.prepareDetectorForRow(nxsteps, (rowtime) / nxsteps)
				##execute the trajectory and wait for it to finish
				approximateX = self.calculateXpositions(startx,stopx,nxsteps)
				timePerPoint = rowtime/nxsteps
				self.tracController.execute()
				xread =0
				sleep(5)
				while (self.tracController.getExecute() != 0): 					
					if(xread == 0):
						sleep(timePerPoint)
						for x in range(nxsteps):	
							sleep(timePerPoint)	
							self.writeDetectorFile(i,x)
							self.updatePointSummary(ymoveto,i, approximateX[x], x, nxsteps)
							self.checkForInterrupt()
					self.checkForInterrupt()
					xread = 1
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
				nameoffset = []
				xposLen = len(xpositions)
				print "the actual number of pulses is " + str(actualPulses)
				print "actual x positions are " 
				print xposLen
				print str(xpositions[0]) + " " + str(xpositions[xposLen - 1]) + " " + str(xpositions[nxsteps - 1])
				##write the detector files for a row . can be done in a thread
				counterTimer01.stop()
				##for recording the data xposiitons should start from the xstart point
				realx = [startx, ]				
				for x in xpositions:
					realx.append(x)
				self.writeSummary(ymoveto, i, realx, actualPulses)
			  
				##at the end of the row increment ymoveto position
				ymoveto = ymoveto + ystepSize
			scanEnd = time.asctime()
			print "scan start time ", scanStart
			print "scan end time ", scanEnd
			self.controller.update(None, "STOP")
		finally:
			self.setDetectorForExternalTrigger(0)
			mapRunning = 0
			if(lock):
				print 'unlocking xpress'
				self.xspress.unlock()
				
			
		print "scan"
		
	def calculateXpositions(self, startx, stopx, nxsteps):
	   approximateX = []
	   stepX = (stopx - startx) / nxsteps
	   for i in range(nxsteps):
	   	   approximateX.append(startx + (i * stepX))
	   return approximateX

  #====================================================
	#
	# Prepare the detector and tfg
	# Detector memory is wiped
	# Then  
	#
	#====================================================
	def prepareDetectorForRow(self, noOfFrames, collectionTime):
		self.das.sendCommand("disable 0")
		self.das.sendCommand("clear 0")
		self.das.sendCommand("enable 0")
		self.setupTFGForRow(noOfFrames, collectionTime)


	#==================================================
	#
	# Produces the tfg setup-groups used for kscans
	# In kscans you may want a time increase from start to finish
	# This method produces a series of individual tfg time frames for each time step in the scan
	#==================================================
	def setupTFGForRow(self, noOfFrames, collectionTime):
		counterTimer01.clearFrameSets()
		deadTime = 1.0e-3
		print "setting the detector for "
		print str(noOfFrames) + "," + str(deadTime) + "," + str(collectionTime) + " " + "0,7,0,8"
		counterTimer01.addFrameSet(noOfFrames, deadTime, collectionTime, 0, 7, 0, 8)
		counterTimer01.loadFrameSets()	
		counterTimer01.start()
	def writeDetectorFiles(self, yindex, nx):
		self.das.sendCommand("disable 0")
		for i in range(nx):
			name = "%s_yindex_%d_xindex_%d.xsp" % (self.mcarootname, yindex, i)
			sname = "%s_yindex_%d_xindex_%d_scalar.xsp" % (self.mcarootname, yindex, i)
			self.mcaList.append(name)
			command = "read 0 0 %d 4096 9 1 from 0 to-local-file \"%s\" raw" % (i, name)
			self.das.sendCommand(command)
			command = "read 0 0 %d 4 9 1 from 1 to-local-file \"%s\" raw intel" % (i, sname)
			self.das.sendCommand(command)
			
	def writeDetectorFile(self, yindex, x):
		frame = counterTimer01.getCurrentFrame()
		print "current frame is ", frame
		while (frame != 0 and frame <= (x *2 + 1)):
			sleep(1.0)
			frame = counterTimer01.getCurrentFrame()
		name = "%s_yindex_%d_xindex_%d.xsp" % (self.mcarootname, yindex, x)
		sname = "%s_yindex_%d_xindex_%d_scalar.xsp" % (self.mcarootname, yindex, x)
		self.mcaList.append(name)
		##check to make sure the detector can write this frame by usinf command tfg read frame
		command = "read 0 0 %d 4096 9 1 from 0 to-local-file \"%s\" raw" % (x , name)
		self.das.sendCommand(command)
		command = "read 0 0 %d 4 9 1 from 1 to-local-file \"%s\" raw intel" % (x , sname)
		self.das.sendCommand(command)

	def updatePointSummary(self, currenty, yindex, currentx, xindex, nxpoints):
		self.ionchamberData.append(counterTimer01.readFrame(0, 4, xindex))
		mcafileIndex = xindex + (yindex * nxpoints)
		##tfg read in 10ns blocks , converting to milli seconds
		pointTime = self.ionchamberData[mcafileIndex][0] * 10e-06
		print currentx, currenty, pointTime, self.ionchamberData[mcafileIndex][1], self.ionchamberData[mcafileIndex][2], self.ionchamberData[mcafileIndex][3], self.mcaList[mcafileIndex]
		# SDP Stuff
		positionVector = Vector()
		positionVector.add(str(currentx))
		positionVector.add(str(currenty))
		sdp = ScanDataPoint()
		sdp.setScanIdentifier("MicroFocus StepMap")
		sdp.setUniqueName(str(self.fileno))
		for s in self.scannableNamesVector:
			sdp.addScannable(s)
		for d in self.detectorNamesVector:
			sdp.addDetector(d)
		for p in positionVector:
			sdp.addScannablePosition(p, ["%.4f"])
		ionData = self.ionchamberData[mcafileIndex][1:]
		sdp.addDetectorData(ionData, ["%5.2g", "%5.2g", "%5.2g"])
		sdp.addDetectorData(self.mcaList[mcafileIndex], ["%s"])
		sdp.setCurrentFilename(self.datafilename)
		sdp.setCurrentPointNumber(mcafileIndex)
		self.controller.update(None, sdp)
		
	def writeSummary(self, currenty, yindex, xpositions, nxpoints):
		# lets window this mofo
		fid = open(self.datafilename, 'a')
		print "actual x points is " + str(len(xpositions))
		for i in range(nxpoints):
			mcafileIndex = i + (yindex * nxpoints)
			val = xpositions[i]
			print 'ic data again', mcafileIndex, counterTimer01.readFrame(0, 4, i), self.mcaList[mcafileIndex]
			##tfg read in 10ns blocks , converting to milli seconds
			pointTime = self.ionchamberData[mcafileIndex][0] * 10e-06
			line = str(val) + "\t" + str(currenty) + "\t" + str(pointTime) + "\t" + str(self.ionchamberData[mcafileIndex][1]) + "\t" + str(self.ionchamberData[mcafileIndex][2]) + "\t" + str(self.ionchamberData[mcafileIndex][3]) + "\t" + str(self.mcaList[mcafileIndex])
			print >> fid, line			
		fid.close()
	#====================================================
	#
	# Creates an srs data file
	#
	#====================================================
	def createFile(self):
		fid = open(self.datafilename, 'w')
		# get datetime
		rightNow = Calendar.getInstance()
		year = rightNow.get(Calendar.YEAR)
		month = rightNow.get(Calendar.MONTH)
		day = rightNow.get(Calendar.DAY_OF_MONTH)
		hour = rightNow.get(Calendar.HOUR)
		minute = rightNow.get(Calendar.MINUTE)
		second = rightNow.get(Calendar.SECOND)
		print "Writing data to file:" + self.datafilename
		print "Writing mca file to:" + self.mcadir
		# write datetime
		line = ' &SRS'
		line = ' &END'
		print >> fid, line
		print >> fid, '   '
		print >> fid, '   '
		fid.close()
	#====================================================
	#
	#  Set the windows
	#
	#====================================================
	def setWindows(self, filename):
		infile = open(filename, 'r')
		while infile:
			a = infile.readline()
			if(a.find("IONCHAMBER") >= 0):
				continue	
			n = len(a)
			if n == 0:
				break
			temp = a.split('\t')
			tmpwindowValues = [[0, 4095]] * 9
			tmpwindowName = temp[0].strip().replace(' ', '')
			print 'window name', tmpwindowName
			for j in range(len(temp) - 1):
				index = j + 1
				mytemp = temp[index].strip().replace('[', '').replace(']', '').split(',')
				mytemp = [int(mytemp[0]), int(mytemp[1])]
				tmpwindowValues[j] = mytemp 
				print 'window values chosen :', j, tmpwindowValues[j]
			self.windowValues.append(tmpwindowValues)
			self.windowName.append(tmpwindowName)
			
	def windowData(self, data, startw, endw):
		#print 'HERE!!',startw,endw	
		sum = 0.0	
		for i in range(startw, endw):
			sum = sum + data[i]
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
			self.interrupted = Boolean(0)
			self.paused = Boolean(0)
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
		transscan  =Boolean(0)
		detectorToUse = gda.gui.microfocus.i18.I18MicroFocusPanel.XSPRESS
		scanstring = str(xstart) + " "+ str(xstep) + " "+str(xend)+" "+str(ystart) + " "+str(ystep)+ " "+ str(yend) + " "+str(collectionTime) +" " + str(continuous)  + " "+ str(transscan)
		scandata.add(scanstring)
		scandata.add(detectorToUse)
		controller = finder.find("MicroFocusController")
		controller.update(None,scandata)
	
	setupGUI = staticmethod(setupGUI)
