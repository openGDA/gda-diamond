from java.io import DataInputStream
from java.io import FileInputStream
import jarray
from time import sleep
from gda.device.xspress import Xspress2Utilities


def getDetectorCounts():
	das=finder.find("daserver")
	# clear the detector
	das.sendCommand("disable 0")
	das.sendCommand("clear 0")
	das.sendCommand("enable 0")
	# start the tfg
	das.sendCommand("tfg init")
	command = "tfg setup-groups cycles 1 \n1 0.01 1.0 0 1 0 0 \n-1 0 0 0 0 0 0 "
	das.sendCommand(command)
	das.sendCommand("tfg start")
#	das.sendCommand("tfg cont")
	das.sendCommand("tfg wait")
	# disable the detector
	das.sendCommand("disable 0")
	# now read in from da server
	das.sendCommand("read 0 0 0 3 9 1 from 1 to-local-file \"/dls/i18/tmp/pdq_scalers_test2.dat\" raw intel")
	#
	# Now type the following in a linux terminal window to get the counts per second
	# od -td4 -Ax4 /dls/i18/tmp/pdq_scalers1.dat
	#
	#
	#
	# now read scalar data
	# 
	scalarData=[] 
	for j in range(3):
		scalarData.append(range(9))
	fis =FileInputStream("/dls/i18/tmp/pdq_scalers_test2.dat")
	dis =DataInputStream(fis)
	scalerBytes =jarray.zeros(27*4,'b')
	dis.read(scalerBytes, 0, 27*4)
	offset = 0

	for l in range(9):
		for j in range(0,12,4):
			scalarData[j/4][l]= (0x000000FF & scalerBytes[offset+j+0]) + ((0x000000FF & scalerBytes[offset+j+1])<<8)+((0x000000FF & scalerBytes[offset+j+2])<<16)+((0x000000FF & scalerBytes[offset+j+3])<<24)
			#print 'pos',l,j,offset+j
		offset=offset+12

	dis.close()	
	return scalarData

def getDetectorMonitorCounts():
	das=finder.find("daserver")
	# clear the detector
	das.sendCommand("disable 0")
	das.sendCommand("clear 0")
	das.sendCommand("enable 0")
	# start the tfg
	das.sendCommand("tfg init")
	command = "tfg setup-groups cycles 1 \n1 0.01 1.0 0 7 0 0 \n-1 0 0 0 0 0 0 "
	das.sendCommand(command)
	das.sendCommand("tfg start")
#	das.sendCommand("tfg cont")
	sleep(0.9)
	das.sendCommand("tfg wait")
	# disable the detector
	das.sendCommand("disable 0")
	scalarString=das.getData("read 0 0 0 3 9 1 from 1")
	scalarData=[]
	for j in range(3):
		scalarData.append(range(9))
	k=0
	for i in range(9):
		for j in range(3):
			scalarData[j][i]=int(scalarString[k])
			k=k+1
	print 'Detector counts per second per channel', scalarData[0]
	return scalarData

def readScalerfromMemory():
	das=finder.find("daserver")
	scalarString=das.getData("read 0 0 0 3 9 1 from 1")
	print scalarString
	#scalarString=['40', '4114', '0', '10', '2657', '0', '12', '3064', '0', '2', '2635', '0', '3', '2627', '0', '5', '2830', '0', '218', '31987', '0', '17', '3119', '0', '936', '158804', '0']
	scalarData=[]
	for j in range(3):
		scalarData.append(range(9))
	k=0
	for i in range(9):
		for j in range(3):
			scalarData[j][i]=int(scalarString[k])
			k=k+1
	return scalarData
	
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
