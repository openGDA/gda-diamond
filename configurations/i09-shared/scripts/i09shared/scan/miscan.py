'''
'miscan' - a scan that collects multiple images at each scan data point. It extends the standard 'scan' syntax and
configure the detector number of images to be collected before scan starts.

It records both 'miscan' command as well as the actual standard 'scan' command in the data file.
This command only works with detector which is configured to collect images in Multiple mode.

Created on 31 Jan 2017

@author: fy65
'''
import time
from gda.device.detector import NXDetector
from types import TupleType
from gda.device.scannable import DummyScannable
from gda.jython.commands.ScannableCommands import scan
from i09shared.utils.check_scan_arguments import parse_tuple_arguments, parse_other_arguments, save_detector_settings_before_scan, parse_detector_arguments, restore_detector_setting_after_scan

print("-"*100)
print("Creating 'miscan' - multiple images per scan data point")
print("    Syntax: miscan (scannable1, scannable2) ([1,2], [3,4],[5,6]) mpx 10 0.1")
print("")

PRINTTIME = False
dummyScannable = DummyScannable("dummyScannable")

PRINTTIME = False
zeroScannable = DummyScannable("zeroScannable")

def miscan(*args):
	'''
	a more generalised scan that extends standard GDA scan syntax to support
	1. scannable tuple (e.g. (s1,s2,...) argument) as scannable group,
	2. its corresponding path tuple (e.g. list of position tuples), if exist, and
	3. area detector that takes 2 input numbers - 1st input is the number of images to be collected at each point,
		if omitted it default to 1, and 2nd input is detector exposure time which must be provided,
	4. syntax 'miscan mpx 10 0.1 ...' is supported for collecting 10 images at a single point.

	It parses input parameters described above before delegating to the standard GDA scan to do the actual data collection.
	Thus it can be used anywhere the standard GDA 'scan' is used.
	'''
	command = "miscan "  # rebuild the input command as String so it can be recored into data file

	starttime = time.ctime()
	start = time.time()
	if PRINTTIME: print("=== Scan started: " + starttime)
	newargs = []
	i = 0;
	CACHE_PARAMETER_TOBE_CHANGED = False
	while i < len(args):
		arg = args[i]
		if i == 0 and isinstance(arg, NXDetector):
			newargs.append(dummyScannable)
			newargs.append(0)
			newargs.append(0)
			newargs.append(1)
			newargs.append(arg)
			command += str(arg.getName()) + " "
		elif type(arg) == TupleType:
			command, newargs = parse_tuple_arguments(command, newargs, arg)
		else:
			newargs.append(arg)
			command = parse_other_arguments(command, arg)
			i = i + 1

		from org.opengda.detector.electronanalyser.nxdetector import EW4000
		if isinstance(arg, NXDetector) and not isinstance(arg, EW4000):
			adbase, image_mode, num_images = save_detector_settings_before_scan(arg)
			if all((adbase, image_mode, num_images)):
				CACHE_PARAMETER_TOBE_CHANGED = True
				command, newargs = parse_detector_arguments(command, newargs, args, i, arg)
				i = i + 1

	# meta.addScalar("user_input", "command", command)
	try:
		scan([e for e in newargs])
	finally:
		if CACHE_PARAMETER_TOBE_CHANGED:
			restore_detector_setting_after_scan(adbase, image_mode, num_images)
		# meta.rm("user_input", "command")

	if PRINTTIME: print("=== Scan ended: " + time.ctime() + ". Elapsed time: %.0f seconds" % (time.time() - start))

from gda.jython.commands.GeneralCommands import alias
alias("miscan")
