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
import sys
try:
    execfile("/dls_sw/i06/software/gda/i06-shared/scripts/localStation.py");
except:
    exceptionType, exception, traceback=sys.exc_info();
    print "Error:  execfile i06-shared 'localStation.py'"
    logger.dump("---> ", exceptionType, exception, traceback)
    
from scan.fastEnergyScan import zacscan,zacstop,zacmode,fesController,fesData, fastEnergy,uuu,i06util  # @UnusedImport

# customised resources for PEEM line
from BeamlineI06.beamline import getTitle,gettitle,getvisit,getVisit,lastscan,setDir,setdir,setTitle,settitle,setVisit,setvisit  # @UnusedImport
from BeamlineI06.createAlias import closebeam, openbeam  # @UnusedImport
from BeamlineI06.Scaler8512 import ca11s,ca12s,ca13s,ca14s,ca21s,ca22s,ca23s,ca24s,ca31s,ca32s,ca33s,ca34s,ca41s,ca42s,ca43s,ca44s,ca11sr,ca12sr,ca13sr,ca14sr,ca21sr,ca22sr,ca23sr,ca24sr,ca31sr,ca32sr,ca33sr,ca34sr,ca41sr,ca42sr,ca43sr,ca44sr,scalar1raw,scaler1  # @UnusedImport
from BeamlineI06.U1Scaler8513 import ca51sr,ca52sr,ca53sr,ca54sr,scalar3  # @UnusedImport

#To eLog the scan
from BeamlineI06.beamline import peemline
from i06shared.setSrsDataFileHeader import fileHeader
fileHeader.setScanLogger(peemline)

#PEEM End Station
from peem.leem_instances import leem2000, leem_fov, leem_obj, leem_stv, leem_objStigmA, leem_objStigmB, leem_p2alignx  # @UnusedImport
from peem.stv_obj_instance import stvobj  # @UnusedImport

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
    

from RGA.rga4 import rgaPeem,rga4Ar,rga4CH4,rga4CO,rga4CO2,rga4H2,rga4H2O,rga4O2,rga4tot  # @UnusedImport
from RGA.rga5 import rgaPreparation, rga5Ar,rga5CH4,rga5CO,rga5CO2,rga5H2,rga5H2O,rga5O2,rga5tot  # @UnusedImport

#from slits.useS4 import s4ygap, s4xgap
#To add PEE line device position to the SRS file header
peemMirrorList = [m3x, m3pitch, m3qg]; fileHeader.add(peemMirrorList);  # @UndefinedVariable
peemDiodeList = [d5x, d6y, d7x, d7ax]; fileHeader.add(peemDiodeList);  # @UndefinedVariable
peemExitSlitList = [s4x, s4xgap, s4y, s4ygap]; fileHeader.add(peemExitSlitList);  # @UndefinedVariable
peemList = [psx, psy]; fileHeader.add(peemList);  # @UndefinedVariable
#Group the hexapod legs into list
m3legs = [m3leg1, m3leg2, m3leg3, m3leg4, m3leg5, m3leg6];  # @UndefinedVariable

from BeamlineI06.KBMirrors import m4bend1g,m4bend2g,m5bend1g,m5bend2g,kbpiezoh,kbpiezov,kbraster,vertFactor,horizFactor,kbpreview,kbimaging,kboff,kbfov  # @UnusedImport
from BeamlineI06.Users.XEnergy.xenergy import ins_device,xenergy,offxenergy,xpol,xmode,offhar,detune,idxmcd,idxas,idd,idu  # @UnusedImport

print "==================================================================="; print; print;

print "end of localStation.py for Beamline I06)"



