#localStation.py
#For beamline specific initialisation code.
from scannables.EnumPVScannable import EnumPVScannable

print("="*100)
print("Performing Beamline I06-2 specific initialisation code (localStation.py).\n")
print("-"*100)
print("Set scan returns to the start positions on completion")
print("   To set scan returns to its start positions on completion please do:")
print("      >>>scansReturnToOriginalPositions=1\n")
scansReturnToOriginalPositions=0;

from i06shared.localStation import *  # @UnusedWildImport
    
from peem.leem_scannables import leem_FOV_A, leem_FOV_B, leem_intermlens, leem_obj, leem_objAlignX, leem_objAlignY, leem_objStigmA, leem_objStigmB, leem_p3alignx, leem_p3aligny, leem_rot, leem_stv, leem_temp, leem_transferlens  # @UnusedImport

print("-"*100)
print("Set 'rotate' and unrotate' commands for medipix detector image")
from gda.jython.commands.GeneralCommands import alias
#
if installation.isLive():
    def rotate():
        rot=caget("BL06K-EA-LEEM-01:CALC:ROT:ANGLE")
        caput("BL06K-EA-DET-01:ROT:Angle",rot)
    alias("rotate")
    
    def set_medipix_acquire_time(t):
        stopped_by_me=False
        ACQUIRE_PV = "BL06K-EA-DET-01:CAM:Acquire"
        if caget(ACQUIRE_PV) == 1:
            caput(ACQUIRE_PV,0)
            stopped_by_me = True
        caput("BL06K-EA-DET-01:CAM:AcquireTime", t)
        caput("BL06K-EA-DET-01:CAM:AcquirePeriod", t+0.003)
        if stopped_by_me:
            caput(ACQUIRE_PV,1)
    alias("set_medipix_acquire_time")
    
  
    try:
        mpxmode=EnumPVScannable("mpxmode", "BL06K-EA-DET-01:CAM:QuadMerlinMode")
        mpxmode.configure()
    except:
        print("Cannot connect to BL06K-EA-DET-01:CAM:QuadMerlinMode, so 'mpxmode' is not available.")
    
    def average(avg):
        caput('BL06K-EA-DET-01:PROCB:NumFilter',avg)
        from time import sleep
        sleep(0.1)
        caput('BL06K-EA-DET-01:PROCB:ResetFilter',1)
        sleep(0.1)
        caput('BL06K-EA-DET-01:PROCB:EnableFilter','Enable')
    
    alias("average")
else:
    def unrotate():
        raise RuntimeError("EPICS PV and IOC required!")
    alias("unrotate")
    
    def rotate():
        raise RuntimeError("EPICS PV and IOC required!")
    alias("rotate")

print("="*100)
print("end of localStation.py for Beamline I06-2)")



