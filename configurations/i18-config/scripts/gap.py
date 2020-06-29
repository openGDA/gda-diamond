import threading
from time import sleep
from gda.jython import InterfaceProvider
from gda.factory import Finder
import datetime
from gda.epics import CAClient
import math


class ThreadClass(threading.Thread):

	def __init__(self):
		super(ThreadClass, self).__init__()
		lutFile = "/dls_sw/i18/software/gda/config/lookupTables/lookuptable_harmonic9_240908.txt"

		self.PVmonoAngle = CAClient("BL18I-OP-DCM-01:BRAGG.RBV")
		self.PVmonoAngle.configure()
		
		self.PVGap = CAClient("SR18I-MO-SERVC-01:BLGAPMTR.VAL")
		self.PVGap.configure()
		#PVgap = CAClient("")
		#PVgap.configure()
		#print int(abs(float(self.PVmonoAngle.caget())*1000))
		
		try: 
			f = open(lutFile, "r")
		#	for line in f:
		#		print line,
			lines = f.readlines()
		except IOError,e:
			print e
		finally:
			try: 
				f.close()
			except: 
				pass	# can't do any
			
		#print lines
		
		lines = lines[2:]
		#print lines
		
		lutList = []
		self.angle = []
		self.gap = []
		for line in lines:
			temp = [float(i) for i in line.split()]
			lutList.append(temp)
			self.angle.append(temp[0])
			self.gap.append(temp[1])
			
		
		self.curr_angle = int(abs(float(self.PVmonoAngle.caget())*1000))
		print "curr_angle=",self.curr_angle
		indexi =  self.angle.index(min(self.angle, key=lambda x:abs(x-self.curr_angle)))
		self.sc_idgap=Finder.find("sc_idgap")
		self.sc_idgap(self.gap[indexi])
		
	def stop(self):
		print "self.gap thread stopped"
		
	def stopped(self):
		return self._stop.isSet()
	
	# add method to run indepenent of qexafs and specify filename
	def run(self):
		print "self.gap thread to start running"
		while True:
			#print "in while"
			new_angle = int(abs(float(self.PVmonoAngle.caget())*1000))
			#print "new angle calculated"
			if abs(new_angle - self.curr_angle) >= 1:
				#print str(new_angle)
				#print str(self.curr_angle)
				print "abs(new_angle - self.curr_angle)",abs(new_angle - self.curr_angle)
				self.curr_angle = new_angle
				indexi =  self.angle.index(min(self.angle, key=lambda x:abs(x-self.curr_angle)))
				#print "indexi=", str(indexi)
				self.PVGap.caput(self.gap[indexi])
				#print "PVGap set"
