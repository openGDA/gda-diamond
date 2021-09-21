#    MainLineUser.py
#
#    For user specific initialisation code on I06 PEEM Line.
import sys

print "--->>>Start initalization of user specific code."

global reset_peem, logger

userScriptsList=["/dls_sw/i06-1/scripts/hello.py"]

# Set up the beamline stauts script
userScriptsList.append("/dls_sw/i06/scripts/status.py")
    
reset_peem

#Set up the XEnergy script
userScriptsList.append("/dls_sw/i06/scripts/beamline/XEnergy/xenergy.py" )

#userScriptsList.append("/dls_sw/i06/scripts/beamline/RS232_class.py")

#Set up the LEEM scannables script
userScriptsList.append("/dls_sw/i06/scripts/instruments/LEEM/LEEM_scannables.py")

#Set up the RGA Monitor script"
userScriptsList.append("/dls_sw/i06/scripts/beamline/RGA_Monitor.py")

#Set up the beamline user additional commands script"
userScriptsList.append("/dls_sw/i06/scripts/beamline/additional_commands.py")

#Set up the KB_Mirror Init script"
userScriptsList.append("/dls_sw/i06/scripts/beamline/KB_Mirror_Init.py")

#pulsing unit
#userScriptsList.append("/dls/i06/scripts/instruments/IsoTech_IPS2010_pulse.py")

for userScript in userScriptsList:
    print "-------------------------------------------------------------------"
    print "Execution of user script: " + userScript + " >>>>>"
    try:
        execfile(userScript);
    except:
        exceptionType, exception, traceback=sys.exc_info();
        print "XXXXXXXXXX:  User script: " + userScript + " Error"
        logger.dump("---> ", exceptionType, exception, traceback)

from scannables import BipolarPS
magPulse=BipolarPS('magPulse', pvBase = 'BL06I-PC-CTRL-01')

print "--->>>Initalization of user specific code done."
