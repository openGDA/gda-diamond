#localStation.py - For beamline specific initialisation code.
from utils.ExceptionLogs import localStation_exception

print("===================================================================")
print("Performing Beamline I06-1 specific initialisation code (localStation.py).")

print("-"*100)
print("Set scan returns to the start positions on completion")
print("   To set scan returns to its start positions on completion please do:")
print("      >>>scansReturnToOriginalPositions=1")
scansReturnToOriginalPositions=0;

from i06shared.localStation import *  # @UnusedWildImport

from Beamline.beamline import getTitle,gettitle,getvisit,getVisit,lastscan,setDir,setdir,setTitle,settitle,setVisit,setvisit  # @UnusedImport
from Beamline.createAlias import closebeam, openbeam  # @UnusedImport

#To eLog the scan
from Beamline.beamline import branchline
fileHeader.setScanLogger(branchline);

#End Station Section
import sys

from Beamline.U2Scaler8513 import ca61sr,ca62sr,ca63sr,ca64sr,ca65sr,ca66sr,ca67sr,ca68sr,scaler2  # @UnusedImport
if installation.isLive():
    from laserCabin.TOPASScaler8512 import ca81sr,ca82sr,ca83sr,ca84sr,ca85sr,ca86sr,ca87sr,ca88sr,topas_scaler  # @UnusedImport
    ##Magnet
    #from magnet.useMagnet import scm,magmode,magcartesian,magspherical,magx,magy,magz,magrho,magth,magphi,magdelay,magtolerance,hyst2,dhyst,logValues,negLogValues,negPosLogValues,cw,cwAsymptote # @UnusedImport
    try:
        execfile('/dls_sw/i06-1/software/gda/config/scripts/magnet/useMagnet.py');
    except:
        exceptionType, exception, traceback = sys.exc_info();
        print("Error:  execfile /magnet/useMagnet.py")
        logger.dump("---> ", exceptionType, exception, traceback)
    #run('/dls_sw/i06-1/software/gda/config/scripts/magnet/useMagnet.py') # 27/9/2017 James M Temp fix as import above fails
    from functionDevices.idivio import idio,ifio,ifioft,ifiofb,testFun  # @UnusedImport
    from Beamline.waveplate3 import wp32  # @UnusedImport

##Exit Slit
from slits.useS6 import news6xgap, news6ygap  # @UnusedImport
#Group the hexapod legs into list
m7legs = [m7leg1, m7leg2, m7leg3, m7leg4, m7leg5, m7leg6];  # @UndefinedVariable

MOVE_COMPLETED = "Move completed"
print("-"*100)
print("Set up d12 position commands - d12Out, d12Ti, d12Co, d12Fe, d12Ni, d12Gd")
def d12Out():
    d12posn.moveTo("Out")  # @UndefinedVariable
    print(MOVE_COMPLETED)
def d12Ti():
    d12posn.moveTo("Ti")  # @UndefinedVariable
    print(MOVE_COMPLETED)
def d12Co():
    d12posn.moveTo("Co")  # @UndefinedVariable
    print(MOVE_COMPLETED)
def d12Fe():
    d12posn.moveTo("Fe")  # @UndefinedVariable
    print(MOVE_COMPLETED)
def d12Ni():
    d12posn.moveTo("Ni")  # @UndefinedVariable
    print(MOVE_COMPLETED)
def d12Gd():
    d12posn.moveTo("Gd")  # @UndefinedVariable
    print(MOVE_COMPLETED)

from gda.jython.commands.GeneralCommands import alias
alias("d12Out")
alias("d12Ti")
alias("d12Co")
alias("d12Fe")
alias("d12Ni")
alias("d12Gd")

print("-"*100)
# print("Switch off scan processor by default at Sarnjeet's request on 11 May 2016 in I06-1.")    
print(" To manually switch on scan processor, run 'scan_processing_on()' function on Jython Terminal.")
print(" To manually switch off scan processor, run 'scan_processing_off()' function on Jython Terminal.")

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

# amplifer gain splitter objects used by metadata
from metadata.amplifierGainPaser import AmplifierGainParser
from java.lang import System
profiles = System.getProperty("gda.spring.profiles.active")
if "magnet" in profiles:
    scm_amp_1 = AmplifierGainParser("scm_amp_1", "BL06I-DI-IAMP-20:SCM:GAIN")
    scm_amp_2 = AmplifierGainParser("scm_amp_2", "BL06I-DI-IAMP-21:SCM:GAIN")
    scm_amp_3 = AmplifierGainParser("scm_amp_3", "BL06I-DI-IAMP-22:SCM:GAIN")
    scm_amp_4 = AmplifierGainParser("scm_amp_4", "BL06I-DI-IAMP-23:SCM:GAIN")

if "DD" in profiles:
    ddiff_amp_1 = AmplifierGainParser("ddiff_amp_1", "BL06I-DI-IAMP-30:DDIFF:GAIN")
    ddiff_amp_2 = AmplifierGainParser("ddiff_amp_2", "BL06I-DI-IAMP-31:DDIFF:GAIN")
    ddiff_amp_3 = AmplifierGainParser("ddiff_amp_3", "BL06I-DI-IAMP-32:DDIFF:GAIN")
    ddiff_amp_4 = AmplifierGainParser("ddiff_amp_4", "BL06I-DI-IAMP-33:DDIFF:GAIN")
    print("*"*80)
    print("import DIFFCALC support for I06-1")
    try:
        from startup.i06 import *  # @UnusedWildImport
    except:
        localStation_exception(sys.exc_info(), "import diffcalc error.")

if "xabs" in profiles:
    xabs_amp_1 = AmplifierGainParser("xabs_amp_1", "BL06I-DI-IAMP-40:XABS:GAIN")
    xabs_amp_2 = AmplifierGainParser("xabs_amp_2", "BL06I-DI-IAMP-41:XABS:GAIN")
    
        
print("===================================================================")
print(" End of i06-1 localStation.py")



