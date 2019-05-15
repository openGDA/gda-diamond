#localStation.py
#For beamline specific initialisation code.

print "===================================================================";
print "Performing Beamline I06 specific initialisation code (localStation.py).";
print
from Diamond.Utility.Functions import logger
print "-"*100
print "Set scan returns to the start positions on completion"
print "   To set scan returns to its start positions on completion please do:"
print "      >>>scansReturnToOriginalPositions=1"
scansReturnToOriginalPositions=0;
print

from i06shared.localStation import *  # @UnusedWildImport
    
#from scan.fastEnergyScan import zacscan,zacstop,zacmode,fesController,fesData, fastEnergy,uuu,beamlineutil  # @UnusedImport

# customised resources for PEEM line
from BeamlineI06.beamline import peemline, getTitle,gettitle,getvisit,getVisit,lastscan,setDir,setdir,setTitle,settitle,setVisit,setvisit  # @UnusedImport
from BeamlineI06.createAlias import closebeam, openbeam  # @UnusedImport

#To eLog the scan
#from i06shared.setSrsDataFileHeader import fileHeader
fileHeader.setScanLogger(peemline)

if installation.isLive():
    from BeamlineI06.U1Scaler8513 import ca51sr,ca52sr,ca53sr,ca54sr,scalar3  # @UnusedImport
    from RGA.rga4 import rgaPeem,rga4Ar,rga4CH4,rga4CO,rga4CO2,rga4H2,rga4H2O,rga4O2,rga4tot  # @UnusedImport
    from RGA.rga5 import rgaPreparation, rga5Ar,rga5CH4,rga5CO,rga5CO2,rga5H2,rga5H2O,rga5O2,rga5tot  # @UnusedImport
    from beam.BeamSize_Class import beamsize  # @UnusedImport
#     from BeamlineI06.KBMirrors import m4bend1g,m4bend2g,m5bend1g,m5bend2g,kbpiezoh,kbpiezov,kbraster,vertFactor,horizFactor,kbpreview,kbimaging,kboff,kbfov  # @UnusedImport
else:
    print "Running in dummy mode"

# USE_UVIEW=False
# if USE_UVIEW:
#     try:
#         from peem.usePEEM import roi1,roi2,roi3,roi4,uvroi,uvpreview,uvimaging,picture  # @UnusedImport
#         #the following line is only for TCPIP connection in GDA.
#         from peem.uv_leem_reconnect import reconnect  # @UnusedImport
#         from peem.idio_peem_rois import roi1io,roi2io,roi3io,roi4io  # @UnusedImport
#     except:
#         exceptionType, exception, traceback=sys.exc_info();
#         print "Error:  import 'from peem.usePEED'"
#         logger.dump("---> ", exceptionType, exception, traceback)
    
#To add PEEM line device position to the SRS file header
print "-"*100
print "Add metadata required by PEEM to file header"
fileHeader.add([m3x, m3pitch, m3qg]);  # @UndefinedVariable
fileHeader.add([d5x, d6y, d7x, d7ax]);  # @UndefinedVariable
fileHeader.add([s4x, s4xgap, s4y, s4ygap]);  # @UndefinedVariable
fileHeader.add([psx, psy]);  # @UndefinedVariable
#Group the hexapod legs into list
m3legs = [m3leg1, m3leg2, m3leg3, m3leg4, m3leg5, m3leg6];  # @UndefinedVariable

#PEEM End Station
if installation.isLive():
    from peem.leem_instances import leem2000, FOV, leem_obj, leem_stv, leem_objStigmA, leem_objStigmB, leem_p2alignx, mcpPlate,mcpScreen  # @UnusedImport
    fileHeader.add([FOV, leem_obj, leem_stv, leem_objStigmA, leem_objStigmB, mcpPlate])
    from peem.stv_obj_instance import stvobj  # @UnusedImport
    from peem.LEEM2000_scannables_init import leem_rot,leem_temp,objAlignY,objAlignX  # @UnusedImport
    fileHeader.add([leem_rot])
else:
    print "No simulation for LEEM control yet!"

def picture(acqTime):
    scan(t,1,1,1,pcotif,acqTime)  # @UndefinedVariable
from gda.jython.commands.GeneralCommands import alias
alias("picture")
#
if installation.isLive():
    def medipix_unrotate():
        caput("BL06I-EA-DET-02:ROT:Angle",0)
    alias("medipix_unrotate")
    
    def medipix_rotate():
        rot=caget("BL06I-EA-LEEM-01:CALC:ROT:ANGLE")
        caput("BL06I-EA-DET-02:ROT:Angle",rot)
    alias("medipix_rotate")
        
    def unrotate():
        caput("BL06I-EA-DET-01:ROT:Angle",0)
    alias("unrotate")
    
    def rotate():
        rot=caget("BL06I-EA-LEEM-01:CALC:ROT:ANGLE")
        caput("BL06I-EA-DET-01:ROT:Angle",rot)
    alias("rotate")
    
    # I06-406   
    temp1_EC3=DisplayEpicsPVClass('temp1_EC3','BL06I-EA-EC3-01:TEMP1','C','%f')
    temp2_EC3=DisplayEpicsPVClass('temp2_EC3','BL06I-EA-EC3-01:TEMP2','C','%f')
    temp3_EC3=DisplayEpicsPVClass('temp3_EC3','BL06I-EA-EC3-01:TEMP3','C','%f')
    temp4_EC3=DisplayEpicsPVClass('temp4_EC3','BL06I-EA-EC3-01:TEMP4','C','%f')
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

from gda.jython.commands.ScannableCommands import add_default
add_default([fileHeader]);

print "==================================================================="
print "end of localStation.py for Beamline I06)"



