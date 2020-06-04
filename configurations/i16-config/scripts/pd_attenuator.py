from inttobin import *
from gda.epics import CAClient
import string 
import beamline_info as BLi
from gda.device.scannable import ScannableMotionBase

from time import sleep
from mathd import *


class Atten(ScannableMotionBase):

	def __init__(self,name,FoilList):
		self.setName(name)
		self.setInputNames(["Atten"])
		self.setExtraNames(["Transmission"])
		self.setOutputFormat(['%4.6f','%4.10f'])
		self.foils = FoilList
		self.Position = [0]*len(FoilList)
		self.bin=None
		#(robw- can fail if bad energy value) self.getPosition()

	def getTransmission(self,energy=None,numero=None):
		positions = self.Position
		#if numero==None:
		#	positions = self.Position
		#else:
		if numero != None:
			numero= int2bin(int(numero))
			for k in range(len(positions)):
				positions[k] = int(numero[k])
		#print positions
		self.transmission = 1.
		for k in range(len(self.foils)):
			if positions[k]==1:
				#if energy==None:
				#	self.transmission = self.transmission*self.foils[k].getTransmission()
				#else:
					self.transmission = self.transmission*self.foils[k].getTransmission(energy)
		#print "Transmission: %4.7f" %(self.transmission)
		return self.transmission

	def getPosition(self,energy=None):
		if self.bin == None:
			self.bin = 0
			for k in range(len(self.foils)):

				self.Position[k] = self.foils[k]()[0]
				if self.Position[k]==1:
					self.bin = self.bin+2**k
		else:
			pass
		self.getTransmission()
		#print "Transmission at %4.3f keV: %4.6f" %(BLi.getEnergy(), self.transmission)
		#return self.bin
		return [float(self.bin), self.transmission]

	def asynchronousMoveTo(self,numero):
		#self.new_position=int(new_position)
		#atten(self.new_position)
		self.bin=None
		stringa=int2bin(int(numero))
		if int(numero)>=2**len(self.foils):
			print "Error: number too high"
			return
		if len(stringa) != len(self.foils):
			print "Error: wrong length of input string"
		else:
			#To prevent damage, all insertions must be done before any removals
			for k in range(len(self.foils)):
				if stringa[k]=='1':
					try:
						#self.foils[len(self.foils)-1-k].(stringa[k])
						self.foils[len(self.foils)-1-k](1)
					except:
						print "Error: foil [%d] did not move" %k
			for k in range(len(self.foils)):
				if stringa[k]=='0':
					try:
						self.foils[len(self.foils)-1-k](0)
					except:
						print "Error: foil [%d] did not move" %k
		sleep(2)



	def isBusy(self):
		sleep(0.2)
		return 0
	
	
#def atten(numero=None):
#	if numero !=None:
#		try:
#			stringa=int2bin(numero)
#			Pb100u.move(stringa[0])
#			Al500u.move(stringa[1])
#			Al300u.move(stringa[2]) 
#			Al150u.move(stringa[3])
#			Al75u.move(stringa[4])
#			Al40u.move(stringa[5])
#			Al20u.move(stringa[6])
#			Al10u.move(stringa[7])
#			sleep(1)
#		except:
#			print "Error: The foils did not move"
#	print 	"Pb 100u %s, Al 500u %s,Al 300u %s, Al 150u %s,Al 75u %s, Al 40u %s,Al 20u %s, Al 10u %s" %(Pb100u.getPosition(),Al500u.getPosition(),Al300u.getPosition(),Al150u.getPosition(),Al75u.getPosition(),Al40u.getPosition(),Al20u.getPosition(),Al10u.getPosition())
#nominal	Al=[10,20,40,75,150,300,500]
#	Al=[10,20,40,80,150,300,500]    # real
#	Pb=100
#	aa=0	
#	if numero==None:
#		f1=(Al10u.getPosition()=='IN')
#		f2=(Al20u.getPosition()=='IN')
#		f3=(Al40u.getPosition()=='IN')
#		f4=(Al75u.getPosition()=='IN')
#		f5=(Al150u.getPosition()=='IN')
#		f6=(Al300u.getPosition()=='IN')
#		f7=(Al500u.getPosition()=='IN')
#		f8=(Pb100u.getPosition()=='IN')
#		aa= f1*Al[0]
#		aa= aa+f2*Al[1]
#		aa= aa+f3*Al[2]
#		aa= aa+f4*Al[3]
#		aa= aa+f5*Al[4]
#		aa= aa+f6*Al[5]
#		aa= aa+f7*Al[6]
#		bb= f8*Pb
#		att=str(f8)+str(f7)+str(f6)+str(f5)+str(f4)+str(f3)+str(f2)+str(f1)
#		print "Current atten is:",att
#	else:
##		print stringa
#		for i in range(7):
#			print int(stringa[7-i])
#			aa= aa+int(stringa[7-i])*Al[i]
#		bb=int(stringa[0])*Pb
#	trans1=Al10u.getTransmission()*Al20u.getTransmission()*Al40u.getTransmission()*Al75u.getTransmission()
#	trans2=Al150u.getTransmission()*Al300u.getTransmission()*Al500u.getTransmission()*Pb100u.getTransmission()
#	trans = trans1*trans2
#
#	print "Transmission at 7 keV: %4.7f" %(exp(-aa/55.26)*exp(-bb/2.74))
#	print "Transmission: %4.7f" %(trans)
#	return trans
#

