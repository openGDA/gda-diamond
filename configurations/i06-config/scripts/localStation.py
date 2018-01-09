#localStation.py
#For beamline specific initialisation code.
from i06shared import installation

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
import sys
from gda.jython.commands.GeneralCommands import alias
from gda.jython.commands.ScannableCommands import scan

# try:
#     execfile("/dls_sw/i06/software/gda/i06-shared/scripts/i06shared/localStation.py");
# except:
#     exceptionType, exception, traceback=sys.exc_info();
#     print "Error:  execfile i06-shared 'localStation.py'"
#     logger.dump("---> ", exceptionType, exception, traceback)

from i06shared.localStation import *  # @UnusedWildImport
    
#from scan.fastEnergyScan import zacscan,zacstop,zacmode,fesController,fesData, fastEnergy,uuu,beamlineutil  # @UnusedImport

# customised resources for PEEM line
from BeamlineI06.beamline import peemline, getTitle,gettitle,getvisit,getVisit,lastscan,setDir,setdir,setTitle,settitle,setVisit,setvisit  # @UnusedImport
#from i06shared.setSrsDataFileHeader import fileHeader
fileHeader.setScanLogger(peemline)
from BeamlineI06.createAlias import closebeam, openbeam  # @UnusedImport

if installation.isLive():
    from BeamlineI06.U1Scaler8513 import ca51sr,ca52sr,ca53sr,ca54sr,scalar3  # @UnusedImport
    from RGA.rga4 import rgaPeem,rga4Ar,rga4CH4,rga4CO,rga4CO2,rga4H2,rga4H2O,rga4O2,rga4tot  # @UnusedImport
    from RGA.rga5 import rgaPreparation, rga5Ar,rga5CH4,rga5CO,rga5CO2,rga5H2,rga5H2O,rga5O2,rga5tot  # @UnusedImport
    from BeamlineI06.KBMirrors import m4bend1g,m4bend2g,m5bend1g,m5bend2g,kbpiezoh,kbpiezov,kbraster,vertFactor,horizFactor,kbpreview,kbimaging,kboff,kbfov  # @UnusedImport
else:
    print "Running in dummy mode"

#from slits.useS4 import news4xgap, news4ygap  # @UnusedImport
#from slits.useS4 import s4ygap, s4xgap
#To eLog the scan

USE_UVIEW=False
if USE_UVIEW:
    try:
        from peem.usePEEM import roi1,roi2,roi3,roi4,uvroi,uvpreview,uvimaging,picture  # @UnusedImport
        #the following line is only for TCPIP connection in GDA.
        from peem.uv_leem_reconnect import reconnect  # @UnusedImport
        from peem.idio_peem_rois import roi1io,roi2io,roi3io,roi4io  # @UnusedImport
    except:
        exceptionType, exception, traceback=sys.exc_info();
        print "Error:  import 'from peem.usePEED'"
        logger.dump("---> ", exceptionType, exception, traceback)
    


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
from peem.leem_instances import leem2000, leem_fov, leem_obj, leem_stv, leem_objStigmA, leem_objStigmB, leem_p2alignx  # @UnusedImport
fileHeader.add([leem_fov, leem_obj, leem_stv, leem_objStigmA, leem_objStigmB])
from peem.stv_obj_instance import stvobj  # @UnusedImport
from peem.LEEM2000_scannables_init import leem_rot,leem_temp,objAlignY,objAlignX  # @UnusedImport

def picture(acqTime):
    scan(t,1,1,1,pcotif,acqTime)  # @UndefinedVariable
alias("picture")

from gda.jython.commands.ScannableCommands import add_default
add_default([fileHeader]);

print "==================================================================="
print "end of localStation.py for Beamline I06)"



