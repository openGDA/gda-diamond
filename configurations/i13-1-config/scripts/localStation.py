import sys	
from gdascripts.messages import handle_messages
from gda.configuration.properties import LocalProperties

try:
	from gda.factory import Finder

	
	finder = Finder.getInstance() 
	beamline = finder.find("Beamline")
	ring= finder.find("Ring")
	
	import tests.testRunner
	tests.testRunner.run_tests()
	
	from gda.scan.RepeatScan import create_repscan, repscan
	vararg_alias repscan
	
	from gdascripts.pd.time_pds import waittimeClass2
	waittime=waittimeClass2('waittime')

except :
	exceptionType, exception, traceback = sys.exc_info()
	handle_messages.log(None, "Error in localStation", exceptionType, exception, traceback, False)
