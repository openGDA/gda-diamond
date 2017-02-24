import sys
from Diamond.Utility.BeamlineFunctions import logger

print "-"*100
print "Waveplate 3 (EC2) motor: wp32"

try:
    from Diamond.PseudoDevices.EpicsMotors import EpicsCallbackMotorClass
    wp32 = EpicsCallbackMotorClass('wp32', "BL06I-OP-WAVE-32:MTR", '%.4f');
except:
    exceptionType, exception, traceback=sys.exc_info();
    print "XXXXXXXXXX:  wp32 Error "
    logger.dump("---> ", exceptionType, exception, traceback)

