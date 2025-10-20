#localStation.py - For beamline specific initialisation code.
from utils.ExceptionLogs import localStation_exception
from gda.factory import Finder
from uk.ac.diamond.daq.configuration import ConfigUtils
from gda.device.temperature import DummyTemp

print("="*100)
print("Performing Beamline I06-1 specific initialisation code (localStation.py).")

print("-"*100)
print("Set scan returns to the start positions on completion")
print("   To set scan returns to its start positions on completion please do:")
print("      >>>scansReturnToOriginalPositions=1")
scansReturnToOriginalPositions=0;

from i06shared.localStation import *  # @UnusedWildImport
if installation.isDummy():
    pgm_controller = Finder.find("pgmController")
    pgm_controller.setPosition("BRANCHLINE")

#End Station Section
import sys

from Beamline.U2Scaler8513 import ca61sr,ca62sr,ca63sr,ca64sr,ca65sr,ca66sr,ca67sr,ca68sr,scaler2  # @UnusedImport
if installation.isLive():
    from laserCabin.TOPASScaler8512 import ca81sr,ca82sr,ca83sr,ca84sr,ca85sr,ca86sr,ca87sr,ca88sr,topas_scaler  # @UnusedImport
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

# amplifer gain splitter objects used by metadata
from metadata.amplifierGainPaser import AmplifierGainParser
if ConfigUtils.profileActive("magnet"):
    LocalProperties.set(LocalProperties.GDA_END_STATION_NAME, "magnet")
    from beam.magnetvalve import closebeam, openbeam  # @UnusedImport
    scm_amp_1 = AmplifierGainParser("scm_amp_1", "BL06I-DI-IAMP-20:SCM:GAIN")
    if installation.isLive():
        # from magnet.useMagnet import scmc,magmode,magcartesian,magspherical,magx,magy,magz,magrho,magth,magphi,magdelay,magtolerance,hyst2,dhyst,logValues,negLogValues,negPosLogValues,cw,cwAsymptote # @UnusedImport
        try:
            execfile('/dls_sw/i06-1/software/gda/config/scripts/magnet/useMagnet.py');
        except:
            exceptionType, exception, traceback = sys.exc_info();
            print("Error:  execfile /magnet/useMagnet.py")
            logger.dump("---> ", exceptionType, exception, traceback)
        #run('/dls_sw/i06-1/software/gda/config/scripts/magnet/useMagnet.py') # 27/9/2017 James M Temp fix as import above fails
        # from scan.fastFieldScan import magnetflyscannable, fastfieldscan  # @UnusedImport
        from scan.fastFieldScanWithEnergySwitch import fastfieldscan, magnetflyscannable  # @UnusedImport
    #sample temperature
    tsample = magnetSampleTemp  # @UndefinedVariable

if ConfigUtils.profileActive("DD"):
    LocalProperties.set(LocalProperties.GDA_END_STATION_NAME, "DD")
    from beam.DDvalve import closebeam, openbeam  # @UnusedImport @Reimport
    ddiff_amp_1 = AmplifierGainParser("ddiff_amp_1", "BL06I-DI-IAMP-30:DDIFF:GAIN")
    print("*"*100)
    print("import DIFFCALC support for I06-1")
    try:
        from startup.i06 import *  # @UnusedWildImport
    except:
        localStation_exception(sys.exc_info(), "import diffcalc error.")
    #sample temperature
    from gdascripts.scannable.temperature.sample_temperature import SampleTemperature
    tsample = SampleTemperature("tsample", ls336, channel_number = 1)  # @UndefinedVariable

if ConfigUtils.profileActive("xabs"):
    LocalProperties.set(LocalProperties.GDA_END_STATION_NAME, "xabs")
    from beam.xabsvalve import closebeam, openbeam  # @UnusedImport @Reimport
    xabs_amp_1 = AmplifierGainParser("xabs_amp_1", "BL06I-DI-IAMP-40:XABS:GAIN")
    #sample temperature
    tsample = DummyTemp(); tsample.setName("tsample")

from i06shared.scan.installStandardScansWithAdditionalScanListeners import *  # @UnusedWildImport
scan_processor.rootNamespaceDict=globals()  
import gdascripts
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()  # @UndefinedVariable

# NXxas App Def template objects
print("-"*100)
print("load 'xasmode' scannable")
XAS_MODES = ['TEY', 'TFY_ft', 'TFY_fb', 'TFY_90']
TEY, TFY_ft, TFY_fb, TFY_90 = XAS_MODES
xasmode = XASMode("xasmode", XAS_MODES, mode = TEY)
mode_path_fast = {TEY: "/entry/instrument/fesData/C1", TFY_ft: "/entry/instrument/fesData/C3", TFY_fb: "/entry/instrument/fesData/C4", TFY_90: "/entry/instrument/fesData/C5"}
mode_path_slow = {TEY: "/entry/instrument/ca61sr/value", TFY_ft: "/entry/instrument/ca63sr/value", TFY_fb: "/entry/instrument/ca64sr/value", TFY_90: "/entry/instrument/ca65sr/value"}
xasmode_fast = XASModePathMapper("xasmode_fast", xasmode, mode_path_fast)
xasmode_slow = XASModePathMapper("xasmode_slow", xasmode, mode_path_slow)
xasscan.NEXUS_TEMPLATE_YAML_FILE_NAME = "NXxas_template_slowscan.yaml"
xasscan.xasmode_scannable_name = "xasmode"

print("="*100)
print("End of i06-1 localStation.py")



