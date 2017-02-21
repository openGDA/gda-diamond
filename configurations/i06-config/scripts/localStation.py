#localStation.py
#For beamline specific initialisation code.
print "===================================================================";
print "Performing Beamline I06 specific initialisation code (localStation.py).";
print

print "-"*100
print "Set scan returns to the start positions on completion"
print "   To set scan returns to its start positions on completion please do:"
print "      >>>scansReturnToOriginalPositions=1"
scansReturnToOriginalPositions=0;
print

from i06shared.localStation import *

from BeamlineI06.beamline import getTitle,gettitle,getvisit,getVisit,lastscan,setDir,setdir,setTitle,settitle,setVisit,setvisit  # @UnusedImport
from BeamlineI06.createAlias import closebeam, openbeam  # @UnusedImport
from BeamlineI06.Scaler8512 import ca11s,ca12s,ca13s,ca14s,ca21s,ca22s,ca23s,ca24s,ca31s,ca32s,ca33s,ca34s,ca41s,ca42s,ca43s,ca44s,ca11sr,ca12sr,ca13sr,ca14sr,ca21sr,ca22sr,ca23sr,ca24sr,ca31sr,ca32sr,ca33sr,ca34sr,ca41sr,ca42sr,ca43sr,ca44sr,scalar1raw,scaler1  # @UnusedImport
from BeamlineI06.U1Scaler8513 import ca51sr,ca52sr,ca53sr,ca54sr,scalar3  # @UnusedImport

#To eLog the scan
from BeamlineI06.beamline import peemline
fileHeader.setScanLogger(peemline);

from peem.leem_instances import leem2000, leem_fov, leem_obj, leem_stv, leem_objStigmA, leem_objStigmB, leem_p2alignx  # @UnusedImport
from peem.usePEEM import roi1,roi2,roi3,roi4,uvroi,uvpreview,uvimaging,picture  # @UnusedImport

from BeamlineI06.useS4 import s4ygap
#To add branchline device position to the SRS file header
peemMirrorList = [m3x, m3pitch, m3qg]; fileHeader.add(peemMirrorList);  # @UndefinedVariable
peemDiodeList = [d5x, d6y, d7x, d7ax]; fileHeader.add(peemDiodeList);  # @UndefinedVariable
peemExitSlitList = [s4y, s4ygap]; fileHeader.add(peemExitSlitList);  # @UndefinedVariable
peemList = [psx, psy]; fileHeader.add(peemList);  # @UndefinedVariable
#Group the hexapod legs into list
m1legs = [m1leg1, m1leg2, m1leg3, m1leg4, m1leg5, m1leg6];  # @UndefinedVariable
m6legs = [m6leg1, m6leg2, m6leg3, m6leg4, m6leg5, m6leg6];  # @UndefinedVariable
m3legs = [m3leg1, m3leg2, m3leg3, m3leg4, m3leg5, m3leg6];  # @UndefinedVariable

from BeamlineI06.KBMirrors import m4bend1g,m4bend2g,m5bend1g,m5bend2g,kbpiezoh,kbpiezov,kbraster,vertFactor,horizFactor,kbpreview,kbimaging,kboff,kbfov  # @UnusedImport
 
if gdaObjectFactoryName == 'I06':
	print
	print "===================================================================";
	print "This is DLS Beamline I06 PEEM Line"
	execfile(gdaScriptDir + "localStation_i06.py");
	#Performing user specific initialisation code"
	print
	print "-------------------------------------------------------------------"
	print "Performing user specific initialisation code for PEEM Line (MainLineUser.py)"
	try:
		execfile(userScriptDir + "MainLineUser.py");
	except:
		exceptionType, exception, traceback=sys.exc_info();
		print "XXXXXXXXXX:  MainLineUser.py Error"
		logger.dump("---> ", exceptionType, exception, traceback)

else:
	print "Wrong Beamline Name"

print "==================================================================="; print; print;

print "Creating i06ccd2 detector (from end of localStation.py)"
#import scannables.detector.andormcd
#i06ccd2 = scannables.detector.andormcd.AndorMCD('i06ccd2')


