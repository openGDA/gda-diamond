from gda.epics import CAClient
from java.lang import *
from gda.device.scannable import ScannableBase
from gda.device import Scannable
from org.python.modules.math import *

from gda.jython import ScriptBase
from time import sleep

from java.util import Calendar
from gda.data import NumTracker
from gda.jython import JythonServerFacade
from gda.jython import JythonStatus
import gda.configuration.properties.LocalProperties
from gda.scan import ScanDataPoint
from java.io import DataInputStream
from java.io import FileInputStream
import os
import jarray
from java.util import Date
from java.text import SimpleDateFormat
from gda.jython import InterfaceProvider

# ========================================
# EXAFS SCAN
# run SlaveCounterTimer.py
# run I18ExafsClass.py
# run BeamMonitorClass.py
#
#	Example of a full Pb scan
#	myscan=I18ExafsScanClass()
#	myscan.setWindows('/home/i18user/i18windows.windows','Pblalpha1')
#	myscan.anglescan(8824.0,8739.460869565219,-3.8608695652174387,1000.0)
#	myscan.anglescan(8735.599999999999,8698.5,-0.6999999999999865,1000.0)
#	myscan.kscan(3.0,12.0,0.04,1000.0,1000.0,3,13.039848732586526,6.271000000000002)
#========================================
class I18ExafsScanClass(ScriptBase):
	def __init__(self,detectorList=None):
		# EXAFS PANEL CODE
		self.scannableNamesVector=Vector()
		self.scannableNamesVector.add("dcm_mono")
		self.detectorNamesVector=Vector()
		self.detectorNamesVector.add("counterTimer01")
		self.detectorNamesVector.add("counterTimer02") 
		self.controller = finder.find("ExafsController")
		self.mcontroller = finder.find("MicroFocusController")
		self.title="TITLE"
		self.condition1="CONDITION1"
		self.condition2="CONDITION2"
		self.condition3="CONDITION3"
		# Script code
		self.das=finder.find("daserver")
		self.ionchambers=SlaveCounterTimer()
		self.converter = finder.find("auto_mDeg_idGap_mm_converter")
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
		self.datadir=InterfaceProvider.getPathConstructor().createFromProperty("gda.data.scan.datawriter.datadir")
		self.datafilename=self.datadir+'/'+str(self.fileno)+self.runext
		if(detectorList!=None):
			self.detectorMask=detectorList
		else:
			self.detectorMask=[1,1,1,1,1,1,1,1,1]

		self.mcadir=self.datadir+'/mca/'+str(self.fileno)+'/'
		self.mcarootname=self.mcadir+str(self.fileno)
		if not os.path.isdir(self.mcadir):
			os.mkdir(self.mcadir)
		self.tag=1
		self.facade=JythonServerFacade.getInstance()
		self.scanList=[]
		self.noOfRepeats=1
		self.noOfPoints=0


	def addAngleScan(self,start,end,step,collectionTime):
		self.noOfPoints=self.noOfPoints+int((end-start)/step)
		self.scanList.append(['a',start,end,step,collectionTime])

	def addKScan(self,start,end,step,kStartTime,kEndTime,kWeighting, edgeEnergy, twoD):
		self.noOfPoints=self.noOfPoints+int((end-start)/step)
		self.scanList.append(['k',start,end,step,kStartTime,kEndTime,kWeighting, edgeEnergy, twoD])


	def setNoOfRepeats(self,repeats):
		self.noOfRepeats=repeats

	def startScan(self):
		#
		# Send repeat and point information to the GUI
		# then start the scan
		#
		self.setupGUI()
		for i in range(self.noOfRepeats):
			if(i>0):				
				self.incrementFilename()
			for j in range(len(self.scanList)):
				if(self.scanList[j][0]=='a'):
					self.anglescan(self.scanList[j][1],self.scanList[j][2],self.scanList[j][3],self.scanList[j][4])
				elif(self.scanList[j][0]=='k'):
					self.kscan(self.scanList[j][1],self.scanList[j][2],\
					self.scanList[j][3],self.scanList[j][4],self.scanList[j][5],self.scanList[j][6],self.scanList[j][7],self.scanList[j][8])
			self.incrementGUIRepeat()
	
	def setupGUI(self):
		scandata=Vector()
		# Type of scan
		scandata.add("FluScan")
		# No of Repeats
		# No of Points
		scandata.add(self.noOfPoints)
		scandata.add(self.noOfRepeats)
		self.controller.update(None,scandata)
		self.mcontroller.update(None,scandata)

	def incrementGUIRepeat(self):
		scandata=Vector()
		# Type of scan
		scandata.add("ScanComplete")
		self.controller.update(None,scandata)
		self.mcontroller.update(None,scandata)

						
		
	# ========================================
	#  Read in a window to be used on the mca files 
	# ========================================
	def setWindows(self,filename,desiredWindow):
		infile=open(filename,'r')
		tmpwindowValues=[[0,4095]]*9
		tmpwindowName=''
		while infile:
			# Read in the line file
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
		if(self.windowName=='ALL'):
			print '======================'
			print '========WARNING========'
			print 'No window has been found or set'
			print '======WARNING=========='
			print '======================'
			

	#==================================================
	# Performs an angle scan in step mode
	# ==================================================
	def anglescan(self,start,end,step,collectionTime):
		i=0
		self.createFile()
		# create some empty lists
		self.mcaList=[]
		self.ionchamberData=[]
		self.scalarList=[]
		# find no of points
		difference = end - start
		if (difference < 0 and step > 0):
			step = -step
		npoints = int(difference / step)
		# start position
		currentpos=start
		print 'Clearing and Preparing Detector'
		# set collection time
		self.prepareDetectorForCollection(npoints,collectionTime/1000.0)
		# Set the collection time
		self.ionchambers.setCollectionTime(collectionTime)
		# loop over npoints
		print 'Starting angle scan'
		print 'Bragg Energy Time I0 It Idrain'
		self.checkForAngleInterrupt(0,start,end,step,collectionTime)
		#print 'w1',w
		for i in range(npoints):
			#print 'w1',w
			self.checkForAnglePause(i,start,end,step,collectionTime)
			# Check beam is running
			while(BeamMonitor.beamOn()==0):
				self.checkForAngleInterrupt(i,start,end,step,collectionTime)
				print 'Beam lost : Pausing until resumed'
				try:
					sleep(60)
				except:
					self.interrupted=1					
				self.checkForAngleInterrupt(i,start,end,step,collectionTime)
			#print 'w2',w
			# Move mono to start position
			self.checkForAngleInterrupt(i,start,end,step,collectionTime)
			#print 'w3',w
			try:
				#print 'w4',w
				comboDCM_d.moveTo(currentpos)
				comboDCM_d.waitWhileBusy()
				self.converter.disableAutoConversion()
				#ScannableBase.waitForScannable(comboDCM)
				#print 'w5',w
			except:
				self.interrupted=1
				self.converter.enableAutoConversion()
			self.checkForAngleInterrupt(i,start,end,step,collectionTime)
			# Ready the ion chambers
			#print 'w5',w
			self.ionchambers.clearAndPrepare()
			#print 'w6',w
			self.checkForAngleInterrupt(i,start,end,step,collectionTime)
			# tfg starts paused so tell it to continue
			self.das.sendCommand("tfg cont")
			self.checkForAngleInterrupt(i,start,end,step,collectionTime)
			self.das.sendCommand("tfg wait timebar")
			self.checkForAngleInterrupt(i,start,end,step,collectionTime)
			# read out the ion chambers
			#print 'w7',w
			while(self.ionchambers.isBusy()>=1):
				self.checkForAngleInterrupt(i,start,end,step,collectionTime)
				try:
					sleep(0.05)
				except:
					self.interrupted=1
				pass
			#print 'w8',w
			self.ionchamberData.append(self.ionchambers.collectData())
			# print out some progress
			self.checkForAngleInterrupt(i,start,end,step,collectionTime)
			#print currentpos,comboDCM.calcEnergy(currentpos/1000.0),collectionTime,self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2]
			print currentpos,comboDCM_eV.getPosition(),collectionTime,self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2]
			# Move the mono
			#print 'w9',w
			currentpos=currentpos+step
			#  stop detector
		self.stopDetector()	
		# write out the data
		self.writeSummary(npoints,start,end,step,collectionTime)
		self.converter.enableAutoConversion()
		self.tag=self.tag+1
		print 'Finished angle scan'


	#==================================================
	# Performs a kscan in step mode
	# ==================================================
	def kscan(self,start,end,step,kStartTime,kEndTime,kWeighting, edgeEnergy, twoD):
		i=0
		#try:
		self.createFile()
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
		print 'Starting k scan'
		print 'Bragg Energy Time I0 It Idrain'
		self.checkForKScanInterrupt(0,start,end,step,edgeEnergy, twoD,kStartTime,kEndTime,kWeighting)
		for i in range(npoints):
			# Check for pause!
			self.checkForKScanPause(i,start,end,step,edgeEnergy, twoD,kStartTime,kEndTime,kWeighting)
			# Check beam is running
			while(BeamMonitor.beamOn()==0):
				print 'Beam lost : Pausing until resumed'
				self.checkForKScanInterrupt(i,start,end,step,edgeEnergy, twoD,kStartTime,kEndTime,kWeighting)
				try:
					sleep(60)
				except:
					self.interrupted=1
			mdegPosition = self.mDegForK(currentpos,edgeEnergy,twoD)
			secTime = self.timeForK(currentpos,start,end,kWeighting,kEndTime,kStartTime)
			self.checkForKScanInterrupt(i,start,end,step,edgeEnergy, twoD,kStartTime,kEndTime,kWeighting)
			# Set the collection time
			self.ionchambers.setCollectionTime(secTime)
			# Move mono to start position
			try:
				comboDCM_d.moveTo(mdegPosition)
				#comboDCM.waitWhileBusy()
				self.converter.disableAutoConversion()
				#ScannableBase.waitForScannable(comboDCM)
			except:
				self.interrupted=1
				self.converter.enableAutoConversion()
			self.checkForKScanInterrupt(i,start,end,step,edgeEnergy, twoD,kStartTime,kEndTime,kWeighting)
			# Ready the ion chambers
			self.ionchambers.clearAndPrepare()
			self.checkForKScanInterrupt(i,start,end,step,edgeEnergy, twoD,kStartTime,kEndTime,kWeighting)
			# tfg starts paused so tell it to continue
			self.das.sendCommand("tfg cont")
			self.checkForKScanInterrupt(i,start,end,step,edgeEnergy, twoD,kStartTime,kEndTime,kWeighting)
			self.das.sendCommand("tfg wait timebar")
			self.checkForKScanInterrupt(i,start,end,step,edgeEnergy, twoD,kStartTime,kEndTime,kWeighting)
			while(self.ionchambers.isBusy()>=1):
				self.checkForKScanInterrupt(i,start,end,step,edgeEnergy, twoD,kStartTime,kEndTime,kWeighting)
				try:
					sleep(0.05)
				except:
					self.interrupted=1
				pass
			self.ionchamberData.append(self.ionchambers.collectData())
			self.checkForKScanInterrupt(i,start,end,step,edgeEnergy, twoD,kStartTime,kEndTime,kWeighting)
			#print mdegPosition,comboDCM.calcEnergy(mdegPosition/1000.0),secTime,self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2]
			print mdegPosition,comboDCM_eV.getPosition(),secTime,self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2]
			# Move the mono
			currentpos=currentpos+step
			#  write out at end
		self.checkForKScanInterrupt(i,start,end,step,edgeEnergy, twoD,kStartTime,kEndTime,kWeighting)
		self.stopDetector()	
		self.checkForKScanInterrupt(i,start,end,step,edgeEnergy, twoD,kStartTime,kEndTime,kWeighting)
		self.converter.enableAutoConversion()
		self.writeKScanSummary(npoints,start,end,step,edgeEnergy, twoD,kStartTime,kEndTime,kWeighting)
		self.tag=self.tag+1
		print 'Finished k scan'

	#==================================================
	#  Disables, Clears and enables the detector
	#  Sets up tfg for a given noOfFrames and  collectionTime
	#  pausing in the dead frame and dead port=1 for adc triggering
	#  and finally starts the tfg which means it sits waiting for a software based continue command
	#==================================================
	def prepareDetectorForCollection(self,noOfFrames,collectionTime):
		self.das.sendCommand("disable 0")
		self.das.sendCommand("clear 0")
		self.das.sendCommand("enable 0")
		self.das.sendCommand("tfg init")
		command = "tfg setup-groups cycles 1 \n%d 0.01 %f 0 1 1 0 \n-1 0 0 0 0 0 0 "  %(noOfFrames,collectionTime)
		self.das.sendCommand(command)
		self.das.sendCommand("tfg start")

	#==================================================
	#  Disables, Clears and enables the detector
	#  Sets up tfg for a set of possibly variable length time frames
	#  and finally starts the tfg which means it sits waiting for a software based continue command
	#==================================================
	def prepareDetectorForKScan(self,start,step,end,kWeighting,kEndTime,kStartTime):
		self.das.sendCommand("disable 0")
		self.das.sendCommand("clear 0")
		self.das.sendCommand("enable 0")
		self.das.sendCommand("tfg init")
		self.das.sendCommand("tfg auto-cont 0")
		command = self.getTFGCommandForKScan(start,step,end,kWeighting,kEndTime,kStartTime)
		self.das.sendCommand(command)
		self.das.sendCommand("tfg start")

	#==================================================
	# Stop the tfg and disable the detector
	#==================================================
	def stopDetector(self):
		self.das.sendCommand("tfg init")
		self.das.sendCommand("disable 0")

	#==================================================
	# Write the detector data to files
	#==================================================
	def writeDetectorFile(self,npoints):
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

	#==================================================
	# Write the data to a file
	#==================================================
	def writeSummary(self,npoints,start,end,step,collectionTime):
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
				if(self.detectorMask[j]==1):
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
			fis.close()
			offset = 0
			for j in range(2):
				for l in range(0,36,4):
					scalarData[j][l/4]= (0x000000FF & scalerBytes[offset+l+0]) +\
					 ((0x000000FF & scalerBytes[offset+l+1])<<8)+\
					((0x000000FF & scalerBytes[offset+l+2])<<16)+((0x000000FF & scalerBytes[offset+l+3])<<24)
				offset=offset+36	

			liveTime=collectionTime/1000.0
			corrCounts=self.getCorrectedCounts(scalarData[0],scalarData[1],liveTime)
			measuredCounts=scalarData[0]
			relinCounts=self.reLinearizeCounts(corrCounts)
			factor=[]
			for j in range(len(relinCounts)):
				if(relinCounts[j]==0 or measuredCounts[j]==0):
					val=1
					factor.append(1.0)
				else:
					val = (relinCounts[j]/measuredCounts[j])
					factor.append(val*liveTime)
			correctWindows=[]
			corrWindTot=0.0
			for j in range(9):
				correctW=float(windowedData[j])*factor[j]
				corrWindTot=corrWindTot+correctW
				correctWindows.append(correctW)
			#print >>fid,current,comboDCM.calcEnergy(current/1000.0),collectionTime,self.ionchamberData[i][0],\
			#	self.ionchamberData[i][1],self.ionchamberData[i][2],str(windowedData[0:]).strip('[]').replace(',',''), \
			#	totalw,str(correctWindows[0:]).strip('[]').replace(',',''),corrWindTot
			print >>fid,current,comboDCM_eV.getPosition(),collectionTime,self.ionchamberData[i][0],\
				self.ionchamberData[i][1],self.ionchamberData[i][2],str(windowedData[0:]).strip('[]').replace(',',''), \
				totalw,str(correctWindows[0:]).strip('[]').replace(',',''),corrWindTot

			# pdq added for plotting
			current=current+step
			# SDP Stuff
			detectorVector = Vector()
			detectorVector.add(self.ionchamberData[i])
			detectorVector.add(windowedData)
			positionVector = Vector()
			positionVector.add(str(current))
			#sdp = ScanDataPoint("scan name",self.scannableNamesVector,self.detectorNamesVector,positionVector,detectorVector,"Panel Name","I18 Custom SDP","Header String",self.datafilename)
			sdp = ScanDataPoint("Exafs FluAngleScan",self.scannableNamesVector,self.detectorNamesVector,None,None,None,None,positionVector,detectorVector,None,"Panel Name","I18 Custom SDP","Header String",self.datafilename,0)
			self.controller.update(None, sdp)
			self.mcontroller.update(None, sdp)

		fid.close()
	#==================================================
	# Write the data to a file
	#==================================================
	def writeKScanSummary(self,npoints,start,end,step,edgeEnergy,twoD,kStartTime,kEndTime,kWeighting):
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
			fis.close()
			offset = 0
			for j in range(2):
				for l in range(0,36,4):
					scalarData[j][l/4]= (0x000000FF & scalerBytes[offset+l+0]) + ((0x000000FF & scalerBytes[offset+l+1])<<8)+((0x000000FF & scalerBytes[offset+l+2])<<16)+((0x000000FF & scalerBytes[offset+l+3])<<24)
				offset=offset+36	
			secTime = self.timeForK(current,start,end,kWeighting,kEndTime,kStartTime)		
			liveTime=secTime/1000.0
			corrCounts=self.getCorrectedCounts(scalarData[0],scalarData[1],liveTime)
			measuredCounts=scalarData[0]
			relinCounts=self.reLinearizeCounts(corrCounts)
			factor=[]
			for j in range(len(relinCounts)):
				if(relinCounts[j]==0 or measuredCounts[j]==0):
					val=1
					factor.append(1.0)
				else:
					val = (relinCounts[j]/measuredCounts[j])
					factor.append(val*liveTime)
			correctWindows=[]
			corrWindTot=0.0
			for j in range(9):
				correctW=float(windowedData[j])*factor[j]
				corrWindTot=corrWindTot+correctW
				correctWindows.append(correctW)
			#print>>fid,self.mDegForK(current,edgeEnergy,twoD),comboDCM.calcEnergy(self.mDegForK(current,edgeEnergy,twoD)/1000.0),\
			#	secTime,self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2],str(windowedData[0:]).strip('[]').replace(',',''), \
			#	totalw,str(correctWindows[0:]).strip('[]').replace(',',''),corrWindTot
			print>>fid,self.mDegForK(current,edgeEnergy,twoD),comboDCM.calcEnergy(self.mDegForK(current,edgeEnergy,twoD)/1000.0),\
				secTime,self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2],str(windowedData[0:]).strip('[]').replace(',',''), \
				totalw,str(correctWindows[0:]).strip('[]').replace(',',''),corrWindTot
			current=current+step
			# SDP Stuff
			detectorVector = Vector()
			detectorVector.add(self.ionchamberData[i])
			detectorVector.add(windowedData[0:])
			positionVector = Vector()
			positionVector.add(str(self.mDegForK(current,edgeEnergy,twoD)))
			#sdp = ScanDataPoint("scan name",self.scannableNamesVector,self.detectorNamesVector,positionVector,detectorVector,"Panel Name","I18 Custom SDP","Header String",self.datafilename)
			sdp = ScanDataPoint("Exafs FluKScan",self.scannableNamesVector,self.detectorNamesVector,None,None,None,None,positionVector,detectorVector,None,"Panel Name","I18 Custom SDP","Header String",self.datafilename,0)
			self.controller.update(None, sdp)
			self.mcontroller.update(None, sdp)

		fid.close()
	#==================================================
	# Window an mca contained in data between two values, start and end
	#==================================================
	def windowData(self,data,start,end):
		sum=0.0	
		for i in range(start,end):
			sum=sum+data[i]
		return sum	
					
	#==================================================
	# mDegForK converts k value (in inverse angstroms) to mDeg by using the java
	# Converter class.
	#==================================================
	def mDegForK(self,k,edgeEnergy,twoD):
		return gda.gui.exafs.Converter.convert(k,gda.gui.exafs.Converter.PERANGSTROM, gda.gui.exafs.Converter.MDEG,edgeEnergy, twoD)

	#==================================================
	# timeForK calculates the appropriate counting time for a particular k value
	# ==================================================
	def timeForK(self,k,start,end,kWeighting,kEndTime,kStartTime):
		a = Math.pow(k - start, kWeighting)
		b = Math.pow(end - start, kWeighting)
		c = (kEndTime - kStartTime)
		time = kStartTime + (a * c) / b
		# round to nearest 10milliseconds as this is all the ion chambers can collect in
		time=Math.round(time/1.0) * 1.0
		return time

	#==================================================
	#
	# Produces the tfg setup-groups used for kscans
	# In kscans you may want a time increase from start to finish
	# This method produces a series of individual tfg time frames for each time step in the scan
	#==================================================
	def getTFGCommandForKScan(self,start,step,end,kWeighting,kEndTime,kStartTime):
		difference = end - start;
		if (difference < 0 and step > 0):
			step = -step
		npoints = int(difference / step)
		currentpos = start
		tfglist="tfg setup-groups cycles 1 \n"
		for  j in range(npoints+1):
			secTime = self.timeForK(currentpos,start,end,kWeighting,kEndTime,kStartTime)
			tfglist = tfglist + "1 0.01 %f 0 1 1 0 \n" %(secTime/1000.0)
			currentpos = currentpos + step
		tfglist=tfglist+"-1 0 0 0 0 0 0 "
		return tfglist

	#==================================================
	#
	#  Creates the file used for the EXAFS
	# 
	#==================================================
	def createFile(self):
		if(os.path.exists(self.datafilename)==0):
			fid=open(self.datafilename,'w')
			df = SimpleDateFormat('hh.mm.dd.MM.yyyy')
			today = df.format(Date()) 
			print "Writing data to file:"+self.datafilename
			print "Writing mca file to:"+self.mcadir
			# write datetime
			line = " I18_EXAFS_RUN="+ str(self.fileno)+" "+ today
			print>>fid,line
			print>>fid,self.title
			print>>fid,self.condition1
			print>>fid,self.condition2
			print>>fid,self.condition3
			print>>fid,'Sample X=',MicroFocusSampleX.getPosition(),'Sample Y=',MicroFocusSampleY.getPosition()
			print>>fid,'comboDCM energy time I0 It drain flu1 flu2 flu3 flu4 flu5 flu6 flu7 flu8 flu9 flutot'
			fid.close()

	#==================================================
	#
	# Checks to see if an angle scan has been interrupted
	#
	#==================================================
	def checkForAngleInterrupt(self,npoints,start,end,step,collectionTime):
		#if(self.facade.getScanStatus()==0 and self.facade.getScriptStatus()==0):
		if(self.interrupted):
			print 'Stopping angle scan:Writing out data taken'
			# write the data we have so far and return
			self.stopDetector()	
			self.writeSummary(npoints,start,end,step,collectionTime)
			self.interrupted=Boolean(0)
			self.paused=Boolean(0)
			JythonServerFacade.getInstance().setScriptStatus(JythonStatus.IDLE)
			scandata = Vector()
			scandata.add("STOP")
			self.controller.update(None, scandata)
			self.mcontroller.update(None, scandata)
			print  'Now the nasty bit: throw an exception to stop running'
			raise lang.InterruptedException()
			raise lang.InterruptedException()


	#==================================================
	#
	# Checks to see if an angle scan has been paused
	#
	#==================================================
	def checkForAnglePause(self,npoints,start,end,step,collectionTime):
		if(self.paused):
			JythonServerFacade.getInstance().setScriptStatus(JythonStatus.PAUSED)
			while(self.paused):
				try:
					print 'Angle Scan paused - Awaiting resume'
					java.lang.Thread.sleep(10000)
				except lang.InterruptedException:
					self.checkForAngleInterrupt(npoints,start,end,step,collectionTime)


	#==================================================
	#
	# Checks to see if an angle scan has been paused
	#
	#==================================================
	def checkForKScanInterrupt(self,npoints,start,end,step,edgeEnergy, twoD,kStartTime,kEndTime,kWeighting):
		#if(self.facade.getScanStatus()==0 and self.facade.getScriptStatus()==0):
		if(self.interrupted):
			print 'Stopping k scan:Writing out data taken'
			# write the data we have so far and return
			self.stopDetector()	
			self.writeKScanSummary(npoints,start,end,step,edgeEnergy, twoD,kStartTime,kEndTime,kWeighting)
			self.interrupted=Boolean(0)
			self.paused=Boolean(0)
			JythonServerFacade.getInstance().setScriptStatus(JythonStatus.IDLE)
			scandata = Vector()
			scandata.add("STOP")
			self.controller.update(None, scandata)
			self.mcontroller.update(None, scandata)
			print  'Now the nasty bit: throw an exception to stop running'
			raise lang.InterruptedException()

	#==================================================
	#
	# Checks to see if an angle scan has been paused
	#
	#==================================================
	def checkForKScanPause(self,npoints,start,end,step,edgeEnergy, twoD,kStartTime,kEndTime,kWeighting):
		if(self.paused):
			JythonServerFacade.getInstance().setScriptStatus(JythonStatus.PAUSED)
			while(self.paused):
				try:
					print 'K Scan Scan paused - Awaiting resume'
					java.lang.Thread.sleep(10000)
				except lang.InterruptedException:
					self.checkForKScanInterrupt(npoints,start,end,step,edgeEnergy, twoD,kStartTime,kEndTime,kWeighting)

	#==================================================
	# To set the resolution binning used by xspress
	#  Usage
	#  setResMode(0)   .. all grades processed
	#  setResMode(1)   .. variable all grades summed into 1 grade
	#  setResMode(1,8)   variable all grades from 0-7 put in one grade and 8-15 in next grade
	#==================================================
	def setResMode(self,mode,map=None):
		if(mode==0):
			command="xspress2 set-resmode \"xsp1\" 0 0"
			self.das.sendCommand(command)
		else:
			if(map==None or map < 0 or map > 15):
				command="xspress2 set-resmode \"xsp1\" 1 0"
			else:
				command="xspress2 set-resmode \"xsp1\" 1 %d" %(map)
			self.das.sendCommand(command)

	#==================================================
	#
	# To set the header info used in the script
	#
	#==================================================
	def setHeaderInfo(self,title,condition1,condition2,condition3):
		self.title=title
		self.condition1=condition1
		self.condition2=condition2
		self.condition3=condition3
	#==================================================
	#
	# Get corrected counts 
	#
	#==================================================
	def getCorrectedCounts(self,countData,resetData,liveTime):
		realCounts=[]
		for i in range(len(countData)):
			realCounts.append(countData[i]*(1.0/(liveTime-((12.5e-9)*resetData[i]))))
		return realCounts
	#==================================================
	#
	# Get corrected counts 
	#
	#==================================================
	def reLinearizeCounts(self,corrCounts):
		process_times=[3.4e-07,3.8e-07,3.7e-07,3.0e-07,3.4e-07,3.5e-07,3.3e-07,3.0e-07,3.3e-07]
		realCounts=[]
		for i in range(len(process_times)):
			a=process_times[i]*corrCounts[i]
			aa=a*a
			eqn1=(-10.0+27.0*a+5.196152423*sqrt(4-20.0*a+27.0*aa))**(1.0/3.0)
			eqn2=(1.0/(3.0*process_times[i]))
			eqn3= eqn2*eqn1 - 2*eqn2/eqn1 + 2*eqn2  
			realCounts.append(eqn3)
		return realCounts

	#==================================================
	#
	# Read in a scalar data file and return array
	#
	#==================================================
	def readScalarDataFile(self,scalarfile):
		scalarData=[] 
		for j in range(2):
			scalerData.append(range(9))
		fis =FileInputStream(self.scalarList[i])
		dis =DataInputStream(fis)
		scalerBytes =jarray.zeros(18*4,'b')
		dis.read(scalerBytes, 0, 18*4)
		fis.close()
		offset = 0
		for j in range(2):
			for l in range(0,36,4):
				scalarData[j][l/4]= (0x000000FF & scalerBytes[offset+l+0]) + ((0x000000FF & scalerBytes[offset+l+1])<<8)+((0x000000FF & scalerBytes[offset+l+2])<<16)+((0x000000FF & scalerBytes[offset+l+3])<<24)
			offset=offset+36	
		fis.close()
		return scalarData

	#
	# In a scan you create a new scan object for each scan
	# You can  reuse the i18exafs scan
	#  This simply increments the file no.s etc.
	#
	def incrementFilename(self):
		self.fileno=self.runs.getCurrentFileNumber()+1
		self.runs.incrementNumber()
		self.datadir=InterfaceProvider.getPathConstructor().createFromProperty("gda.data.scan.datawriter.datadir")
		self.datafilename=self.datadir+'/'+str(self.fileno)+self.runext
		self.mcadir=self.datadir+'/mca/'+str(self.fileno)+'/'
		self.mcarootname=self.mcadir+str(self.fileno)
		if not os.path.isdir(self.mcadir):
			os.mkdir(self.mcadir)
		self.tag=1
		self.interrupted=Boolean(0)
