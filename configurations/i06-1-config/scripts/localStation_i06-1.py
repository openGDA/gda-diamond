
#localStation.py
#For beamline specific initialisation code.
print "===================================================================";
print "Performing Beamline I06 branch line specific initialisation code (localStation_i06-1.py).";
print

#Setup the environment variables
import java
import sys
from gda.configuration.properties import LocalProperties

localStationErrorCount=0

print "-------------------------------------------------------------------"
print "Waveplate 3 (EC2) motor: wp32"

try:
    from Diamond.PseudoDevices.EpicsMotors import EpicsCallbackMotorClass
    wp32 = EpicsCallbackMotorClass('wp32', "BL06I-OP-WAVE-32:MTR", '%.4f');
except:
    exceptionType, exception, traceback=sys.exc_info();
    print "XXXXXXXXXX:  wp32 Error "
    logger.dump("---> ", exceptionType, exception, traceback)
    localStationErrorCount+=1


print "-------------------------------------------------------------------"
print "==================================================================="
print "Total number of localStation errors was", localStationErrorCount
print "==================================================================="