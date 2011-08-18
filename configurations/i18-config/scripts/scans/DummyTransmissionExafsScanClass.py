from gda.epics import CAClient
from java.lang import *
from gda.device.scannable import ScannableBase
from gda.device import Scannable
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
from java.text import SimpleDateFormat
from java.util import Date
import os
import jarray

#
# TRANSMISSION EXAFS SCAN
# run SlaveCounterTimer.py
# run I18TransmissionExafsClass.py
#
# This doesn't plot data, it just collects it. ion chambers  which are synched via the tfg and adc.
#
# Create the class
#	myscan=I18TransmissionExafsScanClass()
#	myscan.anglescan(8824.0,8739.460869565219,-3.8608695652174387,1000.0)
#	myscan.anglescan(8735.599999999999,8698.5,-0.6999999999999865,1000.0)
#
# Now do the kscan with the values from the configure button in the exafs panel
#
#	myscan.kscan(3.0,12.0,0.04,1000.0,3000.0,3,13.039848732586526,6.271000000000002)
#
#
class DummyTransmissionExafsScanClass(ScriptBase):
	def __init__(self):
		self.scannableNamesVector=Vector()
		self.scannableNamesVector.add("dcm_mono")
		self.detectorNamesVector=Vector()
		self.detectorNamesVector.add("counterTimer01")
		self.controller = finder.find("ExafsController")
		self.mcontroller = finder.find("MicroFocusController")
		#self.das=finder.find("daserver")
		self.ionchambers=DummySlaveCounterTimer()
 		# define pi
		self.pi=4.0*atan(1.0)
		# default collect all
		self.title="TITLE"
		self.condition1="CONDITION1"
		self.condition2="CONDITION2"
		self.condition3="CONDITION3"

		self.ionchamberData=[]
		self.runs=NumTracker("tmp")
		self.runext='.dat'
		self.fileno=self.runs.getCurrentFileNumber()+1
		self.runs.incrementNumber()
		self.datadir=LocalProperties.get("gda.data.scan.datawriter.datadir")
		self.datafilename=self.datadir+'/'+str(self.fileno)+self.runext
		self.scanList=[]
		self.noOfRepeats=1
		self.noOfPoints=0
		
	def calcEnergy(self,bragg):
		energy=1977.42/self.sind(bragg)
		return energy

	def sind(self,value):
		valueradians=self.angleToRadians(value)
		sintheta=sin(valueradians)
		return sintheta

	def asind(self,value):
		valueradians=self.angleToRadians(value)
		asintheta=asin(valueradians)
		return asintheta

	def cosd(self,value):
		valueradians=self.angleToRadians(value)
		costheta=cos(valueradians)
		return costheta

	def angleToRadians(self,angle):
		factor = 180.0/self.pi
		return angle/factor

	def radiansToAngle(self,angle):
		factor = 180.0/self.pi
		return angle*factor
	



	def addAngleScan(self,start,end,step,collectionTime):
		self.noOfPoints=self.noOfPoints+int((end-start)/step)
		self.scanList.append(['a',start,end,step,collectionTime])

	def addKScan(self,start,end,step,kStartTime,kEndTime,kWeighting, edgeEnergy, twoD):
		self.noOfPoints=self.noOfPoints+int((end-start)/step)
		self.scanList.append(['k',start,end,step,kStartTime,kEndTime,kWeighting, edgeEnergy, twoD])


	def setNoOfRepeats(self,repeats):
		self.noOfRepeats=repeats

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
		scandata.add("TransScan")
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

	#
	# Performs an angle scan in step mode
	# 
	def anglescan(self,start,end,step,collectionTime):
		self.createFile()
		# find no of points
		difference = end - start
		if (difference < 0 and step > 0):
			step = -step
		npoints = int(difference / step)
		currentpos=start*1.0
		# Set collection times
		self.ionchambers.setCollectionTime(collectionTime/1000.0)
		self.prepareDetectorForCollection(npoints,collectionTime/1000.0)
		# loop over npoints
		print 'Starting angle scan'
		print 'Mono\tI0\t It\t Idrain\t'
		for i in range(npoints):
			self.checkForPause()
			# Check beam is running
			#while(BeamMonitor.beamOn()==0):
			#	print 'Beam lost : Pausing until resumed'
			#	sleep(120)

			# Move mono to start position
			dcm_mono.moveTo(currentpos)
			#ScannableBase.waitForScannable(comboDCM)
			# Ready the ion chambers
			self.ionchambers.clearAndPrepare()
			#
			# tfg starts paused so tell it to continue
			#
			#self.das.sendCommand("tfg cont")
			#self.das.sendCommand("tfg wait timebar")
			# read out the ion chambers
			#while(self.ionchambers.isBusy()>=1):
			##	sleep(0.05)
			#	pass
			self.ionchamberData.append(self.ionchambers.collectData())
			print currentpos,self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2]
			self.writeSummary(currentpos,self.ionchamberData[i],collectionTime)
			# Move the mono
			currentpos=currentpos+step
		#
		self.stopTFG()	
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
		self.createFile()
		# check that step is negative when moving downwards to stop
		difference = end - start
		if (difference < 0 and step > 0):
			step = -step
		npoints = int(difference / step)

		currentpos=start
		# prepare detector for collection
		print 'Preparing TFG'
		self.prepareDetectorForKScan(start,step,end,kWeighting,kEndTime,kStartTime)
		print 'Starting k scan'
		print 'angle \t energy \tI0\t It\t Idrain\t'
		for i in range(npoints):
			self.checkForPause()
			# Check beam is running
		#	while(BeamMonitor.beamOn()==0):
			#	print 'Beam lost : Pausing until resumed'
			#	sleep(120)

			mdegPosition = self.mDegForK(currentpos,edgeEnergy,twoD)
			secTime = self.timeForK(currentpos,start,end,kWeighting,kEndTime,kStartTime)
			# Set the collection time
			self.ionchambers.setCollectionTime(secTime/1000.0)
			# Move mono to start position

			dcm_mono.moveTo(mdegPosition)
			#ScannableBase.waitForScannable(comboDCM)

			# Ready the ion chambers
			self.ionchambers.clearAndPrepare()
			#
			# tfg starts paused so tell it to continue
			#
			#self.das.sendCommand("tfg cont")
			#
			# wait until it is finished running
			#
		#	self.das.sendCommand("tfg wait timebar")
		#	while(self.ionchambers.isBusy()>=1):
			#	sleep(0.05)
			#	pass
			mydata=self.ionchambers.collectData()
			# print out some progress
			print mdegPosition,self.calcEnergy(mdegPosition/1000.0),mydata[0],mydata[1],mydata[2]
			self.writeSummary(mdegPosition,mydata,secTime)
			# Move the mono
			currentpos=currentpos+step

		#
		#  write out at end
		#		
		self.stopTFG()	
		print 'Finished k scan'


	#
	#  Disables, Clears and enables the detector
	#  Sets up tfg for a given noOfFrames and  collectionTime
	#  pausing in the dead frame and dead port=1 for adc triggering
	#  and finally starts the tfg which means it sits waiting for a software based continue command
	#
	def prepareDetectorForCollection(self,noOfFrames,collectionTime):
		#self.das.sendCommand("tfg init")
		command = "tfg setup-groups cycles 1 \n%d 0.01 %f 0 1 1 0 \n-1 0 0 0 0 0 0 "  %(noOfFrames,collectionTime)
		#self.das.sendCommand(command)
	#	self.das.sendCommand("tfg start")
	#
	#  Disables, Clears and enables the detector
	#  Sets up tfg for a set of possibly variable length time frames
	#  and finally starts the tfg which means it sits waiting for a software based continue command
	#
	def prepareDetectorForKScan(self,start,step,end,kWeighting,kEndTime,kStartTime):
	#	self.das.sendCommand("tfg init")
		#self.das.sendCommand("tfg auto-cont 0")
		command = self.getTFGCommandForKScan(start,step,end,kWeighting,kEndTime,kStartTime)
	#	self.das.sendCommand(command)
	#	self.das.sendCommand("tfg start")
	#
	# Stop the tfg and disable the detector
	#
	def stopTFG(self):
	#	self.das.sendCommand("tfg init")
		return

	def writeSummary(self,currentpos,data,collectionTime):
		fid = open(self.datafilename,'a')		
		print >>fid,currentpos,self.calcEnergy(currentpos/1000.0),collectionTime,data[0],data[1],data[2]
		detectorVector = Vector()
		newdata=[data[0],data[1],data[2]]	
		detectorVector.add(newdata)
		positionVector = Vector()
		positionVector.add(str(currentpos))
		#sdp = ScanDataPoint("scan name",self.scannableNamesVector,self.detectorNamesVector,positionVector,detectorVector,"Panel Name","I18 Custom SDP","Header String",self.datafilename)
		#ScanDataPoint(String scanName, Vector<String> scannables,
		#Vector<String> detectors, Vector<String> monitors,
		#Vector<String> scannableHeader, Vector<String> detectorHeader,
		#Vector<String> monitorHeader, Vector<String> positions,
		#Vector<Object> data, Vector<String> monitorPositions,
		#String creatorPanelName, String tostring, String headerString,
		#String currentFilename, boolean hasChild)
		sdp = ScanDataPoint("scan name",self.scannableNamesVector,self.detectorNamesVector,None,None,None,None,positionVector,detectorVector,None,"Panel Name","I18 Custom SDP","Header String",self.datafilename,0)
		self.controller.update(None, sdp)
		fid.close()

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
		time=Math.round(time/1.0) * 1.0
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
		tfglist="tfg setup-groups cycles 1\n"
		for  j in range(npoints+1):
			secTime = self.timeForK(currentpos,start,end,kWeighting,kEndTime,kStartTime)
			tfglist = tfglist + "1 0.01 %f 0 1 1 0\n " %(secTime/1000.0)
			currentpos = currentpos + step
		tfglist=tfglist+"-1 0 0 0 0 0 0 "
		return tfglist

	#
	#
	# If a user presses the halt or stop button on the gui
	# stops the scan
	#
	# def checkForInterupts(self):
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
			# write datetime
			line = " I18_EXAFS_RUN="+ str(self.fileno)+" "+ today
			print>>fid,line
			print>>fid,self.title
			print>>fid,self.condition1
			print>>fid,self.condition2
			print>>fid,self.condition3
			print>>fid,'Sample X=',MicroFocusSampleX.getPosition(),'Sample Y=',MicroFocusSampleY.getPosition()
			print>>fid,'comboDCM energy time I0 It'
			fid.close()


	# ========================================
	#  Read in a window to be used on the mca files 
	# ========================================
	def setWindows(self,filename,desiredWindow):
		print 'Do nothing'

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
	# Checks to see if an angle scan has been paused
	#
	#==================================================
	def checkForPause(self):
		if(self.paused):
			JythonServerFacade.getInstance().setScriptStatus(Jython.PAUSED)
			while(self.paused):
				try:
					print 'Scan paused - Awaiting resume'
					java.lang.Thread.sleep(10000)
				except lang.InterruptedException:
					self.stopTFG()	
					self.interrupted=Boolean(0)
					self.paused=Boolean(0)
					JythonServerFacade.getInstance().setScriptStatus(Jython.IDLE)
					print  'Now the nasty bit: throw an exception to stop running'
					raise lang.InterruptedException()

	#
	# In a scan you create a new scan object for each scan
	# You can  reuse the i18exafs scan
	#  This simply increments the file no.s etc.
	#
	def incrementFilename(self):
		self.fileno=self.runs.getCurrentFileNumber()+1
		self.runs.incrementNumber()
		self.datadir=LocalProperties.get("gda.data.scan.datawriter.datadir")
		self.datafilename=self.datadir+'/'+str(self.fileno)+self.runext
		self.mcadir=self.datadir+'/mca/'+str(self.fileno)+'/'
		self.mcarootname=self.mcadir+str(self.fileno)
		if not os.path.isdir(self.mcadir):
			os.mkdir(self.mcadir)
		self.tag=1
		self.interrupted=Boolean(0)
