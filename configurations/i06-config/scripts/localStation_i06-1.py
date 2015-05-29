
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

from scannables import Keithley2612, Keith2612CurrentMeter, Keith2612VoltSource
Keithley=Keithley2612.Keithley2612(channel=0, function=1, pvBase='BL06J-EA-USER-01:ASYN6.')
volt=Keith2612VoltSource.Keith2612VoltSource('volt', Keithley, 1)
curr=Keith2612CurrentMeter.Keith2612CurrentMeter('curr', Keithley, 1)
kon=Keithley.turnOn
koff=Keithley.turnOff
alias('kon')
alias('koff')

from scannables import KepkoCurrent, KepkoMagnet
print"-> connect the Kepko to Analogue output 2 in patch panel U2 (branchline)"
magnet = KepkoMagnet.KepkoMagnet("magnet", "BL06J-EA-USER-01:AO2")
print"-> magnet calibration for pole gap = 35.4 mm and bobbin turns = 784" 
magnet.setConvCoeff([0, 253.16, 7.22765, 9.37523, -1.81716, -3.49587, 0.155178, 0.267718, -0.00433883, -0.00662351])
magnet.setInvConvCoeff([0, 0.00369277, -7.65554e-07, 6.49905e-09,5.76312e-12, -6.23302e-14, -1.77119e-17, 2.0429e-19,1.8207e-23, -1.70236e-25])

# Since the BeamlineFunctionClass is common between Main and Branch line, if
# we want i06-1 elog messages to be written to the i06-1 eLog, we have to
# override elogID here:
i06.elogID="BLI06-1"

# Get the locatation of the GDA beamline script directory
gdaScriptDir = LocalProperties.get("gda.jython.gdaScriptDir") + "/";

# Get the location of the USERS script directory
userScriptDir = LocalProperties.get("gda.jython.userScriptDir") + "/";

#Enable the laser delay stage functions"
#print "-------------------------------------------------------------------"
#print "Enable the laser delay stage functions"
#execfile(gdaScriptDir + "laserDelayStage.py");

print "-------------------------------------------------------------------"
enableSuperconductingMagnetControl=True
if enableSuperconductingMagnetControl:
    print "Enable the Superconducting Magnet Control."
    try:
        execfile(gdaScriptDir + "BeamlineI06/useMagnet.py")
    except:
        exceptionType, exception, traceback=sys.exc_info()
        print "XXXXXXXXXX:  Magnet Setting Up Error "
        logger.dump("---> ", exceptionType, exception, traceback)
        localStationErrorCount+=1
else:
    print "Not enabled: Superconducting Magnet Control."

#Setup the PIXIS Camera
print "-------------------------------------------------------------------"
enablePixisDetector=False
# See also the server_pixis import in server_i06-1.xml
if enablePixisDetector:
    print "Set up the PIXIS"
    try:
        execfile(gdaScriptDir + "BeamlineI06/usePixis.py");
    except:
        exceptionType, exception, traceback=sys.exc_info();
        print "XXXXXXXXXX:  Pixis Error "
        logger.dump("---> ", exceptionType, exception, traceback)
        localStationErrorCount+=1
else:
    print "Not enabled: PIXIS Detector."

try:
    #Enable Exit Slits S6 Gap Control s6ygap";
    #print "-------------------------------------------------------------------"
    print "Enable Slits S6 Gap Control s6ygap"
    execfile(gdaScriptDir + "BeamlineI06/useS6.py");
except:
    exceptionType, exception, traceback=sys.exc_info();
    print "XXXXXXXXXX:  Errors when running the s6ygap.py"
    logger.dump("---> ", exceptionType, exception, traceback)
    localStationErrorCount+=1

try:
    print "-------------------------------------------------------------------"
    print "Set up the m6qgmax routing"

    execfile(gdaScriptDir + "BeamlineI06/m6qgmax.py");
except:
    exceptionType, exception, traceback=sys.exc_info();
    print "XXXXXXXXXX:  m6qgmax Error "
    logger.dump("---> ", exceptionType, exception, traceback)
    localStationErrorCount+=1

try:
    print "-------------------------------------------------------------------"
    #print "Change the default output format to meet the branch line requirements"
    execfile(gdaScriptDir + "BeamlineI06/setOutputFormat_i06-1.py");
    
    #Group the hexapod legs into list
    m1legs = [m1leg1, m1leg2, m1leg3, m1leg4, m1leg5, m1leg6];
    m6legs = [m6leg1, m6leg2, m6leg3, m6leg4, m6leg5, m6leg6];
    m7legs = [m7leg1, m7leg2, m7leg3, m7leg4, m7leg5, m7leg6];
except:
    exceptionType, exception, traceback=sys.exc_info();
    print "XXXXXXXXXX:  Errors when running the localstation_i06.py"
    logger.dump("---> ", exceptionType, exception, traceback)
    localStationErrorCount+=1

print "-------------------------------------------------------------------"
print "Set up idio and ifio"

try:
    execfile(gdaScriptDir + "BeamlineI06/idivio.py");
except:
    exceptionType, exception, traceback=sys.exc_info();
    print "XXXXXXXXXX:  idivio Error "
    logger.dump("---> ", exceptionType, exception, traceback)
    localStationErrorCount+=1

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

# Set up the scan processing wrappers
print "-------------------------------------------------------------------"
print "Set up standard scan processing"
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()
import gdascripts.utils #@UnusedImport
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals() 

scan_processor_normal_processes = scan_processor.processors
scan_processor_empty_processes  = []

def scan_processing_on():
	scan_processor.processors = scan_processor_normal_processes

def scan_processing_off():
	scan_processor.processors = scan_processor_empty_processes

print "-------------------------------------------------------------------"
print "==================================================================="
print "Total number of localStation errors was", localStationErrorCount
print "==================================================================="