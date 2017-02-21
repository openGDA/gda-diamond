#localStation.py
#For beamline specific initialisation code.
from Diamond.Utility.BeamlineFunctions import logger
print "===================================================================";
print "Performing I06 PEEM line specific initialisation code (localStation_i06.py).";
print
import sys

#Setup the diagnostic cameras
try:
    print "-------------------------------------------------------------------"
    print "Set up the diagnostic cameras"
    execfile(gdaScriptDir + "BeamlineI06/useCameras.py");
except:
    exceptionType, exception, traceback=sys.exc_info();
    logger.dump("---> ", exceptionType, exception, traceback)


try:
    print "Enable the XEnergy"
    execfile(gdaScriptDir + "BeamlineI06/Users/XEnergy/xenergy.py");
except:
    exceptionType, exception, traceback=sys.exc_info();
    print "XXXXXXXXXX:  Errors when running the BeamlineI06/XEnergy/xenergy.py from localstation_i06.py"
    logger.dump("---> ", exceptionType, exception, traceback)

try:
    print "Enabling the Laser..."
    execfile(gdaScriptDir + "BeamlineI06/useSlap.py");
except:
    exceptionType, exception, traceback=sys.exc_info();
    print "XXXXXXXXXX:  Errors when running the BeamlineI06/useSlap.py from localstation_i06.py"
    logger.dump("---> ", exceptionType, exception, traceback)
