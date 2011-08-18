from java.lang import *
from gda.device.scannable import ScannableBase
from gda.device import Scannable
from org.python.modules.math import *
from time import sleep
import jarray
#
#
#   A step map scan
#
#   Usage:
#   pdq=DummyTransmissionMapClass()
#                                 xstart     xend    xstep        ystart     yend   ystep    time(ms)
#   pdq.stepmapscan(-7.474,  -6.613,   0.01,     6.178,   6.86,   0.01,  3000)#    
#
#
#   Does not plot as it runs but will produce a .dat file. 
#   Not ideal, but it works !
#
#

class DummyTransmissionMapClass:
   def __init__(self, datafileNo="default"):
      self.scannableNamesVector=Vector()
      self.scannableNamesVector.add("sample_x_motor")
      self.scannableNamesVector.add("MicroFocusSampleY")
      self.detectorNamesVector=Vector()
      self.detectorNamesVector.add("counterTimer01")
      #self.detectorNamesVector.add("counterTimer02")
      self.xmotor=finder.find("sample_x_motor")
      self.ymotor=MicroFocusSampleY
      self.das=finder.find("daserver")
      self.ionchambers=DummySlaveCounterTimer()
      self.ionchamberData=[]
      # Find the script controller
      self.controller = finder.find("MicroFocusController")
      if(datafileNo == "default"):
            self.runs=NumTracker("tmp")
            self.fileno=self.runs.getCurrentFileNumber()+1
            self.runs.incrementNumber()
      else:
            self.fileno = datafileNo
      self.runext='.dat'
      self.datadir=LocalProperties.get("gda.data.scan.datawriter.datadir")
      self.datafilename=self.datadir+'/'+str(self.fileno)+self.runext
      self.createFile()


   def stepmapscan(self,xstart,xend,xstep,ystart,yend,ystep,collectionTime):
		nx=abs(xend-xstart)/xstep
		ny=abs(yend-ystart)/ystep
		nx=int(nx+0.5)
		ny=int(ny+0.5)
		xcurrent=xstart
		ycurrent=ystart
		# Move to start
		self.xmotor.moveTo(xcurrent)
		self.ymotor.moveTo(ycurrent)
		self.ionchambers.setCollectionTime(collectionTime/1000.0)

		for i in range(ny):
			#
			# Prepare detector for row
			# 
			self.ionchamberData=[]
			self.prepareTFGForRow(nx,collectionTime)
			for j in range(nx):
				# Ready the ion chambers
				self.ionchambers.clearAndPrepare()
				#self.das.sendCommand("tfg cont")
				#while (self.das.sendCommand("tfg read status") == 'RUNNING'):
					#sleep(0.10)
					#pass
				#while(self.ionchambers.isBusy()==1):
					#sleep(0.10)
					#pass

				#self.ionchamberData.append(self.ionchambers.collectData())
				ionChambers=self.ionchambers.collectData()
				#print xcurrent,ycurrent,self.ionchamberData[j][0],self.ionchamberData[j][1],self.ionchamberData[j][2]
				print xcurrent,ycurrent,ionChambers[0],ionChambers[1],ionChambers[2]
				# update the motor position
				self.writeSummary(xcurrent,ycurrent,ionChambers,collectionTime)
				xcurrent=xcurrent+xstep
				self.xmotor.moveTo(xcurrent)	
				# tell the tfg to continue
			print 'Finished row',i
			self.stopTFG()
			#
			# increment y
			#
			#self.writeRowSummary(ycurrent,xstart,xstep,nx,collectionTime)
			ycurrent=ycurrent+ystep
			self.ymotor.moveTo(ycurrent)	
			#
			# return x to its start point
			# 
			xcurrent=xstart
			self.xmotor.moveTo(xcurrent)
		self.controller.update(None, "STOP")
		print 'Scan complete'


   def stopScan(self):
		self.controller.update(None, "STOP")
		return
	
   def prepareTFGForRow(self,noOfFrames,collectionTime):
		#self.das.sendCommand("tfg init")
		#self.das.sendCommand("tfg generate")
		#command = "tfg setup-groups cycles 1 \n %d 1.0E-5 %f 0 1 1 0 \n -1 0 0 0 0 0 0"  %(noOfFrames,collectionTime/1000.0)
		#elf.das.sendCommand(command)
		#self.das.sendCommand("tfg start")
		return

			

   def writeSummary(self,currentx,currenty,ionChambers,collectionTime):
      print "the ion chamber data is  "+ str(len(ionChambers)) 
      print ionChambers
      fid = open(self.datafilename,'a')
      detectorVector = Vector()
      newdata=[ionChambers[0],ionChambers[1],ionChambers[2]]
      detectorVector.add(newdata)
      positionVector = Vector()
      positionVector.add(str(currentx))
      positionVector.add(str(currenty))
      line=str(currentx)+"\t"+str(currenty)+"\t"+str(collectionTime)+"\t"+str(ionChambers[0])+"\t"+str(ionChambers[1])+"\t"+str(ionChambers[2])
      print >>fid, line
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


	# Stop the tfg and disable the detector
	#
   def stopTFG(self):
		#self.das.sendCommand("tfg init")
		return

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
		# write datetime
		line =' &SRS'
		line=' &END'
		print>>fid,line
		print>>fid,'   '
		print>>fid,'   '
		fid.close()
		#fid=open(self.datafilename,'w')
		#fid.close()

