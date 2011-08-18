from gda.epics import CAClient
from java.lang import *
#from gda.jython.scannable import ScannableBase
#from gda.jython.scannable import Scannable
from gda.device.scannable import ScannableBase
from gda.device import Scannable

from org.python.modules.math import *
from time import sleep
from gda.analysis import *
import jarray
#
#
#   A step map scan
#
#   Usage:
#   pdq=I18VortexMapPlotClass()
#                                 xstart     xend    xstep        ystart     yend   ystep    time(ms)
#   pdq.stepmapscan(-7.474,  -6.613,   0.01,     6.178,   6.86,   0.01,  3000)#    
#
#
#   Does not plot as it runs but will produce a .dat file. 
#   Not ideal, but it works !
#
#

class I18VortexMapPlotClass:
	def __init__(self):
		self.xmotor=MicroFocusSampleX
		self.ymotor=MicroFocusSampleY
		self.das=finder.find("daserver")
		self.ionchambers=SlaveCounterTimer()
		self.vortex=vortex_mca
		self.ionchamberData=[]
		self.runs=NumTracker("tmp")
		self.runext='.dat'
		self.fileno=self.runs.getCurrentFileNumber()+1
		self.runs.incrementNumber()
		self.datadir=LocalProperties.get("gda.data.scan.datawriter.datadir")
		self.datafilename=self.datadir+'/'+str(self.fileno)+self.runext
		self.rgbdatafilename=self.datadir+'/'+str(self.fileno)+".rgb"
		self.fluData=[]
		self.createFile()
		#self.createRGBFile()




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
		#self.vortex.setCollectionTime(collectionTime/1000.0)
		#self.vortex.stop()
		# Create the dataset
		self.fluData=DataSet([nx,ny])
		self.vortex.stop()
		for i in range(ny):
			#
			# Prepare detector for row
			# 
			self.ionchamberData=[]
			self.prepareTFGForRow(nx,collectionTime)
			for j in range(nx):
				# Check beam is running
				while(BeamMonitor.beamOn()==0):
					print 'Beam lost : Pausing until resumed'
					try:
						sleep(60)
					except:
						print 'Trying to stop during sleep'

				#
				# topup test
				#
				while(BeamMonitor.collectBeforeTopupTime(collectionTime/1000.0)==1):
					print 'Top up coming : Pausing until resumed'
					try:
						sleep(1)
					except:
						self.interrupted=1    
				#self.checkForInterrupt()
				# Ready the ion chambers and vortex
				self.vortex.stopEraseAndStart()
				self.ionchambers.clearAndPrepare()
				# 
				self.das.sendCommand("tfg cont")
				self.das.sendCommand("tfg wait timebar")
				while(self.ionchambers.isBusy()==1):
					sleep(0.05)
					pass
				# Update the vortex status
				self.vortex.updateStatus()
				sleep(0.1)
				ionChambers=self.ionchambers.collectData()
				vortexdata=self.vortex.getROISums()
				#self.vortex.stop()
				print xcurrent,ycurrent,ionChambers[0],ionChambers[1],ionChambers[2],vortexdata
				self.fluData.set(vortexdata,[j,i])
				# update the motor position
				self.writeSummary(xcurrent,ycurrent,ionChambers,collectionTime,vortexdata)
				#self.writeToRGB(i,j,ionChambers[0],ionChambers[1],ionChambers[2],vortexdata)
				xcurrent=xcurrent+xstep
				self.xmotor.moveTo(xcurrent)	
				# tell the tfg to continue
			print 'Finished row',i
			# Now update the plot
			self.plot()
			self.stopTFG()
			#
			# increment y
			#
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
		self.das.sendCommand("tfg setup-groups cycles 1 ")
		command = "%d 0.01 %f 0 3 1 0 "  %(noOfFrames,collectionTime/1000.0)
		self.das.sendCommand(command)
		self.das.sendCommand("-1 0 0 0 0 0 0 ")
		self.das.sendCommand("tfg start")

			

	def writeSummary(self,currentx,currenty,ionChambers,collectionTime,vortexdata):
		fid = open(self.datafilename,'a')
		print >>fid,str(currentx),str(currenty),str(collectionTime),str(ionChambers[0]),str(ionChambers[1]),str(ionChambers[2]),str(vortexdata)
		fid.close()


	# Stop the tfg and disable the detector
	#
	def stopTFG(self):
		self.das.sendCommand("tfg init")


	def getNorm(self,a):
		max=a.get([0,0])
		min=a.get([0,0])
		newdataset=DataSet([a.getDimensions()[0],a.getDimensions()[1]])
		for i in range(a.getDimensions()[0]):
			for j in range(a.getDimensions()[1]):
				value=a.get([i,j])
				if(value>max):
					max=value
				if(value<min):
					min=value
		if(max==0):
			return a
		else:
			for i in range(a.getDimensions()[0]):
				for j in range(a.getDimensions()[1]):
					value=a.get([i,j])
					value=value-min
					value=value/max
					#print 'value',value
					newdataset.set(value,[i,j])
			return newdataset	
			

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

	def plot(self):
		newdata=self.getNorm(self.fluData)
		Plotter.plotImage("Data Vector",newdata)

	def createRGBFile(self):
		fid=open(self.rgbdatafilename,'w')
		mystr='row  column  i0  it  id  vortex'
		print >> fid,mystr
		fid.close()

	def writeToRGB(self,nx,ny,i0,it,id,flu):
		fid=open(self.rgbdatafilename,'a')
		print >> fid,nx,ny,str(i0).strip(),str(it).strip(),str(id).strip(),flu
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
			self.vortex.stop()	
			self.xmotor.stop()
			self.ymotor.stop()
			self.interrupted=Boolean(0)
			self.paused=Boolean(0)
			self.stopTFG()
			JythonServerFacade.getInstance().setScriptStatus(Jython.IDLE)
			print  'Now the nasty bit: throw an exception to stop running'
			raise lang.InterruptedException()

