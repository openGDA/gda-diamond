#localStation.py
#For beamline specific initialisation code.
print "===================================================================";
print "Performing Beanline I06 specific initialisation code (localStation.py).";
print

import sys;
from os import system;

from gda.configuration.properties import LocalProperties
import scisoftpy as dnp;

# BLVI-110 GDA-5921: Work around ScanBase generating erroneous exceptions after default was changed from False to True:
LocalProperties.set('gda.scan.clearInterruptAtScanEnd', "False")

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
	raise "Basic beamline script error";


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
	#Set up the 8512 scaler card
	print "-------------------------------------------------------------------"
	print "Set up the 8512 scaler card"
	execfile(gdaScriptDir + "BeamlineI06/Scaler8512.py");
	
	#Set up the Patch Panel scaler card
	print "-------------------------------------------------------------------"
	print "Set up the Patch Panel scaler card"
	execfile(gdaScriptDir + "BeamlineI06/PatchPanelScaler8512.py");

	#Set up the Mobilerack scaler card
	print "-------------------------------------------------------------------"
	print "Set up the Patch Panel scaler card"
	execfile(gdaScriptDir + "BeamlineI06/MobilerackScaler8512.py");
	
	#Set the caxxsum for average current amplifier reading 
	execfile(gdaScriptDir + "BeamlineI06/setCASum.py");
except:
	exceptionType, exception, traceback=sys.exc_info();
	print "XXXXXXXXXX:  Patch Panel Scaler Error "
	logger.dump("---> ", exceptionType, exception, traceback)
	

try:
	print "-------------------------------------------------------------------"
	print "Enable the multiple region scan";
	execfile(gdaScriptDir + "BeamlineI06/setSpecialScans.py");
except:
	exceptionType, exception, traceback=sys.exc_info();
	print "XXXXXXXXXX:  rscan Error "
	logger.dump("---> ", exceptionType, exception, traceback)

try:
	print "-------------------------------------------------------------------"
	print "Enable the Constant velocity scan on energy";
	execfile(gdaScriptDir + "BeamlineI06/fastEnergyScan.py");
	
	print "-------------------------------------------------------------------"
	print "Setup the PGM controls";
	execfile(gdaScriptDir + "BeamlineI06/usePGM.py");
except:
	exceptionType, exception, traceback=sys.exc_info();
	print "XXXXXXXXXX:  Energy Device Error "
	logger.dump("---> ", exceptionType, exception, traceback)

try:
	
	print "-------------------------------------------------------------------"
	print "Setup the Insertion Device controls";
	execfile(gdaScriptDir + "BeamlineI06/useID.py");
except:
	exceptionType, exception, traceback=sys.exc_info();
	print "XXXXXXXXXX:  Insertion Device Error "
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
	print "-------------------------------------------------------------------"
	print "Change the default output format to meet the beamline requirements"
	execfile(gdaScriptDir + "BeamlineI06/setOutputFormat.py");
	
	print
	print "===================================================================";
	print "SRS scan data file header setup"
	execfile(gdaScriptDir + "BeamlineI06/setSrsDataFileHeader.py");
except:
	exceptionType, exception, traceback=sys.exc_info();
	print "XXXXXXXXXX:  Errors when running the localstation.py"
	logger.dump("---> ", exceptionType, exception, traceback)


try:
	print "-------------------------------------------------------------------"
	print "Enable the cameras";
#	execfile(gdaScriptDir + "BeamlineI06/useCameras.py");
except:
	exceptionType, exception, traceback=sys.exc_info();
	print "XXXXXXXXXX:  Flea Error "
	logger.dump("---> ", exceptionType, exception, traceback)

	
# Get the beamline branche name from the Object Factory Name property
gdaObjectFactoryName = LocalProperties.get("gda.factory.factoryName")

if gdaObjectFactoryName == 'I06':
	print
	print "===================================================================";
	print "This is DLS Beamline I06 PEEM Line"
	execfile(gdaScriptDir + "localStation_i06.py");
	#Performing user specific initialisation code"
	print
	print "-------------------------------------------------------------------"
	print "Performing user specific initialisation code for PEEM Line (MainLineUser.py)"
	try:
		execfile(userScriptDir + "MainLineUser.py");
	except:
		exceptionType, exception, traceback=sys.exc_info();
		print "XXXXXXXXXX:  MainLineUser.py Error"
		logger.dump("---> ", exceptionType, exception, traceback)

elif gdaObjectFactoryName == 'I06-1':
	print
	print "===================================================================";
	print "This is DLS Beamline I06 Branch Line"
	execfile(gdaScriptDir + "localStation_i06-1.py");
	print
	print "-------------------------------------------------------------------"
	print "Performing user specific initialisation code for Branch Line (BranchLineUser.py)"
	try:
		execfile(userScriptDir + "BranchLineUser.py");
	except:
		exceptionType, exception, traceback=sys.exc_info();
		print "XXXXXXXXXX:  BranchLineUser.py Error"
		logger.dump("---> ", exceptionType, exception, traceback)
else:
	print "Wrong Beamline Name"

print "==================================================================="; print; print;

print "Creating i06ccd2 detector (from end of localStation.py)"
import scannables.detector.andormcd
i06ccd2 = scannables.detector.andormcd.AndorMCD('i06ccd2')


