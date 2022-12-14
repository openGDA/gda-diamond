from gdaserver import fatt
from gda.configuration.properties import LocalProperties

EXCALIBUR_RD_NAME = "BL07I-ML-SCAN-01"

# Set of Strings of runnable device names
detectors = scanRequest.getDetectors().keySet()


if LocalProperties.check("gda.beamline.auto.attenuation", False) and EXCALIBUR_RD_NAME in detectors:
    print("Setting auto attenuation for continuous scan")
    fatt.continuousMode()
else:
    print("Setting manual attenuation")
    fatt.manualMode()
