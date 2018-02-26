#localStation.py
#For beamline specific initialisation code.
print "===================================================================";
print " Performing Beanline I07 specific initialisation code (localStationSimple.py).";
print

#Setup the environment variables
import sys;
from os import system;
from time import sleep;

from gda.configuration.properties import LocalProperties;

import scisoftpy as dnp;

from gdascripts.utils import *;
	
# Get the locatation of the GDA beamline script directory
gdaScriptDir = LocalProperties.get("gda.config") + "/scripts/";

# Get the location of the USERS script directory
userScriptDir = "/dls_sw/" + LocalProperties.get("gda.beamline.name") + "/scripts/";
	


try:
	execfile(gdaScriptDir + "BeamlineI07/beamline.py");
except:
	exceptionType, exception, traceback=sys.exc_info();
	print "XXXXXXXXXX:  Logger Error"
	raise "Logger error";


try:
	#Performing the utility functions"
	print "-------------------------------------------------------------------"
	print "Setup the utility functions"
	execfile(gdaScriptDir + "BeamlineI07/setTimers.py");
	
except:
	exceptionType, exception, traceback=sys.exc_info();
	print "XXXXXXXXXX:  Serious errors when running the setTimers.py"
	logger.dump("---> ", exceptionType, exception, traceback)

#Pilatus Support
print
print "===================================================================";
#print "Pilatus Support"
#try:
#	execfile(gdaScriptDir + "BeamlineI07/useEpicsPilatus100K.py");
#except:
#	exceptionType, exception, traceback=sys.exc_info();
#	print "XXXXXXXXXX:  Pilatus Detector Error"
#	logger.dump("---> ", exceptionType, exception, traceback)


#try:
	#Setup the Flea Camera support in GDA
	#execfile(gdaScriptDir + "BeamlineI07/cameras.py");
#except:
#	exceptionType, exception, traceback=sys.exc_info();
#	logger.fullLog(None, "Flea Camera Error", exceptionType, exception, traceback, True);
	
try:
	#Dummy Camera Setup
	print
	print "===================================================================";
	execfile(gdaScriptDir + "BeamlineI07/useDummyCam.py");
except:
	exceptionType, exception, traceback=sys.exc_info();
	print "XXXXXXXXXX:  Dummy Camera Error"
	logger.dump("---> ", exceptionType, exception, traceback)


try:
	print "-------------------------------------------------------------------"
	print "Enable the multiple region scan";
	execfile(gdaScriptDir + "BeamlineI07/setSpecialScans.py");
except:
	exceptionType, exception, traceback=sys.exc_info();
	print "XXXXXXXXXX:  rscan Error "
	logger.dump("---> ", exceptionType, exception, traceback)

	
try:	
	#Constants used on this beamline
	execfile(gdaScriptDir + "BeamlineI07/createAlias.py");
except:
	exceptionType, exception, traceback=sys.exc_info();
	print "XXXXXXXXXX:  Errors when creating alias commands"
	logger.dump("---> ", exceptionType, exception, traceback)


##to setup the scan processing wrappers
#from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
#scan_processor.rootNamespaceDict=globals()
#import gdascripts.utils #@UnusedImport
#gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals() 


print "==================================================================="; print; print;
