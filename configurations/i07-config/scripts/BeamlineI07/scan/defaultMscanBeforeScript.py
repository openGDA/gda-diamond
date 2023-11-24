from gdaserver import fatt
from gda.configuration.properties import LocalProperties
from time import sleep
from gdascripts.utils import caput

EXCALIBUR_RD_NAME = "BL07I-ML-SCAN-01"
EXCALIBUR_STATIC_NAME = "BL07I-ML-SCAN-11"
P2_STATIC_NAME = "BL07I-ML-SCAN-12"
P3_STATIC_NAME = "BL07I-ML-SCAN-32"

# Set of Strings of runnable device names
detectors = scanRequest.getDetectors().keySet()

if LocalProperties.check("gda.beamline.auto.attenuation", False) and ( EXCALIBUR_RD_NAME in detectors or EXCALIBUR_STATIC_NAME in detectors ):
    print("Setting auto attenuation for continuous scan")
    fatt.manualMode()
    sleep(0.2)
    fatt.continuousMode()
else:
    print("Setting manual attenuation")
    fatt.manualMode()

#caput("BL07I-MO-STEP-08:COORDINATE_SYS_GROUP", "Empty")
if ( P2_STATIC_NAME in detectors or P3_STATIC_NAME in detectors or EXCALIBUR_STATIC_NAME in detectors ):
    caput("BL07I-MO-STEP-08:COORDINATE_SYS_GROUP", "Static")
else :
    caput("BL07I-MO-STEP-08:COORDINATE_SYS_GROUP", "Direct Mapping")
#sleep(0.1)
