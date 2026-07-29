from gda.jython.commands.ScannableCommands import createConcurrentScan
from gdascripts import installation
import time

kenergy_tolerance = 0.002
sleep_time=0.05

def fastscan(*args):
	''' A wrapper scan that extends standard GDA scan syntax.
	This scan works only if there is kenergy or Kenergy scannable which are children of SingleEpicsPositionerClass in a scan command.
	It will first make a blocking move kenergy(Kenergy) scannable to a start value and then run the main scan.
	Waiting is NOT based on scannable.isBusy() method but on comparing readback to demand.

	'''
	final_scan = createConcurrentScan([e for e in args])
	scannable_names = [sc.getName() for sc in final_scan.getScannables()]

	if (("kenergy" not in scannable_names) and ("Kenergy" not in scannable_names)):
		print("kenergy or Kenergy scannables were not found in fastscan command - aborting scan")
		print("fastscan can only work if kenergy or Kenergy scannables are used in fastscan command!")
		return

	for sc in final_scan.getAllScanObjects():
		sc_name = sc.getScannable().getName()
		if (sc_name=="Kenergy" or sc_name=="kenergy"):
			sc_pos = sc.getStart()
			print("Moving %s scannable to a start position %f", sc_name, sc_pos)
			sc.getScannable().asynchronousMoveTo(sc_pos)
			if installation.isLive():
				while (abs(float(sc.getScannable().readCli.caget())-sc_pos)>sc.getScannable().target_tolerance):
					time.sleep(sleep_time)
			else:
				while (abs(sc.getScannable().getPosition()-sc_pos)>kenergy_tolerance):
					time.sleep(sleep_time)
	try:
		final_scan.runScan()
	except:
		print("Error running fastscan")


