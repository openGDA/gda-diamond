#localStation.py
#For beamline specific initialisation code.

print "===================================================================";
print "Performing Beanline I06-shared initialisation code (localStation.py).";
print

import sys;

from gda.configuration.properties import LocalProperties

# Get the locatation of the GDA beamline script directory
gdaScriptDir = LocalProperties.get("gda.jython.gdaScriptDir") + "/";

# Get the location of the USERS script directory
userScriptDir = LocalProperties.get("gda.jython.userScriptDir") + "/";

gdaDevScriptDir = LocalProperties.get("gda.jython.gdaDevScriptDir") + "/";

from i06shared.commands.dirFileCommands import pwd, lwf,nwf,nfn,setSubdirectory,getSubdirectory  # @UnusedImport
from i06shared.functions.aliasFunctions import setAlias, setGdaAlias  # @UnusedImport
from i06shared.constant import *  # @UnusedWildImport
from Diamond.Utility.Functions import logger, getScanNumber,incScanNumber,interruptable,removeDevices,getDevice,isDefaultDevice,removeDefaults,backupDefaults,restoreDefaults  # @UnusedImport
from Diamond.Utility.setTimers import stopwatch,timekeeper,clock,lineTime,pointTime,waitTimer,timer,scanTimer,Timers,Dummies,dummyCounter  # @UnusedImport
from Diamond.PseudoDevices.CorrespondentDevice import CorrespondentDeviceClass;  # @UnusedImport
from Diamond.PseudoDevices.DeviceFunction import DeviceFunctionClass;  # @UnusedImport

try:
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
	import scisoftpy as dnp;  # @UnusedImport
except:
	exceptionType, exception, traceback1=sys.exc_info();
	print "Error:  import scisoftpy raise exceptions"
	logger.dump("---> ", exceptionType, exception, traceback1)

from i06shared.setCASum import ca11sum,ca12sum,ca13sum,ca14sum,ca21sum,ca22sum,ca23sum,ca24sum,ca31sum,ca32sum,ca33sum,ca34sum,ca41sum,ca42sum,ca43sum,ca44sum  # @UnusedImport

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
#import scannables.detector.andormcd
#i06ccd2 = scannables.detector.andormcd.AndorMCD('i06ccd2')


