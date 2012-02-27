##
## Functions required for scanning with ccd using XPS Position Compare
##
from gdascripts.messages import handle_messages
from gdascripts.messages.handle_messages import simpleLog
from gdascripts.parameters import beamline_parameters

global configured, beamline, ruby
configured = False
def configure(jythonNameMap, beamlineParameters):
	global configured, beamline, ruby
	"""
	sets module variables from jython namespace, finder and beamline parameters
	"""
	beamline = jythonNameMap.beamline
	ruby = jythonNameMap.ruby
	configured = True
	
def checkConfigured():
	if not configured:
		raise "ccdMechanics not configured"
		
######################################################################################
def scanGeometry(axis, velocity, A, B):
	"""
	Gets geometry string for Crysalis header, sets motor velocity and activates position compare
	"""
	geometry = getGeometry(axis, velocity, A, B)
	setVelocity(axis, velocity)

	correctedA = A
	correctedB = B
	suffix = ""
	
	velocityMinimumWithoutDebounce_DegPerSec = 0.1
	velocityMinimumWithDebounce_DegPerSec = 0.0002
	
	if velocity >= velocityMinimumWithoutDebounce_DegPerSec:
		debounce = 0 # False
	
	elif velocity >= velocityMinimumWithDebounce_DegPerSec:
		debounce = 1 # True
		# If the debounce circuit is enabled, then we need to shorten the
		# position compare by the length of time the stretcher stretches the
		# pulse. Note if step is -ve then we have to correct A instead.
		stretchedPulseLengthMs = 1100.
		if (A > B):
			correctedA = A + (velocity*stretchedPulseLengthMs/1000)
		else:
			correctedB = B - (velocity*stretchedPulseLengthMs/1000)
		suffix = "(corrected from A, B = %f %f)" % (A, B)
		if correctedA > correctedB:
			raise "Error: Move is either too short or too slow, so the " + \
				"start position (%f) is after the end position (%f)" % (
				correctedA, correctedB) + "with de-bounce correction! " + \
				"Moves must take more than %f ms with velocities below %f." % (
				stretchedPulseLengthMs, velocityMinimumWithoutDebounce_DegPerSec)
	
	else:
		raise "Error: velocity (%f) is below minimum supported velocity (%f)" \
			% (velocity, velocityMinimumWithDebounce_DegPerSec)
	
	debounce_current = beamline.getValue(None, "Top", "-EA-PCMP-01:STRETCH")
	if debounce <> debounce_current:
		simpleLog("Debounce circuit currently %r , needs to be %r " %
			(debounce_current, debounce))
		simpleLog("""NOTE:
			If the next line doesn't start 'Activating position compare'
			then try setting manually in Launcher, Beamlines, I15,
			Experimental Hutch, SMPL2, Position Compare""")
		
		beamline.setValue("Top", "-EA-PCMP-01:STRETCH", debounce)
		suffix += "(set debounce to %r)" % debounce
	
	simpleLog("Activating position compare: A, B, axis = %f %f %s %s" %
			(correctedA, correctedB, axis.name, suffix))
	
	activatePositionCompare(correctedA, correctedB, axis)
	
	return geometry
######################################################################################
def getGeometry(axis, velocity, A, B):
	
	"""
	Returns string of motor positions and velocities and detector distance to be written to the Crysalis data header
	"""
	checkConfigured()
	# Set start, stop and velocity values for all axes
	phiStart = phiStop = beamline.getValue(None,"Top","-MO-DIFF-01:SAMPLE:KPHI.RBV")
	kappaStart = kappaStop = beamline.getValue(None,"Top","-MO-DIFF-01:SAMPLE:KAPPA.RBV")
	omegaStart = omegaStop = float(beamline.getValue(None,"Top","-MO-DIFF-01:SAMPLE:KTHETA.RBV") + 90.0)
	twothetaStart = twothetaStop = beamline.getValue(None,"Top","-MO-DIFF-01:ARM:DELTA.RBV")
	gammaStart = gammaStop = beamline.getValue(None,"Top","-MO-DIFF-01:ARM:GAMMA.RBV")
	muStart = muStop = beamline.getValue(None,"Top","-MO-DIFF-01:SAMPLE:MU.RBV")
	
	phiVel = kappaVel = omegaVel = twothetaVel = gammaVel = 0

	# Set start, stop and velocity for axis to be moved
	if (axis.name =='dkphi' or axis.name == 'testLinearDOF1'):
		phiStart = A
		phiStop = B
		phiVel = velocity
	elif (axis.name =='dktheta'):
		omegaStart = A + 90.0
		omegaStop = B + 90.0
		omegaVel = velocity
	elif (axis.name =='dkappa'):
		kappaStart = A
		kappaStop = B
		kappaVel = velocity
	elif (axis.name =='ddelta'):
		twothetaStart = A
		twothetaStop = B
		twothetaVel = velocity
	elif (axis.name =='dmu'):
		muStart = A
		muStop = B
		muVel = velocity
	elif (axis.name =='dgamma'):
		gammaStart = A
		gammaStop = B
		gammaVel = velocity
		
	
	else:
		raise "Error: axis (%s) not valid in scan" % axis.name
	
	# Return formatted geometry string 
	geometry = '%.3f %.3f %.4f %.3f %.3f %.4f %.3f %.3f %.4f %.3f %.3f %.4f %.3f %.3f %.4f ' % (phiStart, phiStop, phiVel, 
																								kappaStart, kappaStop, kappaVel, 
																								omegaStart, omegaStop, omegaVel, 
																								twothetaStart, twothetaStop, twothetaVel, 
																								gammaStart, gammaStop, gammaVel)
	return geometry + str(ruby.detectorDistance)

######################################################################################
def activatePositionCompare(start, stop, axis):
	"""
	Sets up position compare to be triggered on axis between start and stop positions
		e.g. activatePositionCompare(-122, -121, dkphi)
	"""
	checkConfigured()
	if axis.getName() == "testLinearDOF1":
		return	
	# Get offset value	
#	PCOOffset = 0
	PCOOffset = beamline.getValue(None, "Top", getVelocityPvRoot(axis) + ".OFF")
	if (PCOOffset > 0):
		simpleLog("Offset for " + axis.name + " is: " + str(PCOOffset))

	pvRoot = ""
	if (axis.name =='dkphi'):
		pvRoot = '-MO-XPS-02:PCO6'
	elif (axis.name =='dktheta'):
		pvRoot = '-MO-XPS-02:PCO4'
	elif (axis.name =='ddelta'):
		pvRoot = '-MO-XPS-02:PCO2'
	elif (axis.name =='dgamma'):
		pvRoot = '-MO-XPS-02:PCO1'
	elif (axis.name =='dmu'):
		pvRoot = '-MO-XPS-02:PCO3'
	elif (axis.name =='dkappa'):
		pvRoot = '-MO-XPS-02:PCO5'
	else:
		raise "Error: axis (%s) not valid in scan" % axis.name

	beamline.setValue("Top", pvRoot + ":ENABLE", 0)					   #Deactivate position compare
	beamline.setValue("Top", pvRoot + ":START", start - PCOOffset)	   	#Set Start of position compare
	beamline.setValue("Top", pvRoot + ":END", stop - PCOOffset)		   #Set End of position compare
	beamline.setValue("Top", pvRoot + ":SEND.PROC", 1)				   #Write `this data to XPS box.
	beamline.setValue("Top", pvRoot + ":ENABLE", 1)					   #Activate position compare
######################################################################################
def setVelocity(axis, velocity):
	"""
	Sets the velocity on axis
	"""
	if axis.getName() == "testLinearDOF1":
		return
	checkConfigured()
	pvRoot = getVelocityPvRoot(axis)
	beamline.setValue("Top", pvRoot + ".VELO", velocity)
	
######################################################################################
def setMaxVelocity(axis):
	"""
	Sets the maximum velocity on axis
	"""
	if axis.getName() == "testLinearDOF1":
		return
	checkConfigured()
	pvRoot = getVelocityPvRoot(axis)
	maxVelocity = beamline.getValue(None, "Top", pvRoot + ".VMAX")
	beamline.setValue("Top", pvRoot + ".VELO", maxVelocity)

######################################################################################
def getVelocityPvRoot(axis):
	"""
	Gets pv root for setting axis velocity
	"""
	if (axis.name == 'dkphi'):
		return "-MO-DIFF-01:SAMPLE:KPHI"
	elif (axis.name == 'dktheta'):
		return "-MO-DIFF-01:SAMPLE:KTHETA"
	elif (axis.name == 'ddelta'):
		return "-MO-DIFF-01:ARM:DELTA"
	elif (axis.name == 'dgamma'):
		return "-MO-DIFF-01:ARM:GAMMA"
	elif (axis.name == 'dkappa'):
		return "-MO-DIFF-01:SAMPLE:KAPPA"
	elif (axis.name == 'dmu'):
		return "-MO-DIFF-01:SAMPLE:MU"

	raise "Error: axis (%s) not valid in scan" % axis.name
######################################################################################
def deactivatePositionCompare():
	"""
	Deactivates all position compare function.
	"""
	checkConfigured()
	beamline.setValue("Top","-MO-XPS-02:PCO1:ENABLE",0)			#Deactivate gamma position compare
	beamline.setValue("Top","-MO-XPS-02:PCO2:ENABLE",0)			#Deactivate delta position compare
	beamline.setValue("Top","-MO-XPS-02:PCO4:ENABLE",0)			#Deactivate ktheta position compare
	beamline.setValue("Top","-MO-XPS-02:PCO6:ENABLE",0)			#Deactivate kphi position compare
	beamline.setValue("Top","-MO-XPS-02:PCO3:ENABLE",0)
	beamline.setValue("Top","-MO-XPS-02:PCO5:ENABLE",0)
	
