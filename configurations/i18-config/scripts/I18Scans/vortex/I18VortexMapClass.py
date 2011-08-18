from gda.epics import CAClient
from java.lang import *
from gda.jython.scannable import ScannableBase
from gda.jython.scannable import Scannable
from org.python.modules.math import *
from time import sleep
import jarray
#
#
#   A step map scan
#
#   Usage:
#   pdq=I18VortexMapClass()
#                                 xstart     xend    xstep        ystart     yend   ystep    time(ms)
#   pdq.stepmapscan(-7.474,  -6.613,   0.01,     6.178,   6.86,   0.01,  3000)#    
#
#
#   Does not plot as it runs but will produce a .dat file. 
#   Not ideal, but it works !
#
#

class I18VortexMapClass:
	def __init__(self):
		self.xmotor=finder.find("sample_x_motor")
		self.ymotor=MicroFocusSampleY
		self.das=finder.find("daserver")
		self.ionchambers=SlaveCounterTimer()
		self.vortex=vortex1
		self.ionchamberData=[]
		self.runs=NumTracker("tmp")
		self.runext='.dat'
		self.fileno=self.runs.getCurrentFileNumber()+1
		self.runs.incrementNumber()
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
		self.ionchambers.setCollectionTime(collectionTime)
		self.vortex.setCollectionTime(collectionTime/1000.0)
		for i in range(ny):
			#
			# Prepare detector for row
			# 
			self.ionchamberData=[]
			self.prepareTFGForRow(nx,collectionTime)
			for j in range(nx):
				# Ready the ion chambers
				self.ionchambers.clearAndPrepare()
				self.vortex.start()
				self.das.sendCommand("tfg cont")
				
				while (self.das.sendCommand("tfg read status") == 'RUNNING'):
					sleep(0.05)
					pass
				while(self.ionchambers.isBusy()==1):
					sleep(0.05)
					pass

				#self.ionchamberData.append(self.ionchambers.collectData())
				ionChambers=self.ionchambers.collectData()
				vortexdata=self.vortex.getPosition()
				self.vortex.stop()
				#print xcurrent,ycurrent,self.ionchamberData[j][0],self.ionchamberData[j][1],self.ionchamberData[j][2]
				print xcurrent,ycurrent,ionChambers[0],ionChambers[1],ionChambers[2],vortexdata
				# update the motor position
				self.writeSummary(xcurrent,ycurrent,ionChambers,collectionTime,vortexdata)
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
		print 'Scan complete'


	
	def prepareTFGForRow(self,noOfFrames,collectionTime):
		self.das.sendCommand("tfg init")
		command = "tfg setup-groups cycles 1 \n%d 0.01 %f 0 1 1 0 \n -1 0 0 0 0 0 0 "  %(noOfFrames,collectionTime)
		self.das.sendCommand(command)
		self.das.sendCommand("tfg start")

			

	def writeSummary(self,currentx,currenty,ionChambers,collectionTime,vortexdata):
		fid = open(self.datafilename,'a')
		print >>fid,str(currentx),str(currenty),str(collectionTime),str(ionChambers[0]),str(ionChambers[1]),str(ionChambers[2]),str(vortexdata)
		fid.close()


	# Stop the tfg and disable the detector
	#
	def stopTFG(self):
		self.das.sendCommand("tfg init")

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
		fid=open('/dls/i18/tmp/currentImage.dat','w')
		fid.close()

	def createRGBFile(self):
		fid=open(self.rgbdatafilename,'w')
		mystr='row  column  i0  it  id  flu'
		print >> fid,mystr
		fid.close()

	def writeToRGB(self,nx,ny,i0,it,id,flu):
		fid=open(self.rgbdatafilename,'a')
		print >> fid,nx,ny,str(i0).strip(),str(it).strip(),str(id).strip(),str(flu).strip()
		fid.close()

