#localStation.py
print "===================================================================";
print " Performing Beamline I07 specific initialisation code (localStation.py).";
print

import sys
from os import system
from time import sleep

from gda.configuration.properties import LocalProperties;
from gdascripts.utils import *  # @UnusedWildImport
import scisoftpy as dnp  # @UnusedImport
from gdaserver import ebe, p2_mask, p3_mask, ex_mask, ei_mask
from gdascripts.installation import isLive, isDummy # @UnusedImport
from scannable.energy_id_gap import energy # @UnusedImport
from gda.jython.commands.ScannableCommands import add_default

userScriptDir = "/dls_sw/" + LocalProperties.get("gda.beamline.name") + "/scripts/";

def disable_nexus():
        LocalProperties.set("gda.data.scan.datawriter.dataFormat", "SrsDataFile")

def enable_nexus():
        LocalProperties.set("gda.data.scan.datawriter.dataFormat", "NexusScanDataWriter")

def try_execfile(filepath, description=None, full_log=False, absolute=False):
    print "-------------------------------------------------------------------"
    if description:
        print description
    print "Running: '%s'" % filepath

    if not absolute:
        filepath = LocalProperties.get("gda.config") + "/scripts/" + filepath

    try:
        execfile(filepath, globals());
    except:
        exceptionType, exception, traceback=sys.exc_info();
        print "************************************************************"
        print "XXXXXXXXXX:  Exception caught while: '%s'" % description
        if full_log:
            logger.fullLog(None, "Error", exceptionType, exception, traceback, True);
            #Note that the final argument 'True' causes a Java exception to be thrown which will terminate the script
        else:
            logger.dump("---> ", exceptionType, exception, traceback)
        print "************************************************************"

try_execfile("BeamlineI07/beamline.py")

try_execfile("BeamlineI07/setTimers.py", "Setup the timers")

try_execfile("BeamlineI07/setSpecialScans.py", "Enable the multiple region scan")

print "-------------------------------------------------------------------"
print "Note: Use dnp (Diamond NumPy) from scisoftpy for data handling and plotting in GDA"
print "Note: Use help dnp for all commands"
print "Note: Use help <component> for help on all components ..."
print "      (dnp.core, dnp.io, dnp.maths, dnp.plot, dnp.image)"
print "For example: "
print "		 To load data:  data=dnp.io.load(/full/path/to/data/file, formats=['srs'], asdict=True)"
print "		 To plot data:  dnp.plot.line(x, y)"
print "		 To plot image: dnp.plot.image(data)"

from BeamlineI07.useMotors import diff1chioffset, diff1homegaoffset, diff1vdeltaoffset, diff1vgammaoffset, diff1vomegaoffset, thv # @UnusedImport
from BeamlineI07.useFourc import fc # @UnusedImport
from BeamlineI07.useTenma import tenma # @UnusedImport
from gdaserver import fastshutter as fs, fastshutter_fatt as ffs, fastshutterScan
add_default(fastshutterScan)
from BeamlineI07.useFastShutter import emergency_stopper, setShutterDelay # @UnusedImport
from BeamlineI07.useNormalisation import ex_norm, p2_norm, p3_norm # @UnusedImport
from BeamlineI07.useFilters import filterset # @UnusedImport

print "==================================================================="
print "Ion Chamber ADC Scaler Support"
print "Use ionsc for the scaler card and ionsc1, ionsc2, ... ionsc8 on channels"
print "==================================================================="
print "Use cyberstar and apdstar  for Cyberstar Scintillation detector and APD-ACE pulse unit respectively"
print "==================================================================="
print "EH1 Struct Scaler Support"
print "Use eh1sc for the scaler card and eh1sc01, eh1sc02, ... eh1sc32 on channels"

try_execfile("BeamlineI07/useDetectors.py", "Start detectors")

# initialise the PDs top set and monitor the bimorph voltages in HFM and VFM
#run("init_bimorph_voltage_setter.py")
#execfile("BeamlineI07/init_bimorph_voltage_setter.py")
try_execfile("BeamlineI07/setBimorphMirror.py", "Start bimorph stuff")

try_execfile("BeamlineI07/diff_mode.py", "Setting diffractometer mode")

try_execfile("BeamlineI07/useDCD.py", "Creating the DCD motors for Liquid Surface Reflectivity Measurement")

try_execfile("BeamlineI07/useHex1.py", "Creating Hexapod1 Pivot Points")

try_execfile("BeamlineI07/useHex2.py", "Creating Hexapod2 Pivot Points")

try_execfile("BeamlineI07/setFastScan.py", "Fast scan setup")

try_execfile("BeamlineI07/createAdditionalMetadataDevices.py", "Metadata Header setup")

try_execfile("BeamlineI07/createAlias.py")

try_execfile("BeamlineI07/useGigECams.py")

from BeamlineI07.useEuroThermo import etoutput11, etoutput12, etoutput13, etoutput21, etoutput22, etoutput23, etoutput3, etoutput4, etoutput5 # @UnusedImport
# Replaces metadata set up in setSrsDataFileHeader.py
try_execfile("BeamlineI07/configureMetadata.py")

#try_execfile(userScriptDir + "MainHutch.py", "Performing user specific initialisation code (MainHutch.py)", absolute=True)
try_execfile("BeamlineI07/Users/MainHutch.py")

from BeamlineI07.Users.ct import ct, ct_detectors # @UnusedImport
from BeamlineI07.useHtc import htc # @UnusedImport
from BeamlineI07.useVirtual6CircleMotors import sgam, sdel # @UnusedImport
from BeamlineI07.useElectroChemValves import openvalve, closevalve  # @UnusedImport
from BeamlineI07.i07_fscan import fscan, fpscan, fhklscan, cfscan # @UnusedImport
from BeamlineI07.i07_mscan import exc, exs, p2c, p2s, p3c, p3s, eic, m3, ex_rois, p2_rois, p3_rois # @UnusedImport
from BeamlineI07.useMalcolm import restart_ei, restart_ex, restart_p2, restart_p3 # @UnusedImport
from det_threshold_setter import exthresh, p2thresh, p3thresh # @UnusedImport

try:
	from gdaserver import d5i
	add_default(d5i)
except:
	print('Could not find d5i to add as a default scannable')

from BeamlineI07.useFastAttenuators import att, autofon, autofoff, setProcessingEnabled, exc_fast_exp_time, list_transmissions, load_transmissions, save_current_transmissions, add_transmissions, remove_transmissions # @UnusedImport
from scannable.pv_with_separate_readback_and_tolerance import PVWithSeparateReadbackAndToleranceScannable
chiller1=PVWithSeparateReadbackAndToleranceScannable('chiller1', pv_set='BL07I-EA-CHIL-01:SET_TEMP', pv_read='BL07I-EA-CHIL-01:TEMP', timeout=30*60, tolerance=0.2)
chiller2=PVWithSeparateReadbackAndToleranceScannable('chiller2', pv_set='BL07I-EA-CHIL-02:SET_SETPOINT', pv_read='BL07I-EA-CHIL-02:TEMPERATURE', timeout=30*60, tolerance=0.2)

from BeamlineI07.gaspanel import (
		GasPanel,
		GasPanelScannable,
		DummyGasPanel,
		gasScanStop
)

_dummygp = DummyGasPanel("_dummygp")
dummygp = GasPanelScannable("dummygp", _dummygp)

#_gp = GasPanel("_gp", "BL07I-EA-GAS-01:")
#gp = GasPanelScannable("gp", _gp)
from BeamlineI07.lakeshore import LakeshoreDoubleReadout, LakeshoreDoubleReadoutDummy # @UnusedImport
#lakeshore = LakeshoreDoubleReadout("lakeshore", lakeshore_base)
dummyLakeshore = LakeshoreDoubleReadoutDummy("dummyLakeshore")

print "==================================================================="
print

from BeamlineI07.hplc import Hplc
hplc = Hplc("BL07I-EA-HPLC-01:")
import diffcalc

# TODO this should probably be part of diffcalc itself
def checkHkl(position):
	try:
		diffcalc.hkl._diffcalc.hkl_to_angles(position[0], position[1], position[2])
	except diffcalc.util.DiffcalcException as err:
		return(str(err))

diffcalc.hkl.checkPositionValid = checkHkl

overwriting.protect("betain", "betaout", "bin_eq_bout")

from BeamlineI07.devices.ivium import ivium, ivium1, iviumPotential, iviumCurrent, iviumRange, iviumMethod # @UnusedImport

if isLive() :
	# add hexapod reset command
	run "reset_symetrie.py"
	# add transmissions command
	run "transmissions.py"

from BeamlineI07.devices.IviumDevice import IviumMethodScannableClass
ivium_method = IviumMethodScannableClass("ivium_method", "BL07I-EA-IVIUM-01", 1, subdir = "processing")

from BeamlineI07.zocalofunctions import currentscan, mapstart, mapend, checkzocalo

# scannables for scientist to set its value at sample position - please update the default value to i07 one if existing.
from beam.beam_properteis import beam_divergence_at_sample, beam_flux_at_sample, beam_size_at_sample  # @UnusedImport

from gdascripts.scannable.virtual_scannable import VirtualScannable
comment = VirtualScannable("comment", initial_value="Not set", value_format="%s")
sample_name = VirtualScannable("sample_name", initial_value="Not set", value_format="%s")

# sample temperature metadata
from gdascripts.scannable.temperature.sample_temperature import SampleTemperature
tsample = SampleTemperature('tsample', lakeshore_base)  # @UndefinedVariable
