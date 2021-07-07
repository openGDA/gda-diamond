##
## Functions required for scanning with ccd using XPS Position Compare
##
from gdascripts.messages.handle_messages import simpleLog

global configured, beamline
configured = False
def configure(jythonNameMap, beamlineParameters):
	global configured, beamline
	"""
	sets module variables from jython namespace, finder and beamline parameters
	"""
	beamline = jythonNameMap.beamline
	configured = True
	
def checkConfigured():
	if not configured:
		raise Exception, "ccdMechanics not configured"
		
######################################################################################
def scanGeometryCheck(axis, velocity, A, B):
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
			raise Exception, "Error: Move is either too short or too slow, so the " + \
				"start position (%f) is after the end position (%f)" % (
				correctedA, correctedB) + "with de-bounce correction! " + \
				"Moves must take more than %f ms with velocities below %f." % (
				stretchedPulseLengthMs, velocityMinimumWithoutDebounce_DegPerSec)
	
	else:
		raise Exception, "Error: velocity (%f) is below minimum supported velocity (%f)" \
			% (velocity, velocityMinimumWithDebounce_DegPerSec)
	
	return debounce, correctedA, correctedB, suffix

def scanGeometryApply(axis, geometry, debounce, correctedA, correctedB, suffix):
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
		raise Exception, "Error: axis (%s) is not supported by position compare" % axis.name

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
	elif (axis.name == 'cryorot'):
		return "-MO-VCOLD-01:THETA"
	elif (axis.name == 'syaw'):
		simpleLog("WARNING: the syaw motor ignores the velocity setting and always moves at full speed!")
		return "-MO-SFAB-01:YAW"
	
	raise Exception, "Error: axis (%s) is not supported by velocity change script" % axis.name
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
	
