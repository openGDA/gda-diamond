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
#   pdq=I18StepMapClass()
#                                 xstart     xend    xstep        ystart     yend   ystep    time(ms)
#   pdq.stepmapscan(-7.474,  -6.613,   0.01,     6.178,   6.86,   0.01,  3000)#    
#
#
#   Does not plot as it runs but will produce a .dat file. You can use the load command in GDA Microfocus window 
#   to produce a map from the .dat file later
#

class I18StepMapClass:
	def __init__(self):
		self.xmotor=finder.find("sample_x_motor")
		self.ymotor=MicroFocusSampleY
		self.das=finder.find("daserver")
		self.mcaList=[]
		self.ionchambers=SlaveCounterTimer()
		self.ionchamberData=[]
		self.mcaList=[]
		self.runs=NumTracker("tmp")
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




	def stepmapscan(self,xstart,xend,xstep,ystart,yend,ystep,collectionTime):
		self.mcaList=[]
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

		for i in range(ny):
			#
			# Prepare detector for row
			# 
			self.ionchamberData=[]
			self.mcaList=[]
			self.prepareDetectorForRow(nx,collectionTime)
			for j in range(nx):
				# Ready the ion chambers
				self.ionchambers.clearAndPrepare()
		
				self.das.sendCommand("tfg cont")
				while (self.das.sendCommand("tfg read status") == 'RUNNING'):
					sleep(0.10)
					pass
				while(self.ionchambers.isBusy()==1):
					sleep(0.10)
					pass

				self.ionchamberData.append(self.ionchambers.collectData())
				print xcurrent,ycurrent,self.ionchamberData[j][0],self.ionchamberData[j][1],self.ionchamberData[j][2]
				
				# update the motor position
				xcurrent=xcurrent+xstep
				self.xmotor.moveTo(xcurrent)	
				# tell the tfg to continue
			print 'Finished row',i
			self.stopDetector()	
			#
			# Dump the detector data to files
			#
			self.writeDetectorFiles(i,nx)		
			#
			# increment y
			#
			self.writeSummary(ycurrent,xstart,xstep,nx,collectionTime)
			ycurrent=ycurrent+ystep
			self.ymotor.moveTo(ycurrent)	
			#
			# return x to its start point
			# 
			xcurrent=xstart
			self.xmotor.moveTo(xcurrent)
		print 'Scan complete'


	
	def prepareDetectorForRow(self,noOfFrames,collectionTime):
		self.das.sendCommand("disable 0")
		self.das.sendCommand("clear 0")
		self.das.sendCommand("enable 0")
		self.das.sendCommand("tfg init")
		self.das.sendCommand("tfg generate")
		command = "tfg setup-groups cycles 1 \n %d 1.0E-5 %f 0 1 1 0 \n -1 0 0 0 0 0 0"  %(noOfFrames,collectionTime/1000.0)
		self.das.sendCommand(command)
		self.das.sendCommand("tfg start")

	def writeDetectorFiles(self,yindex,nx):
		self.das.sendCommand("disable 0")
		for i in range(nx):
			name = "%s_yindex_%d_xindex_%d.xsp" % (self.mcarootname,yindex,i)
			self.mcaList.append(name)
			#command = "read 0 0 %d 65536 9 1 from 0 to-local-file \"/dls/i18/tmp/%s\" raw intel" % ( i, name)
			command = "read 0 0 %d 4096 9 1 from 0 to-local-file \"%s\" raw intel" % ( i, name)
			self.das.sendCommand(command)
			

	def writeSummary(self,currenty,startx,stepx,nx,collectionTime):
		# lets window this mofo
		fid = open(self.datafilename,'a')
		for i in range(nx):
			val=(startx+(i-1)*stepx)
			line=str(val)+"\t"+str(currenty)+"\t"+str(collectionTime)+"\t"+str(self.ionchamberData[i][0])+"\t"+str(self.ionchamberData[i][1])+"\t"+str(self.ionchamberData[i][2])+"\t"+str(self.mcaList[i])
			print >> fid,line
			print (startx+(i-1)*stepx),currenty,collectionTime,self.ionchamberData[i][0],self.ionchamberData[i][1],self.ionchamberData[i][2],self.mcaList[i]
		fid.close()

	# Stop the tfg and disable the detector
	#
	def stopDetector(self):
		self.das.sendCommand("tfg init")
		self.das.sendCommand("disable 0")
		

		

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
		line =' &SRS'
		line=' &END'
		print>>fid,line
		print>>fid,'   '
		print>>fid,'   '
		fid.close()
