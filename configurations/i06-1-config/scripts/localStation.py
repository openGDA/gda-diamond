#localStation.py
#For beamline specific initialisation code.
from utils.ExceptionLogs import localStation_exception

print "===================================================================";
print "Performing Beamline I06-1 specific initialisation code (localStation.py).";
print

print "-"*100
print "Set scan returns to the start positions on completion"
print "   To set scan returns to its start positions on completion please do:"
print "      >>>scansReturnToOriginalPositions=1"
scansReturnToOriginalPositions=0;
print

from i06shared.localStation import *  # @UnusedWildImport
#from scan.fastEnergyScan import zacscan,zacstop,zacmode,fesController,fesData, fastEnergy,uuu,beamlineutil  # @UnusedImport

from Beamline.beamline import getTitle,gettitle,getvisit,getVisit,lastscan,setDir,setdir,setTitle,settitle,setVisit,setvisit  # @UnusedImport
from Beamline.createAlias import closebeam, openbeam  # @UnusedImport

#To eLog the scan
from Beamline.beamline import branchline
fileHeader.setScanLogger(branchline);

#End Station Section
import sys

if installation.isLive():
    from Beamline.U2Scaler8513 import ca61sr,ca62sr,ca63sr,ca64sr,ca65sr,ca66sr,ca67sr,ca68sr,scaler2  # @UnusedImport
    from laserCabin.TOPASScaler8512 import ca81sr,ca82sr,ca83sr,ca84sr,ca85sr,ca86sr,ca87sr,ca88sr,topas_scaler  # @UnusedImport
    ##Magnet
    #from magnet.useMagnet import scm,magmode,magcartesian,magspherical,magx,magy,magz,magrho,magth,magphi,magdelay,magtolerance,hyst2,dhyst,logValues,negLogValues,negPosLogValues,cw,cwAsymptote # @UnusedImport
    try:
        execfile('/dls_sw/i06-1/software/gda/config/scripts/magnet/useMagnet.py');
    except:
        exceptionType, exception, traceback=sys.exc_info();
        print "Error:  execfile /magnet/useMagnet.py"
        logger.dump("---> ", exceptionType, exception, traceback)
    #run('/dls_sw/i06-1/software/gda/config/scripts/magnet/useMagnet.py') # 27/9/2017 James M Temp fix as import above fails
    from functionDevices.idivio import idio,ifio,ifioft,ifiofb,testFun  # @UnusedImport
    from Beamline.waveplate3 import wp32  # @UnusedImport
##Pixis - there is a java object replement
#from cameras.usePixis import pixis
##Exit Slit
from slits.useS6 import news6xgap, news6ygap  # @UnusedImport
#Group the hexapod legs into list
m7legs = [m7leg1, m7leg2, m7leg3, m7leg4, m7leg5, m7leg6];  # @UndefinedVariable
#To add branchline device position to the SRS file header
fileHeader.add([m7x, m7pitch, m7qg]);  # @UndefinedVariable
fileHeader.add([d9y, d10y, d11y]);  # @UndefinedVariable
fileHeader.add([s6x, s6xgap, s6y, s6ygap]);  # @UndefinedVariable

print "-"*100
print "Set up d12 position objects"
def d12Out():
    d12posn.moveTo("Out")  # @UndefinedVariable
    print "Move completed"
def d12Ti():
    d12posn.moveTo("Ti")  # @UndefinedVariable
    print "Move completed"
def d12Co():
    d12posn.moveTo("Co")  # @UndefinedVariable
    print "Move completed"
def d12Fe():
    d12posn.moveTo("Fe")  # @UndefinedVariable
    print "Move completed"
def d12Ni():
    d12posn.moveTo("Ni")  # @UndefinedVariable
    print "Move completed"
def d12Gd():
    print "Move completed"
    d12posn.moveTo("Gd")  # @UndefinedVariable

from gda.jython.commands.GeneralCommands import alias
alias("d12Out")
alias("d12Ti")
alias("d12Co")
alias("d12Fe")
alias("d12Ni")
alias("d12Gd")

fileHeader.add([iamp12_gain])  # @UndefinedVariable
from gda.jython.commands.ScannableCommands import add_default
add_default([fileHeader]);


print "Switch off scan processor by default at Sarnjeet's request on 11 May 2016 in I06-1."    
print " To manually switch on scan processor, run 'scan_processing_on()' function on Jython Terminal."
print " To manually switch off scan processor, run 'scan_processing_off()' function on Jython Terminal."

from gdascripts.scan.installStandardScansWithProcessing import * # @UnusedWildImport
scan_processor.rootNamespaceDict=globals()  
import gdascripts
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()  # @UndefinedVariable
scan_processor_normal_processes = scan_processor.processors
scan_processor_empty_processes  = []
 
def scan_processing_on():
    scan_processor.processors = scan_processor_normal_processes
 
def scan_processing_off():
    scan_processor.processors = scan_processor_empty_processes
    
print
print "*"*80
#DiffCalc
print "import DIFFCALC support for I06-1"
try:
    from startup.i06 import *  # @UnusedWildImport
except:
    localStation_exception(sys.exc_info(), "import diffcalc error.")
        
print "===================================================================";
print " End of i06-1 localStation.py"



