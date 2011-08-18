from java.io import DataInputStream
from java.io import FileInputStream
import jarray
from time import sleep
from gda.device.xspress import Xspress2Utilities
import random


def getDetectorMonitorCounts():
	xspress = finder.find("xspress2system")
	lock =0
	try:
		#print 'locking xspress'
		#lock = xspress.lockXspress()
		#if not lock:
		#	print "Xspress detector is already locked"
		#	return
		sleep(1)
		scalarString = readScalerfromMemory()
		#print scalarString
		scalarData=[]
		for j in range(3):
			scalarData.append(range(9))
		k=0
		for i in range(9):
			for j in range(3):
				scalarData[j][i]=int(scalarString[k])
				k=k+1
		return scalarData
	
	finally :
		if(lock):
			print 'unlocking xspress'
			xspress.unlockXspress()
	
def readScalerfromMemory():
	scalarstring =[]
	for i in range(27):
		scalarstring.append(str(random.randint(0, 300000)))
	return scalarstring
	
def readScalarDataFile(scalarfile):
	scalarData=[] 
	for j in range(3):
		scalarData.append(range(9))
	fis =FileInputStream(scalarfile)
	dis =DataInputStream(fis)
	scalerBytes =jarray.zeros(27*4,'b')
	dis.read(scalerBytes, 0, 27*4)
	fis.close()
	offset = 0
	for l in range(9):
		for j in range(0,12,4):
			scalarData[j/4][l]= (0x000000FF & scalerBytes[offset+j+0]) + ((0x000000FF & scalerBytes[offset+j+1])<<8)+((0x000000FF & scalerBytes[offset+j+2])<<16)+((0x000000FF & scalerBytes[offset+j+3])<<24)
		offset=offset+12
	fis.close()
	corrWindows=Xspress2Utilities.deadTimeCorrectWindows(scalarData,1000.0/1000.0)
	totalW=Xspress2Utilities.getWindowTotal()
	print corrWindows
	print totalW
	return scalarData
