# ===================================================================================
# Configuration of servers after restart/reset
# ===================================================================================

# Uncomment to change which channels and gain settings are used for It and I0 values in nexus files
# NB Commenting this out again after a reset will not return the settings to default until the servers
#    are restarted
#scaler_channels = {'It': NcdChannel(channel=3, scaling=bs2diodegain),
#                   'I0': NcdChannel(channel=1, scaling=d4d2gain)}

# ===================================================================================
# Add any commands that needs to be run after each restart/reset below this line
# ===================================================================================
#diode_y = SingleEpicsPositionerClass('diode_y', 'BL22I-MO-TABLE-05:Y', 'BL22I-MO-TABLE-05:Y.RBV' , 'BL22I-MO-TABLE-05:Y.DMOV' , 'BL22I-MO-TABLE-05:Y.STOP','mm', '%.4f')
#diode_x = SingleEpicsPositionerClass('diode_x', 'BL22I-MO-TABLE-05:X', 'BL22I-MO-TABLE-05:X.RBV' , 'BL22I-MO-TABLE-05:X.DMOV' , 'BL22I-MO-TABLE-05:X.STOP','mm', '%.4f')

from gdascripts.mscanHandler import *
from gdascripts import mscanHandler

rds = mscanHandler.getRunnableDeviceService()
p1xy_fly = rds.getRunnableDevice("BL22I-ML-SCAN-01")
base_fly = rds.getRunnableDevice("BL22I-ML-SCAN-02")
time_fly = rds.getRunnableDevice("BL22I-ML-SCAN-03")

def feedback_SS():
    caput("BL22I-OP-KBM-01:HFM:FBS4.INP","BL22I-EA-XBPM-01:PosX:MeanValue_RBV")
    caput("BL22I-OP-KBM-01:VFM:FBS4.INP","BL22I-EA-XBPM-01:PosY:MeanValue_RBV")
    caput("BL22I-OP-KBM-01:HFM:FBS4.KP", 0.001)
    caput("BL22I-OP-KBM-01:VFM:FBS4.KP", -0.001)
    caput("BL22I-OP-KBM-01:HFM:FBS4.KI", 0.41667)
    caput("BL22I-OP-KBM-01:VFM:FBS4.KI", 0.5208)
    caput("BL22I-EA-XBPM-01:DRV:Geometry", "Square")
    print "Feedback running from XBPM1 at secondary source"
    return
    
def feedback_EH():
    caput("BL22I-OP-KBM-01:HFM:FBS4.INP","BL22I-EA-XBPM-02:PosX:MeanValue_RBV")
    caput("BL22I-OP-KBM-01:VFM:FBS4.INP","BL22I-EA-XBPM-02:PosY:MeanValue_RBV")
    caput("BL22I-OP-KBM-01:HFM:FBS4.KP", 0.001)
    caput("BL22I-OP-KBM-01:VFM:FBS4.KP", -0.001)
    caput("BL22I-OP-KBM-01:HFM:FBS4.KI", 0.41667)
    caput("BL22I-OP-KBM-01:VFM:FBS4.KI", 0.5208)
    caput("BL22I-EA-TTRM-01:DRV:Geometry", "Square")
    print "Feedback running from XBPM2 in experimental hutch"
    return
    
def feedback_auto():
    caput("BL22I-OP-KBM-01:HFM:FBS4:AUTO","Auto")
    caput("BL22I-OP-KBM-01:VFM:FBS4:AUTO","Auto")
    print "Feedback running in auto mode"
    return

def feedback_off():
    caput("BL22I-OP-KBM-01:HFM:FBS4:AUTO","Manual")
    caput("BL22I-OP-KBM-01:HFM:FBS4.FBON","Off")
    caput("BL22I-OP-KBM-01:VFM:FBS4:AUTO","Manual")
    caput("BL22I-OP-KBM-01:VFM:FBS4.FBON","Off")
    print "Feedback is OFF!"
    
def feedback_on():
    caput("BL22I-OP-KBM-01:HFM:FBS4:AUTO","Manual")
    caput("BL22I-OP-KBM-01:HFM:FBS4.FBON","On")
    caput("BL22I-OP-KBM-01:VFM:FBS4:AUTO","Manual")
    caput("BL22I-OP-KBM-01:VFM:FBS4.FBON","On")
    print "Feedback is ON in manual mode"
    
def optimise_pitch():
    feedback_off()
    if qbpm0_total.getPosition() > 1e-8:
        rscan(dcm_pitch,-150,150,2,qbpm0_total)
        inc(dcm_pitch,-150)
        go(peak)
        feedback_auto()
    else:
        print "Not enough beam to optimise - Aborting here"
        feedback_auto()
        return

def enable_pressure():
    from gdaserver import ncd_pressure_cell
    if ncd_pressure_cell not in ncddetectors.detectors:
        ncddetectors.addDetector(ncd_pressure_cell)

def disable_pressure():
    from gdaserver import ncd_pressure_cell
    if ncd_pressure_cell in ncddetectors.detectors:
        ncddetectors.removeDetector(ncd_pressure_cell)

from setup import tfgsetup
def pressure_collection(pressure_from, pressure_to, xray_frames_before, xray_frames_after, frame_time, title):
    with tfgsetup.tfgGroups():
        tfgsetup.addGroup(xray_frames_before, frame_time, 10, runPulse="11101111")
        tfgsetup.addGroup(xray_frames_after, frame_time, 10, runPulse="11111111")
    enable_pressure()
    ncd_pressure_cell.setJumpPressures(pressure_from, pressure_to)
    pressure_samples_before = xray_frames_before * (frame_time+10) * 10
    pressure_samples_after = xray_frames_after * (frame_time+10) * 10
    ncd_pressure_cell.setSamplesBefore(pressure_samples_before)
    ncd_pressure_cell.setSamplesAfter(pressure_samples_after)
    setTitle(title)
    staticscan(ncddetectors)
    disable_pressure()

from setup import sampleCam

d11_ncd = sampleCam.AdCam('d11_ncd', d11gige)
add_reset_hook(lambda ncd=ncddetectors, cam=d11_ncd: ncd.removeDetector(cam))
d12_ncd = sampleCam.AdCam('d12_ncd', d12gige)
add_reset_hook(lambda ncd=ncddetectors, cam=d12_ncd: ncd.removeDetector(cam))

from setup import malcolm_tfg
from gdaserver import Pilatus2M_SAXS, Pilatus2M_WAXS, I0, bsdiodes

saxs_reset = malcolm_tfg.NcdPilatusReset(Pilatus2M_SAXS)
waxs_reset = malcolm_tfg.NcdPilatusReset(Pilatus2M_WAXS)
i0_reset = malcolm_tfg.NcdTetrammReset(I0)
bsdiodes_reset = malcolm_tfg.NcdTetrammReset(bsdiodes)

def install_hook(detector, action):
    detector.addPreScanAction(action)
    add_reset_hook(lambda det=detector, act=action: det.removePreScanAction(act))

install_hook(Pilatus2M_SAXS, saxs_reset)
install_hook(Pilatus2M_WAXS, waxs_reset)
install_hook(I0, i0_reset)
install_hook(bsdiodes, bsdiodes_reset)
