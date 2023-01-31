from gdaserver import fatt, exr, exv, excalibur, excalibur_atten
from gda.configuration.properties import LocalProperties

add_default(fatt)

def att(attenuation=None):
    if attenuation != None:
        pos(fatt, attenuation)
    else :
        pos(fatt)


def autofon():
    exr.setDetector(excalibur_atten)
    exv.setDetector(excalibur_atten)
    LocalProperties.set("gda.beamline.auto.attenuation", "true")
    exc_scan = getRunnableDeviceService().getRunnableDevice("BL07I-ML-SCAN-01")
    procs = exc_scan.getProcessing().getProcessorMap()
    atten = [conf for conf in procs if conf.detFileNameSuffix() == "-attenuation.h5"]
    for a in atten:
        for proc in procs[a]:
            proc.setEnabled(True)
    print("Automatic attenuation enabled for exr, exv and exc")


def autofoff():
    exr.setDetector(excalibur)
    exv.setDetector(excalibur)
    LocalProperties.set("gda.beamline.auto.attenuation", "false")
    exc_scan = getRunnableDeviceService().getRunnableDevice("BL07I-ML-SCAN-01")
    procs = exc_scan.getProcessing().getProcessorMap()
    atten = [conf for conf in procs if conf.detFileNameSuffix() == "-attenuation.h5"]
    for a in atten:
        for proc in procs[a]:
            proc.setEnabled(False)
    fatt.manualMode()
    print("Automatic attenuation disabled for exr, exv and exc")

def exc_fast_exp_time(time=None):
    if time==None:
        print("exc_fast_exp_time : " + excalibur_atten.getCollectionStrategy().getFastExpTime())
    elif time<=0:
        raise ValueError("exc_fast_exp_time must be positive.")
    else:
        excalibur_atten.getCollectionStrategy().setFastExpTime(time)

# Default to off
autofoff()

alias(att)
alias(autofon)
alias(autofoff)
alias(exc_fast_exp_time)

