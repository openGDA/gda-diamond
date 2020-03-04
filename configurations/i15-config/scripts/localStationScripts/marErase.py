from gda.factory import Finder
from gda.jython.commands.GeneralCommands import pause
from gdascripts.messages.handle_messages import simpleLog
from gdascripts.utils import caput
from localStationScripts.shutterCommands import closeEHShutter
import time

def marErase(N=1):
	"""
	marErase(N)
	erases image plate N times.
	"""
	checkMarIsReady()

	marEraseTimeout = 250

	#Make sure EH shutter is closed.
	closeEHShutter()
	for i in range(0,N,1):
		simpleLog("==============")

		simpleLog("Wait for mar to be ready before starting erase...")
		timeTaken = waitForMarStatus(marEraseTimeout, 0)
		if (timeTaken == -1):
			simpleLog("Timed out waiting for mar to be ready, so erase not performed")
			return

		# Send erase command and Wait for mar to start erasing
		simpleLog( "Mar ready, so start erasing " + str(i+1) + " of " + str(N) )
		#Finder.getInstance().find('mar').erase()
		caput("BL15I-EA-MAR-01:CAM:Erase","1")
		timeTaken = waitForMarStatus(marEraseTimeout, 1)
		if (timeTaken == -1):
			simpleLog("Timed out waiting for mar to start, so erase not performed")
		else:
			# Scan erasing and wait for mar to be ready
			timeTaken = waitForMarStatus(marEraseTimeout, 0)
			if (timeTaken == -1):
				simpleLog("Timed out waiting for mar to stop erasing")
			else:
				simpleLog("Erased in time %.2f" % timeTaken + "s")

	simpleLog("Erasures complete")

def waitForMarStatus(timeout, status):
	"""
	waitForMarStatus(timeout, status) waiting for mar status
	returns time taken or -1 if timed out
	"""
	mar = Finder.getInstance().find('mar')

	t0 = time.clock()
	t1 = t0
	while ( (t1 - t0) < timeout ): 
		if (mar.getStatus() == status):
			#simpleLog("Mar status of " + str(status) + " reached in time %.2f" % (t1 - t0) + "s")
			return (t1 - t0)
		t1 = time.clock()
		time.sleep(1)
		pause()                     # ensures script can be stopped promptly

	simpleLog("Timed out waiting for mar status of " + str(status) + " (waited " + str(timeout) + "s)")
	return -1

def checkMarIsReady():
	"""
	If mar not ready, then display message and abort
	"""
	status = Finder.getInstance().find('mar').getStatus()
	if (status != 0):
		raise "Mar is not ready. Please wait or restart the mar. Value = " +`status`
