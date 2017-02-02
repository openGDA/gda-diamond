#localStation.py
#For beamline specific initialisation code.
print "===================================================================";
print "Performing Beamline I06 specific initialisation code (localStation.py).";
print

print "-"*100
print "Set scan returns to the start positions on completion"
print "   To set scan returns to its start positions on completion please do:"
print "      >>>scansReturnToOriginalPositions=1"
scansReturnToOriginalPositions=0;
print

from i06shared.localStation import *

from BeamlineI06.beamline import getTitle,gettitle,getvisit,getVisit,lastscan,setDir,setdir,setTitle,settitle,setVisit,setvisit  # @UnusedImport
from BeamlineI06.createAlias import closebeam, openbeam  # @UnusedImport
from BeamlineI06.Scaler8512 import ca11s,ca12s,ca13s,ca14s,ca21s,ca22s,ca23s,ca24s,ca31s,ca32s,ca33s,ca34s,ca41s,ca42s,ca43s,ca44s,ca11sr,ca12sr,ca13sr,ca14sr,ca21sr,ca22sr,ca23sr,ca24sr,ca31sr,ca32sr,ca33sr,ca34sr,ca41sr,ca42sr,ca43sr,ca44sr,scalar1raw,scaler1  # @UnusedImport
from BeamlineI06.U1Scaler8513 import ca51sr,ca52sr,ca53sr,ca54sr,scalar3  # @UnusedImport

try:

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


