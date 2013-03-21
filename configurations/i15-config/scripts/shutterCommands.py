import sys
from time import sleep
from gdascripts.messages import handle_messages
from gdascripts.messages.handle_messages import simpleLog

global configured, isccd, beamline
configured = False

def configure(jythonNameMap, beamlineParameters):
	global configured, isccd, beamline
	"""
	sets module variables from jython namespace, finder and beamline parameters
	"""
	isccd = jythonNameMap.atlas
	beamline = jythonNameMap.beamline
	configured = True

def checkConfigured():
	if not configured:
		raise "shutterCommands not configured"
	
def sh(cmd):
	"""
	sh('o')  - Reset and Open EH & Atlas shutter.
	sh('oa') - Reset and Open FE, OH, EH & Atlas Shutters
	sh('c')  - Close EH & Atlas Shutter
	sh('ca') - Close FE, OH, EH & Atlas Shutters"
	sh('status') - get Status

	Note: If the Atlas is switched to Ext. trigger rather than Atlas, then
		the Atlas shutter will follow the Epics synoptic FS control and
		Newport XPS position compare.
	
	See: http://wiki.diamond.ac.uk/Wiki/Wiki.jsp?page=Atlas%20detector%20does%20not%20acquire%20images
	"""
	checkConfigured()
	try:
		if (cmd=="o"):
			#Reset and Open EH & Atlas shutter (Open takes 4-5 seconds).
			openEHShutter()
			isccd.openS()
			return
		elif (cmd=="c"):
			#Close EH & Atlas Shutter
			closeEHShutter()
			isccd.closeS()
			return
		elif (cmd=="oa"):
			#Reset and Open OH2 and EH shutter (Open takes 4-5 seconds).
			openOH2Shutter()
			openEHShutter()
			isccd.openS()
			return
		elif (cmd=="ca"):
			#Close EH & Atlas Shutter
			closeOH2Shutter()
			closeEHShutter()
			isccd.closeS()
			return
		elif (cmd=="status"):
			#Get status
			return isccd.getS()
		else:
			simpleLog( 'No habla ingles? Use "o", "c", "oa", or "oc". Versuchen noch einmal!')
		
		getShutterStatus()
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None, "sh command error", type, exception, traceback, False)
	return

#===========================================================================================
def openEHShutter():
	"""
	openEHShutter does:
		1. Opens the experimental hutch shutter.
		2. Waits for it to open.
		3. Checks the shutter status.
	syntax: openEHShutter()
	"""
	checkConfigured()
	beamline.setValue("Top","-PS-SHTR-02:CON",2)		#RESET
	beamline.setValue("Top","-PS-SHTR-02:CON",0)		#OPEN
	simpleLog( "Opening the EH shutter...")
	status = beamline.getValue(None,"Top","-PS-SHTR-02:STA")
	count = 0
	while (status != 1):
		sleep(1)  # Pause for 1 second.
		count = count +1
		if count ==6:
			simpleLog( " -> Time out: Could not Open EH shutter")
			return
		status = beamline.getValue(None,"Top","-PS-SHTR-02:STA")
	getShutterStatus(`status`)
	return

#===========================================================================================
def closeEHShutter():
	"""
	closeExperimentalHutchShutter
		1. Closes the experimental hutch shutter.
		2. Waits for it to close.
		3. Checks the shutter status.
	syntax: closeExperimentalHutchShutter()
	"""
	checkConfigured()
	beamline.setValue("Top","-PS-SHTR-02:CON",2)		#RESET
	beamline.setValue("Top","-PS-SHTR-02:CON",1)		#CLOSE
	simpleLog( "Closing the EH shutter...")
	status = beamline.getValue(None,"Top","-PS-SHTR-02:STA")
	count = 0
	while (status != 3):
		sleep(1)  # Pause for 1 second.
		count = count +1
		if count ==4:
			simpleLog( " -> Time out: Could not Close EH shutter")
			return
		status = beamline.getValue(None,"Top","-PS-SHTR-02:STA")
	getShutterStatus(`status`)
	return

#===========================================================================================
def openOH2Shutter():
	"""
	openOH2Shutter
		1. Opens the OH2 (Optics hutch 2) shutter.
		2. Waits for it to open.
		3. Checks the shutter status.
	syntax: openExperimentalHutchShutter()
	"""
	checkConfigured()
	beamline.setValue("Top","-PS-SHTR-01:CON",2)		#RESET
	beamline.setValue("Top","-PS-SHTR-01:CON",0)		#OPEN
	simpleLog( "Opening the OH2 shutter...")
	status = beamline.getValue(None,"Top","-PS-SHTR-01:STA")
	count = 0
	while (status != 1):
		sleep(1)  # Pause for 1 second.
		count = count +1
#		print count
		if count ==6:
			simpleLog( " -> Time out: Could not Open OH2 shutter")
			return
		status = beamline.getValue(None,"Top","-PS-SHTR-01:STA")
	getShutterStatus(`status`)
	return

#===========================================================================================
def closeOH2Shutter():
	"""
	closeOH2Shutter
		1. Closes the OH2 (Optics hutch 2) shutter.
		2. Waits for it to close.
		3. Checks the shutter status.
	syntax: closeOH2Shutter()
	"""
	checkConfigured()
	beamline.setValue("Top","-PS-SHTR-01:CON",2)		#RESET
	beamline.setValue("Top","-PS-SHTR-01:CON",1)		#CLOSE
	simpleLog( "Closing the OH2 shutter...")
	status = beamline.getValue(None,"Top","-PS-SHTR-01:STA")
	count = 0
	while (status != 3):
		sleep(1)  # Pause for 1 second.
		count = count +1
#		print count
		if count ==5:
			simpleLog( " -> Time out: Could not Close OH2 shutter")
			return
		status = beamline.getValue(None,"Top","-PS-SHTR-01:STA")
	getShutterStatus(`status`)
	return

#===========================================================================================

def getShutterStatus(status):
	"""
	getShutterStatus formats the shutter status in human readable and prints its status to command line.
	syntax: getShutterStatus()
	"""
	checkConfigured()
	if (status=="3"):
		simpleLog( " -> Shutter Closed")
	elif (status=="1"): 
		simpleLog( " -> Shutter Open")
	return
