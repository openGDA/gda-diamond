from gda.epics import CAClient 
from java import lang
from gda.device.scannable import ScannableBase
from gda.device import Scannable
from time import sleep

class TCA(ScannableBase):
	def __init__(self,pvstring):
		self.pvstring=pvstring
		

	def setDefaults(self):
		self.setProperty('POLARITY',0)
		self.setProperty('THRESHOLD',0)
		self.setProperty('SCA_ENABLE',0)
		self.setProperty('READBACK.SCAN',4)
		self.setProperty('PUR_ENABLE',0)
		self.setProperty('PUR_AMP',0)
		self.setProperty('TCA_SELECT',0)
		self.setProperty('SCA1_GATE',0)
		self.setProperty('SCA2_GATE',0)
		self.setProperty('SCA3_GATE',0)
		self.setProperty('SCA1_PUR',0)
		self.setProperty('SCA2_PUR',0)
		self.setProperty('SCA3_PUR',0)
	

	def setProperty(self,name,value):
        		caput(self.pvstring+name,value)

		
	def getProperty(self,name):
        		return caget(self.pvstring+name)





class tcasca(ScannableBase):
	def __init__(self, name,formatstring,link,unitstring,number):
		self.setName(name);
		self.setLevel(3)
		self.link=link
		self.setInputNames([name+' low',name+' hi'])
		self.Units=[unitstring]
		self.setOutputFormat([formatstring,formatstring])
		self.number=number
		
	def asynchronousMoveTo(self,new_position):
		if new_position[0] >= new_position[1]:
			print "error: wrong values"
		else:
			self.link.setProperty('SCA'+self.number+'_LOW',new_position[0])
			self.link.setProperty('SCA'+self.number+'_HI',new_position[1])


	def isBusy(self):
		return 0

	def getPosition(self):
		scalow=self.link.getProperty('SCA'+self.number+'_LOW')
		scahi=self.link.getProperty('SCA'+self.number+'_HI')
		return [float(scalow), float(scahi)]

	def on(self):
		stringa='SCA'+self.number+'_GATE'
		self.link.setProperty(stringa,1)
		return self.link.getProperty(stringa)


	def off(self):
		stringa='SCA'+self.number+'_GATE'
		self.link.setProperty(stringa,0)
		return self.link.getProperty(stringa)



# commented out for the moment to save time !!!!!!!!!!!

tca=TCA('BL18I-EA-DET-05:tca1')
tcasca1=tcasca('TCAsca1',"%4.3f",tca,"%",'1')
tcasca2=tcasca('TCAsca2',"%4.3f",tca,"%",'2')
tcasca3=tcasca('TCAsca3',"%4.3f",tca,"%",'3')  



class McaChannel( ScannableBase ):
	def __init__(self,name,mca):
		self.mca=mca
		self.setName(name)
		self.newpos=0
		self.maxpos=self.mca.getProperty('.NUSE')
		self.setInputNames(['Counts'])
		self.setOutputFormat(["%.0f"])
		self.needsRead = 1
		
	def atStart(self):
		self.mca.read()
		self.mca.wait()
		self.data=self.mca.getData()
		self.maxpos=self.mca.getProperty('.NUSE')
		
		
	def asynchronousMoveTo(self,newpos):
		if newpos < self.maxpos and newpos >=0:
			self.newpos=int(newpos)
		else:
			print "Error: newpos not correct"
			
			
	def isBusy(self):
		return 0


	def getPosition(self):
		return int(self.data[self.newpos])
		#return [self.newpos, int(self.data[self.newpos])]
		
#
# Modified MCA
#
class Mca(ScannableBase):
	def __init__(self,name,pvstring):
		self.setName(name)
		self.pvstring=pvstring
		self.setInputNames(['ROI1'])
		self.noOfROI=3
		self.channels = int(self.getProperty( '.NUSE' ))
		self.setOutputFormat( ['%.0f'] * self.noOfROI )
		self.setExtraNames(['ROI2','ROI3'])
		self.xxx = CAClient(pvstring+".VAL")
		self.xxx.configure()
		self.setLevel(9)
		
	def __del__(self):
		self.xxx.clearup()

	def setProperty(self,name,value):
        		caput(self.pvstring+name,value)

		
	def getProperty(self,name):
        		return caget(self.pvstring+name)
			
			
	def setDefaults(self):
		"""Set the MCA property to defaults values"""  
		self.setProperty('.NUSE',2048)
		self.setProperty('.PLTM',0)
		self.setProperty('.PRTM',0)
		self.setProperty('.PCTL',1)
		self.setProperty('.PCTH',0)
		self.setProperty('.PCT',0)
		self.setProperty('.HIGH',40)
		self.setProperty('.HIHI',70)
		self.setProperty('.MODE',0)
		self.setProperty('.CHAS',0)
		self.setProperty('.DWEL',0)
		self.setProperty('.PSCL',1)
		self.setProperty('Read.SCAN',1)
		self.setProperty('Status.SCAN',.1)
		self.setProperty('EnableWait',.1)

	#
	# Set ROI for a given index
	#
	def setROI(self,index,low,high):
		roilow=self.pvstring+'.R'+str(index)+'LO'
		roihigh=self.pvstring+'.R'+str(index)+'HI'
		self.setPropery(roilow,low)
		self.setPropery(roihigh,high)
	#
	# Get ROI for a given index
	#
	def getROI(self,index):
		roilow=self.pvstring+'.R'+str(index)+'LO'
		roihigh=self.pvstring+'.R'+str(index)+'HI'
		return [self.getPropery(roilow),self.setPropery(roihigh)]
		

	def start(self):
		"""Start the MCA data acquisiton"""
		self.setProperty('.STRT', 1)
		self.needsRead=1

	def ctime(self,ctime=None):
		"""Define the preset Live Time"""
		if ctime==None:
			return self.getProperty('.PLTM')
		self.setProperty('.PLTM', ctime)
		return self.getProperty('.PLTM')


	def stop(self):
		"""Stop The acquisition"""
		self.setProperty('.STOP', 1)

	def erase(self):
		"""Erase the spectra"""
		self.setProperty('.ERAS', 1)
		self.needsRead=1

	def read(self):
		"""Start data transfer from AIM"""
		self.setProperty('.READ', 1)
		self.needsRead=0

	def wait(self):
		"""Wait until transfer from AIM is done. This process is the bottleneck!"""
		while self.getProperty('.RDNG')=='1' or self.getProperty('.READ')=='1' :
			sleep(0.1)
			
	def getData(self):
		"""Transfer the data from EPICS to GDA"""
		return self.xxx.cagetArray()


	def atStart(self):
		"""Method used at the beginning of the scan, it stops and clears the MCA"""
		self.stop()
		self.erase()
		self.channels = int(self.getProperty( '.NUSE' ))
		self.setOutputFormat( ['%.0f'] * self.channels )
		self.setExtraNames(['Counts'] * (self.channels-1) )
		
	def asynchronousMoveTo(self,newpos):
		self.stop()
		self.erase()
		self.setProperty('.PRTM', newpos )
		self.start()
		while self.getProperty('.ACQG')=='0' :
			self.start()

	def prepareForCollection(self):
		self.stop()
		self.erase()
		self.setProperty('.PRTM', newpos )

	def setCollectionTime(self,collectionTime):
		self.setProperty('.PRTM',collectionTime)		

	def isBusy(self):
		if  self.getProperty('.ACQG')=='1':
			self.needsRead=1
			return 1
		else:
			return 0
		
	def getPosition(self):
		self.stop()
		if self.needsRead==1:
			self.read()
		self.wait()
		self.intdata=map(int,self.getData() )
	
		return self.intdata

	#def getPosition(self):
	#	self.stop()
	#	if self.needsRead==1:
	#		self.read()
	#	self.wait()
	#	for i in range()
	#	self.intdata=map(int,self.getData() )
	#	return self.intdata
			
	def setNoOfROI(self,noOfROI):
		self.noOfROI=noOfROI

mca2=Mca('MCA2','BL18I-EA-IONC-02:I:MCA')
mca1=Mca('MCA1','BL18I-EA-IONC-01:I:MCA')

 



