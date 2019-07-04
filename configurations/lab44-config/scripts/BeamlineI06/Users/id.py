import math;
print "Enable the control of I06 Insertion Devices via Energy setting"
print "-------------------Example-----------------------"
print "pos iddenergy  400"
print "pos iddrpenergy 400"
print "--------------------Result-----------------------"

def iddrpWait(targetValue,targetError):
	targetReachedTop = 0
	targetReachedBottom = 0
	while 1:
		if abs(iddtrp.getPosition()-targetValue) >= targetError:
			print "iddtrp ==> ", abs(iddtrp.getPosition()-targetValue), " mm to target"
		else:
			targetReachedTop  = targetReachedTop  + 1
			sleep(0.1)
		if abs(iddbrp.getPosition()-targetValue) >= targetError:
			print "iddbrp ==> ", abs(iddbrp.getPosition()-targetValue), " mm to target"
		else:
			targetReachedBottom  = targetReachedBottom + 1
			sleep(0.1)
		if targetReachedBottom >= 1:
			if targetReachedTop >= 1:
				sleep(1)
				break
		sleep(0.2)

def iddtrpWait(targetValue,targetError):
	while abs(iddtrp.getPosition()-targetValue) >= targetError:
		print abs(iddtrp.getPosition()-targetValue), " mm to target"
		sleep(0.2)
	sleep(2)

def iddbrpWait(targetValue,targetError):
	while abs(iddbrp.getPosition()-targetValue) >= targetError:
		print abs(iddbrp.getPosition()-targetValue), " mm to target"
		sleep(0.2)
	sleep(2)

#Define functions for each type of gap movement vs polarisation
def eV_to_mmPosCirc(eVinput):
	eV = float(eVinput)
	P1 = 21.84361986821063
	P2 = -0.2003836758955337
	P3 = 0.002291136605289847
	P4 = -1.088881076307586E-5
	P5 = 2.989789974084859E-8
	P6 = -5.073100951682625E-11
	P7 = 5.358876793295571E-14
	P8 = -3.383513881935705E-17
	P9 = 1.138966261140803E-20
	P10 = -1.488400114824732E-24
	mm = P1+P2*eV+P3*eV**2+P4*eV**3+P5*eV**4 + P6*eV**5 + P7*eV**6 + P8*eV**7 + P9*eV**8 + P10*eV**9
	return mm
def eV_to_mmNegCirc(eVinput):
	eV = float(eVinput)
	P1 = -695.5507395154041
	P2 = 12.21996196047702
	P3 = -0.0915320243718321
	P4 = 3.953166642060013E-4
	P5 = -1.081841042523599E-6
	P6 = 1.945726427754425E-9
	P7 = -2.300919991711818E-12
	P8 = 1.726091664151633E-15
	P9 = -7.457589077419326E-19
	P10 = 1.414534248725179E-22
	mm = P1+P2*eV+P3*eV**2+P4*eV**3+P5*eV**4 + P6*eV**5 + P7*eV**6 + P8*eV**7 + P9*eV**8 + P10*eV**9
	return mm
def eV_to_mmHorizontal(eVinput):
	eV = float(eVinput)
	P1 = 5.048311024081E1
	P2 = -4.527831259772E-1
	P3 = 3.182108172734E-3
	P4 = -1.091152188016E-5
	P5 = 2.205820876532E-8
	P6 = -2.731496059207E-11
	P7 = 2.038120569673E-14
	P8 = -8.416619176957E-18
	P9 = 1.479337928900E-21
	mm = P1+P2*eV+P3*eV**2+P4*eV**3+P5*eV**4 + P6*eV**5 + P7*eV**6 + P8*eV**7 + P9*eV**8
	return mm
def eV_to_mmVertical(eVinput):
	eV = float(eVinput)
	P1 = 1.170564513640E1
	P2 = 1.346839969658E-2
	P3 = 2.708516839446E-4
	P4 = -1.263866964149E-6
	P5 = 2.980395821007E-9
	P6 = -4.114956015538E-12
	P7 = 3.370964180767E-15
	P8 = -1.520025404071E-18
	P9 = 2.920658237205E-22
	mm = P1+P2*eV+P3*eV**2+P4*eV**3+P5*eV**4 + P6*eV**5 + P7*eV**6 + P8*eV**7 + P9*eV**8
	return mm
def mm_to_eVPosCirc(mminput):
	mm = float(mminput)
	P1 = -430958.9687318461
	P2 = 98317.83845378432
	P3 = -9310.767773648086
	P4 = 456.8175210174009
	P5 = -10.93856555010642
	P6 = 0.01761477508177703
	P7 = 0.00622321138919677
	P8 = -1.681703705880674E-4
	P9 = 1.940856876694135E-6
	P10 = -8.76566273818261E-9
	eV = P1 + P2 *mm+P3 *mm**2+P4 *mm**3+P5 *mm**4 +P6 *mm**5 +P7 *mm**6 +P8 *mm**7 +P9 *mm**8 +P10 *mm**9
	return eV;
def mm_to_eVNegCirc(mminput):
	mm = float(mminput)
	P1 = 1177741.058697857
	P2 = -253610.2374075396
	P3 = 22381.09958182648
	P4 = -988.2317843081472
	P5 = 18.16208592112800
	P6 = 0.2410482165652461
	P7 = -0.02023963393821341
	P8 = 4.517469238395192E-4
	P9 = -4.754251099903418E-6
	P10 = 2.010762748937732E-8
	eV = P1 + P2 *mm+P3 *mm**2+P4 *mm**3+P5 *mm**4 +P6 *mm**5 +P7 *mm**6 +P8 *mm**7 +P9 *mm**8 +P10 *mm**9
	return eV;
def mm_to_eVHorizontal(mminput):
	mm = float(mminput)
	P1 = 1.858841333202E4
	P2 = -3.206914808115E3
	P3 = 2.389954957716E2
	P4 = -9.998107367567E0
	P5 = 2.567821562465E-1
	P6 = -4.123946902279E-3
	P7 = 4.037850109977E-5
	P8 = -2.206004764242E-7
	P9 = 5.159487410806E-10
	eV = P1 + P2 *mm+P3 *mm**2+P4 *mm**3+P5 *mm**4 +P6 *mm**5 +P7 *mm**6 +P8 *mm**7 +P9 *mm**8
	return eV;
def mm_to_eVVertical(mminput):
	mm = float(mminput)
	P1 =-847.7841258746101
	P2 = 172.7118786422540
	P3 = -13.28051081731081
	P4 = 0.5295755936772300
	P5 = -0.00929682947261154
	P6 = 5.934495192308022E-5
	eV = P1 + P2 *mm+P3 *mm**2+P4 *mm**3+P5 *mm**4 +P6 *mm**5
	return eV;

####################################################################################
#Enable the Downstream undulator Gap control via Energy

iddenergy = CorrespondentDeviceClass("iddenergy", 200.0, 1300.0, "iddgap","mm_to_eV", "eV_to_mm");
iddrpenergy = CorrespondentDeviceClass("iddrpenergy", 200.0, 1300.0, "iddgap","mm_to_eVrp", "eV_to_mmrp");

#Function must:
#--> Measure position of RP and determine polarization condition, thus polynomial to use
#--> Calculate undulator gap as a function of energy for appropriate RP
#--> input: energy (eV)
#--> output: undulator gap (mm)

def eV_to_mm(eVinput):
	brp = iddtrp.getPosition()
	trp = iddbrp.getPosition()
	gap = iddgap.getPosition()
	if abs(brp-trp) < 0.1:
		if brp > 0.1:
			mm = eV_to_mmPosCirc(eVinput)
		elif brp < -0.1:
			mm = eV_to_mmNegCirc(eVinput)
		else:
			mm = eV_to_mmHorizontal(eVinput)
	elif abs(brp-32) < 0.1:
		if abs(trp+32) < 0.1:
			mm = eV_to_mmVertical(eVinput)
	elif abs(brp+32) < 0.1:
		if abs(trp-32) < 0.1:
			mm = eV_to_mmVertical(eVinput)
	elif brp > 0.0:
		if trp < 0.0:
			mm = gap
	elif brp < 0.0:
		if trp > 0.0:
			mm = gap
	else:
		print "Error reading RP positions!"
		mm = gap
	return mm

#Function must:
#--> Measure position of RP and determine polarization condition, thus polynomial to use
#--> Calculate undulator gap as a function of energy for appropriate RP
#--> input: energy (eV)
#--> output: undulator gap (mm)

def mm_to_eV(mminput):
	brp = iddtrp.getPosition()
	trp = iddbrp.getPosition()
	energy = pgmenergy.getPosition()
	if abs(brp-trp) < 0.1:
		if brp > 0.1:
			eV = mm_to_eVPosCirc(mminput)
		elif brp < -0.1:
			eV = mm_to_eVNegCirc(mminput)
		else:
			eV = mm_to_eVHorizontal(mminput)
	elif abs(brp-32) < 0.1:
		if abs(trp+32) < 0.1:
			eV = mm_to_eVVertical(mminput)
	elif abs(brp+32) < 0.1:
		if abs(trp-32) < 0.1:
			eV = mm_to_eVVertical(mminput)
	elif brp > 0.0:
		if trp < 0.0:
			print "Polarisation not ready! (wrong energy readback)"
			eV = energy
	elif brp < 0.0:
		if trp > 0.0:
			print "Polarisation not ready! (wrong energy readback)"
			eV = energy
	else:
		print "Error reading RP positions!"
		eV = energy
	return eV;

###################################################################################

def eV_to_mmrp(eVinput):
	brp = iddtrp.getPosition()
	trp = iddbrp.getPosition()
	gap = iddgap.getPosition()
	A0 = 9.339571708466E0
	A1 = 1.209037698066E0
	A2 = -6.109333492521E-2
	A3 = 1.916688241616E-3
	A4 = -3.402925759270E-5
	A5 = 3.140701220987E-7
	A6 = -1.168975158856E-9
	A7 = 3.705325695106E-14
	A8 = -3.497119951560E-16
	if abs(brp-trp) < 0.1:
		if brp > 0.1:
			mm = eV_to_mmPosCirc(eVinput)
			rp = 12.36919+0.656 * mm-0.02055 * mm**2+3.88289E-4 * mm**3-3.01253E-6 * mm**4
			#rp = A0 + A1 * mm + A2 * mm**2+ A3 * mm**3 + A4 * mm**4 + A5 * mm**5 + A6 * mm**6 + A7 * mm**7 + A8 * mm**8
			iddtrp.moveTo(rp)
			sleep(1)
			iddbrp.moveTo(rp)
			iddrpWait(rp,0.01)
		elif brp < -0.1:
			mm = eV_to_mmNegCirc(eVinput)
			rpTemp = 12.36919+0.656 * mm-0.02055 * mm**2+3.88289E-4 * mm**3-3.01253E-6 * mm**4
			#rpTemp = A0 + A1 * mm + A2 * mm**2+ A3 * mm**3 + A4 * mm**4 + A5 * mm**5 + A6 * mm**6 + A7 * mm**7 + A8 * mm**8
			rp = -rpTemp
			iddtrp.moveTo(rp)
			sleep(1)
			iddbrp.moveTo(rp)
			iddrpWait(rp,0.01)
		else:
			mm = eV_to_mmHorizontal(eVinput)
	elif abs(brp-32) < 0.1:
		if abs(trp+32) < 0.1:
			mm = eV_to_mmVertical(eVinput)
	elif abs(brp+32) < 0.1:
		if abs(trp-32) < 0.1:
			mm = eV_to_mmVertical(eVinput)
	elif brp > 0.0:
		if trp < 0.0:
			print "Polarisation not ready!"
			mm = gap
	elif brp < 0.0:
		if trp > 0.0:
			print "Polarisation not ready!"
			mm = gap
	else:
		print "Error reading RP positions!"
		mm = gap
	return mm

#Function must:
#--> Measure position of RP and determine polarization condition, thus polynomial to use
#--> Calculate undulator gap as a function of energy for appropriate RP
#--> input: energy (eV)
#--> output: undulator gap (mm)

def mm_to_eVrp(mminput):
	brp = iddtrp.getPosition()
	trp = iddbrp.getPosition()
	energy = pgmenergy.getPosition()
	if abs(brp-trp) < 0.1:
		if brp > 0.1:
			eV = mm_to_eVPosCirc(mminput)
		elif brp < 0.1:
			eV = mm_to_eVNegCirc(mminput)
		else:
			eV = mm_to_eVHorizontal(mminput)
	elif abs(brp-32) < 0.1:
		if abs(trp+32) < 0.1:
			eV = mm_to_eVVertical(mminput)
	elif abs(brp+32) < 0.1:
		if abs(trp-32) < 0.1:
			eV = mm_to_eVVertical(mminput)
	elif brp > 0.0:
		if trp < 0.0:
			print "Polarisation not ready! (wrong energy readback)"
			eV = energy
	elif brp < 0.0:
		if trp > 0.0:
			print "Polarisation not ready! (wrong energy readback)"
			eV = energy
	else:
		print "Error reading RP positions!"
		eV = energy
	return eV;

###################################################################################

