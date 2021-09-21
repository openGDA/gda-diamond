import math;
from time import sleep
from Diamond.PseudoDevices.CorrespondentDevice import CorrespondentDeviceClass
print "Enable polarization selection"
print "Available options:"
print "     0   -->    horizontal polarization"
print "     1   -->    vertical polarization"
print "     2   -->    positive circular polarization"
print "     3   -->    negative circular polarization"
print "     4   -->    unknow polarization"
print " "
print "Example  -->    pos selPol 2"

global iddtrp, iddbrp, iddgap,pgmenergy

def iddrpWait(targetValue,targetError):
	targetReachedTop = 0
	targetReachedBottom = 0
	while 1:
		if abs(iddtrp.getPosition()-targetValue) >= targetError:
			print "iddtrp ==> ", abs(iddtrp.getPosition()-targetValue), " mm to target"
		else:
			targetReachedTop  = targetReachedTop  + 1
			sleep(2)
		if abs(iddbrp.getPosition()-targetValue) >= targetError:
			print "iddbrp ==> ", abs(iddbrp.getPosition()-targetValue), " mm to target"
		else:
			targetReachedBottom  = targetReachedBottom + 1
			sleep(2)
		if targetReachedBottom >= 1:
			if targetReachedTop >= 1:
				break
		sleep(0.2)
	sleep(1)

def iddtrpWait(targetValue,targetError):
	while abs(iddtrp.getPosition()-targetValue) >= targetError:
		print abs(iddtrp.getPosition()-targetValue), " mm to target"
		sleep(0.2)
	sleep(0.5)

def iddbrpWait(targetValue,targetError):
	while abs(iddbrp.getPosition()-targetValue) >= targetError:
		print abs(iddbrp.getPosition()-targetValue), " mm to target"
		sleep(0.2)
	sleep(0.5)


####################################################################################
#Enable the Downstream undulator Gap control via Energy

selPol= CorrespondentDeviceClass("selPol", 0.0, 4.0, "testMotor1","returnFunction", "inputFunction");

def inputFunction(selection):
	brp = iddtrp.getPosition()
	trp = iddbrp.getPosition()
	mm = iddgap.getPosition()
	energy = pgmenergy.getPosition()
	selection = float(selection)
	if selection == 0.0:
		print "Move to  -->  horizontal polarization"
		iddtrp.moveTo(0.0)
		sleep(1)
		iddbrp.moveTo(0.0)
		iddbrpWait(0.0,0.1)
	elif selection == 1.0:
		print "Move to  -->  vertical polarization"
		iddtrp.moveTo(32.0)
		sleep(1)
		iddbrp.moveTo(-32.0)
		iddbrpWait(-32.0,0.1)
	elif selection == 2.0:
		print "Move to  -->  positive circular polarization"
		rp = 12.36919+0.656 * mm-0.02055 * mm**2+3.88289E-4 * mm**3-3.01253E-6 * mm**4
		iddtrp.moveTo(rp)
		sleep(1)
		iddbrp.moveTo(rp)
		iddrpWait(rp,0.01)
	elif selection == 3.0:
		print "Move to  -->  negativecircular polarization"
		rpTemp = 12.36919+0.656 * mm-0.02055 * mm**2+3.88289E-4 * mm**3-3.01253E-6 * mm**4
		rp = -rpTemp
		iddtrp.moveTo(rp)
		sleep(1)
		iddbrp.moveTo(rp)
		iddrpWait(rp,0.01)
	else:
		print "Wrong entry value"
	return selection

def returnFunction(selection):
	brp = iddtrp.getPosition()
	trp = iddbrp.getPosition()
	if abs(brp-trp) < 0.1:
		if brp > 0.1:
			selection = 2.0
		elif brp < -0.1:
			selection = 3.0
		else:
			selection = 0.0
	elif abs(brp-32) < 0.1:
		if abs(trp+32) < 0.1:
			selection = 1.0
	elif abs(brp+32) < 0.1:
		if abs(trp-32) < 0.1:
			selection = 1.0
	elif brp > 0.0:
		if trp < 0.0:
			print "Unknown polarisation settings"
			selection = 4
	elif brp < 0.0:
		if trp > 0.0:
			print "Unknown polarisation settings"
			selection = 4
	else:
			print "Unknown polarisation settings"
			selection = 4
	return selection;

