#localStation.py
#For beamline specific initialisation code.
from scannables.EnumPVScannable import EnumPVScannable

print("=" *100)
print("Performing Beamline I06 specific initialisation code (localStation.py).\n")
from Diamond.Utility.Functions import logger
print("-"*100)
print("Set scan returns to the start positions on completion")
print("   To set scan returns to its start positions on completion please do:")
print("      >>>scansReturnToOriginalPositions=1\n")
scansReturnToOriginalPositions=1;

from i06shared.localStation import *  # @UnusedWildImport

from BeamlineI06.createAlias import closebeam, openbeam  # @UnusedImport

if installation.isLive():
    from BeamlineI06.U1Scaler8513 import ca51sr,ca52sr,ca53sr,ca54sr,scalar3  # @UnusedImport
    from RGA.rga4 import rgaPeem,rga4Ar,rga4CH4,rga4CO,rga4CO2,rga4H2,rga4H2O,rga4O2,rga4tot  # @UnusedImport
    from RGA.rga5 import rgaPreparation, rga5Ar,rga5CH4,rga5CO,rga5CO2,rga5H2,rga5H2O,rga5O2,rga5tot  # @UnusedImport
    from scannables.m4m5finepitches import m4fpitch, m5fpitch  # @UnusedImport
    
#     from beam.BeamSize_Class import beamsize  # @UnusedImport
#     from BeamlineI06.KBMirrors import m4bend1g,m4bend2g,m5bend1g,m5bend2g,kbpiezoh,kbpiezov,kbraster,vertFactor,horizFactor,kbpreview,kbimaging,kboff,kbfov  # @UnusedImport
else:
    print("Running in dummy mode")

#Group the hexapod legs into list
m3legs = [m3leg1, m3leg2, m3leg3, m3leg4, m3leg5, m3leg6];  # @UndefinedVariable

from peem.leem_scannables import leem_FOV_A, leem_FOV_B, leem_intermlens, leem_obj, leem_objAlignX, leem_objAlignY, leem_objStigmA, leem_objStigmB, leem_p3alignx, leem_p3aligny, leem_rot, leem_stv, leem_temp, leem_transferlens  # @UnusedImport

def picture(acqTime):
    scan(t,1,1,1,pcotif,acqTime)  # @UndefinedVariable
from gda.jython.commands.GeneralCommands import alias
alias("picture")
#
def enableRastering():
    from gdaserver import medipix  # @UnresolvedImport
    medipix.getCollectionStrategy().getDecoratee().getDecoratee().getDecoratee().setEnable(True)
alias("enableRastering")

def disableRatsering():
    from gdaserver import medipix  # @UnresolvedImport
    medipix.getCollectionStrategy().getDecoratee().getDecoratee().getDecoratee().setEnable(False)
alias("disableRatsering")
  
if installation.isLive():
    def medipix_unrotate():
        caput("BL06I-EA-DET-02:ROT:Angle",0)
    alias("medipix_unrotate")
    
    def medipix_rotate():
        rot=caget("BL06I-EA-LEEM-01:CALC:ROT:ANGLE")
        caput("BL06I-EA-DET-02:ROT:Angle",rot)
    alias("medipix_rotate")
        
    def unrotate():
        caput("BL06I-EA-DET-02:ROT:Angle",0)
    alias("unrotate")
    
    def rotate():
        rot=caget("BL06I-EA-LEEM-01:CALC:ROT:ANGLE")
        caput("BL06I-EA-DET-02:ROT:Angle",rot)
    alias("rotate")
    
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
else:
    def medipix_unrotate():
        raise RuntimeError("EPICS PV and IOC required!")
    alias("medipix_unrotate")
    
    def medipix_rotate():
        raise RuntimeError("EPICS PV and IOC required!")
    alias("medipix_rotate")
    
    def unrotate():
        raise RuntimeError("EPICS PV and IOC required!")
    alias("unrotate")
    
    def rotate():
        raise RuntimeError("EPICS PV and IOC required!")
    alias("rotate")

LocalProperties.set("run.in.gda", True) # property 'run.in.gda' must be set before import add_pixel_mask, remove_pixel_mas
from i06shared.metadata.detectorPixelMask import add_pixel_mask, remove_pixel_mask # @UnusedImport

from i06shared.scan.installStandardScansWithAdditionalScanListeners import *  # @UnusedWildImport
scan_processor.rootNamespaceDict=globals()  
import gdascripts
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()  # @UndefinedVariable

from beam.beam_centering import centerBeam  # @UnusedImport

print("="*100)
print("end of localStation.py for Beamline I06)")



