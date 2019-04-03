#localStation.py
#For beamline specific initialisation code.
print "===================================================================";
print "Performing Beanline I06 specific initialisation code (localStation.py).";
print

import sys;
from os import system;

from gda.configuration.properties import LocalProperties
import scisoftpy as dnp;

# Get the locatation of the GDA beamline script directory
gdaScriptDir = LocalProperties.get("gda.jython.gdaScriptDir") + "/";

# Get the location of the USERS script directory
userScriptDir = LocalProperties.get("gda.jython.userScriptDir") + "/";

gdaDevScriptDir = LocalProperties.get("gda.jython.gdaDevScriptDir") + "/";

try:
	execfile(gdaScriptDir + "BeamlineI06/beamline.py");
except:
	exceptionType, exception, traceback=sys.exc_info();
	print "XXXXXXXXXX:  beamline.py script error"
	raise RuntimeError("Basic beamline script error");


try:
	#Setup the environment variables
	from Diamond.Utility.Functions import *;
	execfile(gdaScriptDir + "BeamlineI06/createAlias.py");
	
	#Performing the utility functions"
	print "-------------------------------------------------------------------"
	print "Setup the utility functions"
	execfile(gdaScriptDir + "BeamlineI06/setTimers.py");
	
	print "-------------------------------------------------------------------"
	print "Enable the CorrespondentDevice";
	from Diamond.PseudoDevices.CorrespondentDevice import CorrespondentDeviceClass;
	print "-------------------------------------------------------------------"
	print "Enable DeviceFunction";
	from Diamond.PseudoDevices.DeviceFunction import DeviceFunctionClass;
	
	#Set up the Diamond NumPy
	print "-------------------------------------------------------------------"
	print "Note: Use dnp (Diamond NumPy) from scisoftpy for data handling and plotting in GDA"
	print "Note: Use help dnp for all commands"
	print "Note: Use help <component> for help on all components ..." 
	print "      (dnp.core, dnp.io, dnp.maths, dnp.plot, dnp.image)"
	print "For example: "
	print "		 To load data:  data=dnp.io.load(/full/path/to/data/file, formats=['srs'], asdict=True)"
	print "		 To plot data:  dnp.plot.line(x, y)"
	print "		 To plot image: dnp.plot.image(data)"
	
except:
	exceptionType, exception, traceback=sys.exc_info();
	print "XXXXXXXXXX:  Serious errors when running the localstation.py"
	logger.dump("---> ", exceptionType, exception, traceback)
	

try:
	print "-------------------------------------------------------------------"
	print "Enable the multiple region scan";
	execfile(gdaScriptDir + "BeamlineI06/setSpecialScans.py");
except:
	exceptionType, exception, traceback=sys.exc_info();
	print "XXXXXXXXXX:  mrscan Error "
	logger.dump("---> ", exceptionType, exception, traceback)

try:	
	print "-------------------------------------------------------------------"
	print "Enable the Peak finding pseudo device pfif";
	execfile(gdaScriptDir + "BeamlineI06/findingKeyPoints.py");
	
	print "-------------------------------------------------------------------"
	print "Enable the FixThings function";
	execfile(gdaScriptDir + "BeamlineI06/fixThings.py");
	
	
	#Enable the laser delay stage functions"
	#print "-------------------------------------------------------------------"
	#print "Enable the laser delay stage functions"
	#execfile(gdaScriptDir + "laserDelayStage.py");
except:
	exceptionType, exception, traceback=sys.exc_info();
	print "XXXXXXXXXX:  Errors when running the localstation.py"
	logger.dump("---> ", exceptionType, exception, traceback)


try:
	#Dummy Camera Setup
	print
	print "===================================================================";
#	execfile(gdaScriptDir + "BeamlineI06/useDummyCam.py");
except:
	exceptionType, exception, traceback=sys.exc_info();
	print "XXXXXXXXXX:  Dummy Camera Error"
	logger.dump("---> ", exceptionType, exception, traceback)



try:
	print
	print "===================================================================";
	print "SRS scan data file header setup"
	execfile(gdaScriptDir + "BeamlineI06/setDummyDataFileHeader.py");
except:
	exceptionType, exception, traceback=sys.exc_info();
	print "XXXXXXXXXX:  Errors when running the localstation.py"
	logger.dump("---> ", exceptionType, exception, traceback)

	


print "==================================================================="; print; print;
