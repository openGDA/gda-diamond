#localStation.py
#For beamline specific initialisation code.
from scannables.EnumPVScannable import EnumPVScannable
from i06shared.scalers.scaler_configuration import is_use_scaler_channel_as_detector  # @UnusedImport

print("=" *100)
print("Performing Beamline I06 specific initialisation code (localStation.py).\n")
print("-"*100)
print("Set scan returns to the start positions on completion")
print("   To set scan returns to its start positions on completion please do:")
print("      >>>scansReturnToOriginalPositions=1\n")
scansReturnToOriginalPositions = 0

from i06shared.localStation import *  # @UnusedWildImport

from BeamlineI06.createAlias import closebeam, openbeam  # @UnusedImport
from BeamlineI06.U1Scaler8513 import ca51sr,ca52sr,ca53sr,ca54sr,scalar3  # @UnusedImport
from scannables.m4m5finepitches import m4fpitch, m5fpitch  # @UnusedImport
        
if installation.isLive():
    from RGA.rga4 import rgaPeem,rga4Ar,rga4CH4,rga4CO,rga4CO2,rga4H2,rga4H2O,rga4O2,rga4tot  # @UnusedImport
    from RGA.rga5 import rgaPreparation, rga5Ar,rga5CH4,rga5CO,rga5CO2,rga5H2,rga5H2O,rga5O2,rga5tot  # @UnusedImport
    
#     from beam.BeamSize_Class import beamsize  # @UnusedImport
#     from BeamlineI06.KBMirrors import m4bend1g,m4bend2g,m5bend1g,m5bend2g,kbpiezoh,kbpiezov,kbraster,vertFactor,horizFactor,kbpreview,kbimaging,kboff,kbfov  # @UnusedImport
else:
    print("Running in dummy mode")

LocalProperties.set(LocalProperties.GDA_END_STATION_NAME, "PEEM")

#Group the hexapod legs into list
m3legs = [m3leg1, m3leg2, m3leg3, m3leg4, m3leg5, m3leg6];  # @UndefinedVariable

from peem.leem_scannables import leem_FOV_A, leem_FOV_B, leem_intermlens, leem_obj, leem_objAlignX, leem_objAlignY, leem_objStigmA, leem_objStigmB, leem_p3alignx, leem_p3aligny, leem_rot, leem_stv, leem_temp, leem_transferlens, leem_AC_state  # @UnusedImport
def picture(acqTime):
    scan(t,1,1,1,medipix,acqTime)  # @UndefinedVariable
from gda.jython.commands.GeneralCommands import alias
alias("picture")
#
def preview():
    from time import sleep
    from gdaserver import medipixpreview  # @UnresolvedImport
    from gda.scan import ScanInformation
    medipixpreview.getCollectionStrategy().saveState()
    medipixpreview.stop()
    sleep(1)
    medipixpreview.getCollectionStrategy().prepareForCollection(0.1, 3, ScanInformation.EMPTY)
    medipixpreview.collectData()
    
def stop_preview():
    from gdaserver import medipixpreview  # @UnresolvedImport
    medipixpreview.stop()
    medipixpreview.getCollectionStrategy().restoreState()
    
def enableRastering():
    from gdaserver import medipix  # @UnresolvedImport
    medipix.getCollectionStrategy().getDecoratee().getDecoratee().getDecoratee().getDecoratee().getDecoratee().setEnabled(True)
alias("enableRastering")

def disableRastering():
    from gdaserver import medipix  # @UnresolvedImport
    medipix.getCollectionStrategy().getDecoratee().getDecoratee().getDecoratee().getDecoratee().getDecoratee().setEnabled(False)
alias("disableRastering")
  
if installation.isLive():
    
    def set_medipix_acquire_time(t):
        stopped_by_me=False
        ACQUIRE_PV = "BL06I-EA-DET-02:CAM:Acquire"
        if caget(ACQUIRE_PV) == 1:
            caput(ACQUIRE_PV,0)
            stopped_by_me = True
        caput("BL06I-EA-DET-02:CAM:AcquireTime", t)
        caput("BL06I-EA-DET-02:CAM:AcquirePeriod", t+0.003)
        if stopped_by_me:
            caput(ACQUIRE_PV,1)
    alias("set_medipix_acquire_time")
    
    # I06-406   
    temp1_EC3=DisplayEpicsPVClass('temp1_EC3','BL06I-EA-EC3-01:TEMP1','C','%f')
    temp2_EC3=DisplayEpicsPVClass('temp2_EC3','BL06I-EA-EC3-01:TEMP2','C','%f')
    temp3_EC3=DisplayEpicsPVClass('temp3_EC3','BL06I-EA-EC3-01:TEMP3','C','%f')
    temp4_EC3=DisplayEpicsPVClass('temp4_EC3','BL06I-EA-EC3-01:TEMP4','C','%f')
    
    try:
        mpxmode=EnumPVScannable("mpxmode", "BL06I-EA-DET-02:CAM:QuadMerlinMode")
        mpxmode.configure()
    except:
        print("Cannot connect to BL06I-EA-DET-02:CAM:QuadMerlinMode, so 'mpxmode' is not available.")
    
    from kbRastering.rasteringUseKeysight import *  # @UnusedWildImport
    
    def average(avg):
        from time import sleep
        caput('BL06I-EA-DET-02:PROCB:NumFilter',avg)
        sleep(0.1)
        caput('BL06I-EA-DET-02:PROCB:ResetFilter',1)
        sleep(0.1)
        caput('BL06I-EA-DET-02:PROCB:EnableFilter','Enable')
    
    alias("average")

LocalProperties.set("run.in.gda", True) # property 'run.in.gda' must be set before import add_pixel_mask, remove_pixel_mas
from i06shared.metadata.detectorPixelMask import add_pixel_mask, remove_pixel_mask # @UnusedImport

from i06shared.scan.installStandardScansWithAdditionalScanListeners import *  # @UnusedWildImport
scan_processor.rootNamespaceDict = globals()  
import gdascripts
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()  # @UndefinedVariable

from beam.beam_centering import centerBeam  # @UnusedImport
from i06shared.keithley.keithley2461_scannables_instances import keiCur, keiVolt, keithley2461  # @UnusedImport

from Diamond.PseudoDevices.EpicsDevices import EpicsMonitorClass
top_up_countdown = EpicsMonitorClass('top_up_countdown', 'SR-CS-FILL-01:STACOUNTDN', 'sec', '%f')

# NXxas App Def template objects
print("-"*100)
print("load 'xasmode' scannable")
XAS_MODES = ['TEY', 'TFY_ft', 'TFY_fb']
TEY, TFY_ft, TFY_fb = XAS_MODES
xasmode = XASMode("xasmode", XAS_MODES, mode = TEY)
mode_path_fast = {TEY: "/entry/instrument/fesData/C1", TFY_ft: "/entry/instrument/fesData/C3", TFY_fb: "/entry/instrument/fesData/C4"}
mode_path_slow = {TEY: "/entry/instrument/ca51sr/ca51sr", TFY_ft: "/entry/instrument/ca53sr/ca53sr", TFY_fb: "/entry/instrument/ca54sr/ca54sr"}
xasmode_fast = XASModePathMapper("xasmode_fast", xasmode, mode_path_fast)
xasmode_slow = XASModePathMapper("xasmode_slow", xasmode, mode_path_slow)
xasscan.NEXUS_TEMPLATE_YAML_FILE_NAME = "NXxas_template_slowscan.yaml"
xasscan.xasmode_scannable_name = "xasmode"
# sample temperature
tsample = temp  # @UndefinedVariable

from scans.xray_dichroism import xmcd, CRW, SRW  # @UnusedImport
from scans.flat_field import flatField  # @UnusedImport

#--new default processor DP 20/01/26
from gda.device.scannable import ProcessingScannable
from gda.jython.commands.ScannableCommands import add_default
nexus_processor = ProcessingScannable('nexus_processor')
nexus_processor['mmg-nexus'] = [{'nxs2dat': False}]
add_default(nexus_processor)

from scannables.leem_projection import leem_presetA  # @UnusedImport
extractor_voltage = VirtualScannable("extractor_voltage", initial_value=2000.0, value_format="%f")
energy_interval = VirtualScannable("energy_interval", initial_value=0.0, value_format="%f")

from scannables.image_inversion import x_inversion  # @UnusedImport

print("="*100)
print("end of localStation.py for Beamline I06)")



