from java.lang import *
from jarray import *
from time import sleep
		
#
# A Script for collecting Vortex deadtime correction related parameters
#
class VortexDTCParams:
	def __init__(self):
		xmapstring = "BL18I-EA-DET-04:DXP"
		self.channels=[]
		basetring=''
		for i in range(4):
			basestring=xmapstring+str(i)+":DATA:"
			self.channels.append(CAClient(basestring+"ICR"))			
			self.channels[-1].configure()
		for i in range(4):
			basestring=xmapstring+str(i)+":DATA:"
			self.channels.append(CAClient(basestring+"OCR"))			
			self.channels[-1].configure()


	def getVortexDTCParams(self):
		results=[]
		for channel in self.channels:
			if not channel.isConfigured():
				channel.configure()
				val=float(channel.caget())
				results.append(val)
				channel.clearup()
			else:
				val=float(channel.caget())
				results.append(val)
		return results
		


	def dumpVortexDTCParamsToFile(self,filename):
		results=[]
		for channel in self.channels:
			if not channel.isConfigured():
				channel.configure()
				val=float(channel.caget())
				results.append(val)
				channel.clearup()
			else:
				val=float(channel.caget())
				results.append(val)
		fout=open(filename,"w")
		print >> fout,str(results[0:]).strip('[]').replace(',','')
		fout.close()
		return results
		
vortexDTCparameters=VortexDTCParams()

