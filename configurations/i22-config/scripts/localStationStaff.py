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

rds = mscanHandler.runnableDeviceService
p1xy_fly = rds.getRunnableDevice("BL22I-ML-SCAN-01")
base_fly = rds.getRunnableDevice("BL22I-ML-SCAN-02")
time_fly = rds.getRunnableDevice("BL22I-ML-SCAN-03")

def caputWithCheck(pvChannel, pvValue):

    if (caget(pvChannel) != pvValue):
        valueHasBeenTaken = 0
        caput(pvChannel, pvValue)
        sleep(0.3)

#        This functionality isn't currently fully tested and seems to enter into an infinite loop from time to time.
#       I could put in a limit of retries but I'd like first to solve *why* it's failing but not in front of users who are waiting for their experiment to start!
#         while (valueHasBeenTaken != 1):
#             sleep(0.15)
#
#             if (caget(pvChannel) == pvValue):
#                 valueHasBeenTaken == 1
#             else:
#                 caput(pvChannel, pvValue)


def resetPilatusDetector(detectorPVprefix, detectorType):
    # We need to reset everything to a safe state for this detector
    # the anticipated path through areaDetector is CAM --> CDC --> HDF5
    # Malcolm will touch CAM and HDF, not CDC so we will need to undo it's
    # changes there more rigorously that elsewhere...

    if (detectorType == "SAXS"):
        PVprefix = "SAXS"
    elif (detectorType == "WAXS"):
        PVprefix = "TWOML"

    # So, let's start by reconfiguring CAM
    caputWithCheck (detectorPVprefix + ':CAM:ImageMode', "Multiple")
    caputWithCheck(detectorPVprefix + ':CAM:TriggerMode', "Ext. Enable")

    # Then CDC
    caputWithCheck(detectorPVprefix + ':CDC:NDArrayPort', PVprefix + '.PIL.CAM')

    # Then, finally, HDF5
    caputWithCheck(detectorPVprefix + ':HDF5:NDArrayPort', PVprefix +'.PIL.CDC')
    caputWithCheck(detectorPVprefix + ':HDF5:Compression', 'Blosc')
    caputWithCheck(detectorPVprefix + ':HDF5:PositionMode', 'Off')
    caputWithCheck(detectorPVprefix + ':HDF5:XMLFileName', '0')


def resetTetrammDetector(detectorPVprefix, detectorType):
    # We need to reset everything to a safe state for this detector
    # the anticipated path through areaDetector is DRV --> HDF5
    # Malcolm will touch DRV and HDF so we will need to undo it's
    # changes

    if (detectorType == "I0"):
        PVprefix = "XBPM2"
    elif (detectorType == "It"):
        PVprefix = "TTRM2"

    # So, let's start by reconfiguring DRV
    caputWithCheck(detectorPVprefix + ':DRV:TriggerMode', '0')
    caputWithCheck(detectorPVprefix + ':DRV:AveragingTime', '0.1')

    # Then POS
    caputWithCheck(detectorPVprefix + ':POS:Filename', '0')

    # And then HDF5
    caputWithCheck(detectorPVprefix + ':HDF5:NDArrayPort', PVprefix + '.DRV')
    caputWithCheck(detectorPVprefix + ':HDF5:FileWriteMode', '2')
    caputWithCheck(detectorPVprefix + ':HDF5:NDArrayAddress', '11')
    caputWithCheck(detectorPVprefix + ':HDF5:XMLFileName', '0')
    caputWithCheck(detectorPVprefix + ':HDF5:PositionMode', 'Off')

    # Turn back on acquisition!
    caputWithCheck(detectorPVprefix + ':DRV:Acquire', '1')

def resetOpticalDetector(detectorPVprefix):
    # We need to reset everything to a safe state for this detector
    # the anticipated path through areaDetector is DRV --> TRS --> OVER --> ARR or MJPG
    # Malcolm will touch DRV and HDF so we will need to undo it's
    # changes

    # So, let's start by reconfiguring DET
    caputWithCheck(detectorPVprefix + ':DET:TriggerMode', 'Off')
    caputWithCheck(detectorPVprefix + ':DET:ImageMode', 'Continuous')
    caputWithCheck(detectorPVprefix + ':DET:TriggerSource', 'Freerun')

    # Then TRS
    caputWithCheck(detectorPVprefix + ':TRS:NDArrayPort', 'OAVC.cam')
    caputWithCheck(detectorPVprefix + ':TRS:EnableCallbacks', 'Enable')
    caputWithCheck(detectorPVprefix + ':TRS:Type', 'Mirror')

    # Then OVER
    caputWithCheck(detectorPVprefix + ':OVER:NDArrayPort', 'OAVC.trs')
    caputWithCheck(detectorPVprefix + ':OVER:EnableCallbacks', 'Enable')

    # Then ARR
    caputWithCheck(detectorPVprefix + ':ARR:NDArrayPort', 'OAVC.over')
    caputWithCheck(detectorPVprefix + ':ARR:EnableCallbacks', 'Enable')

    # And finally, MJPG
    caputWithCheck(detectorPVprefix + ':ARR:NDArrayPort', 'OAVC.over')
    caputWithCheck(detectorPVprefix + ':ARR:EnableCallbacks', 'Enable')

    # Turn back on acquisition!
    caputWithCheck(detectorPVprefix + ':DET:Acquire', '1')


def resetSAXSdetector():
    print('Setting up SAXS detector')
    resetPilatusDetector('BL22I-EA-PILAT-01', 'SAXS')
    print('SAXS detector set up')


def resetWAXSdetector():
    print('Setting up WAXS detector')
    resetPilatusDetector('BL22I-EA-PILAT-03', 'WAXS')
    print('WAXS detector set up')


def resetI0Tetramm():
    print('Setting up I0 amplifier')
    resetTetrammDetector('BL22I-EA-XBPM-02', 'I0')
    print('I0 amplifier set up')


def resetBsdiodesTetramm():
    print('Setting up beamstop diode amplifier')
    resetTetrammDetector('BL22I-EA-TTRM-02', 'It')
    print('Beamstop diode amplifier set up')


def resetOAV():
    print('Setting up on-axis optical camera')
    resetOpticalDetector('BL22I-DI-OAV-01')
    print('On-axis optical camera set up')


def reEnableTetramms():
    print('Changing to linescan acquisition mode')
    resetI0Tetramm()
    resetBsdiodesTetramm()
    print('Mode change complete')


def tfgAcquisition():
    print('Changing to TFG acquisition mode')
    resetSAXSdetector()
    resetWAXSdetector()
    resetI0Tetramm()
    resetBsdiodesTetramm()
    resetOAV()
    print('Mode change complete')

def pandaAcquisition():
    print('Changing to mapping acquisition mode')
    caputWithCheck('BL22I-EA-XBPM-02:HDF5:NDArrayAddress', '0')
    caputWithCheck('BL22I-EA-TTRM-02:HDF5:NDArrayAddress', '0')
    print('Mode change complete')

def resetMalcolm():
    print('Starting Malcolm reset')
    caput('BL22I-CS-IOC-16:STOP', 1)
    caput('BL22I-CS-IOC-17:STOP', 1)
    caput('BL22I-EA-PILAT-01:RESTART', 1)
    caput('BL22I-EA-PILAT-03:RESTART', 1)
    sleep(120)
    print('Pilatus detectors reset')
    caput('BL22I-CS-IOC-16:START', 1)
    caput('BL22I-CS-IOC-17:START', 1)
    caput('BL22I-DI-IOC-03:RESTART', 1)
    caput('BL22I-EA-IOC-09:RESTART', 1)
    sleep(60)
    print('PandABoxes & OAV reset')
    caput('BL22I-ML-MALC-01:RESTART', 1)
    sleep(30)
    print('All reset.')

def resetPandABox():
    caput('BL22I-EA-IOC-09:RESTART', 1)
    sleep(30)
    print('PandABox Reset Done.')


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

##########################
# User Specific Commands #
##########################

def AFL_Acquisition(scan_title = 'Scan', background_frame = '730798', frame_time = 1000, num_frames = 1, x_position = 1, y_position = 1):
    pos eh_shutter 'Open'
    pos base_x x_position
    pos base_y y_position
    setTitle(scan_title)
    setSampleBackground('/dls/i22/data/2024/sm35647-1/i22-' + background_frame + '.nxs')

    with tfgGroups():
        addGroup(num_frames, 10, frame_time, '00100000', '11111111')

    staticscan ncddetectors


def AFL_Background(scan_title = 'Scan', frame_time = 1000, num_frames = 1, x_position = 1, y_position = 1):
    pos eh_shutter 'Open'
    pos base_x x_position
    pos base_y y_position
    setTitle(scan_title)

    with tfgGroups():
        addGroup(num_frames, 10, frame_time, '00100000', '11111111')

    staticscan ncddetectors
    print(gda.jython.InterfaceProvider.getScanDataPointProvider().getLastScanDataPoint().getScanIdentifier())
