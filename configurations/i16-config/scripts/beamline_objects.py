#
# BLobjects.py
#
# Richard Woolliscroft Dec 2005
#
# This module makes the connection between the other modules and the beamline
# control software (GDA).  It holds links to the kappa motors
#
# If the simulation is switched off, then this module
# should be run within the GDA environment to creates objects references to
# motor control and set up the system.
#
# If the simulation is switched on, the the other modules rely on values which
# they hold themselves rather than real motor positions.
#


# I believe setting ,y_simulation is designes to let software run totally outside the gda
# In the process of being obsoleted.
my_simulation = 0
if my_simulation:
	print "WARNING: Simulataion mode set in beamline_objects.py.Some devices not loaded, and energy set from file"




import ShelveIO
BLO=ShelveIO.ShelveIO()
BLO.path=ShelveIO.ShelvePath+'BLobjects'
BLO.setSettingsFileName('BLobjects')

try:
	if BLO.getValue('ScatteringPlane') == None:
		BLO.ChangeValue('ScatteringPlane', "vertical")
except:
	BLO.ChangeValue('ScatteringPlane', "vertical")


#if self.isSimulation():
	#set up beamline specific things here
	#from gda.factory import Finder
	#from gda.jython.scannable import *
	#my_sixcircle = Finder.find("sixcircle")

	# create pseudo devices to allow scanning in reciprocal space

	# import EulerianPseudoDevice
	# reload(EulerianPseudoDevice)
	# import EulerianAxisPseudoDevice
	# reload(EulerianAxisPseudoDevice)

	# euler = EulerianPseudoDevice.EulerianPseudoDevice("euler")
	# phi = EulerianAxisPseudoDevice.EulerianAxisPseudoDevice("phi",euler)
	# chi = EulerianAxisPseudoDevice.EulerianAxisPseudoDevice("chi",euler)
	# theta = EulerianAxisPseudoDevice.EulerianAxisPseudoDevice("theta",euler)

	# my_theta = theta
	# my_chi = chi
	# my_phi = phi
	# my_euler = euler

# def getTheta():
	# return my_theta

# def getPhi():
	# return my_phi

# def getChi():
	# return my_chi

# def getEuler():
	# return my_euler

def isSimulation():
	return my_simulation
	
#returns true if any of the motors which are part of the diffractometer are busy
def isBusy():
	if isSimulation():
		return 0
	else:
		if my_kphi.isBusy():
			return 1
		if my_kap.isBusy():
			return 1
		if my_kth.isBusy():
			return 1
		if my_mu.isBusy():
			return 1
#		if my_delta.isBusy():
#			return 1
#		if my_gam.isBusy():
#			return 1

#		if my_wavelength.isBusy():
#			return 1
		else:
			return 0

#which motor represents two theta?
def setScatteringPlane(plane):

	if plane == "h" or plane == "horizontal" or plane == "horiz":
		BLO.ChangeValue('ScatteringPlane', "horizontal")
	elif plane == "v" or plane == "vertical" or plane == "vert":
		BLO.ChangeValue('ScatteringPlane', "vertical")
	else:
		print "Incorrect argument for setScatteringPlane().  Enter 'h' or 'v'."

def getScatteringPlane():
	try:
		return BLO.getValue('ScatteringPlane')
	except KeyError:
		setScatteringPlane('v')
#return the object reference to the pseudo device which acts as the two theta
def getScatteringPlaneDevice():

	if getScatteringPlane() == "horizontal":
		return my_gam
	elif getScatteringPlane() == "vertical":
		return my_delta

def getTth():
	return getScatteringPlaneDevice()

#these methods should only be accessed if isSimulation returns false
#they should be called by other modules needing real object references rather than
#values held in shelve files
def getKphi():
	return my_kphi

def getKap():
	return my_kap

def getKth():
	return my_kth

def getKmu():
	return my_mu

def getDelta():
	return my_delta

def getGam():
	return my_gam

def getsgomega():
	return my_smaromega

def getsgchi():
	return my_smarchi

def getsgphi():
	return my_smarphi


#
# Return a Pesudo Device which holds the wavelength of the system.
#
#def getWavelength():
	#return my_wavelength




