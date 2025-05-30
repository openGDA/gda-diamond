from utils.ExceptionLogs import localStation_exceptions, localStation_exception
from gdascripts.messages.handle_messages import simpleLog
import sys
from org.slf4j import LoggerFactory
from gda.configuration.properties import LocalProperties

print("*"*80)
print("Running the I10 startup script localStation.py...")
print("\n")
logger = LoggerFactory.getLogger(__name__)

print("-"*100)
print("Set scan returns to the original positions on completion to false (0); default is 0.")
print("   To set scan returns to its start positions on completion please do:")
print("      >>>scansReturnToOriginalPositions=1")
scansReturnToOriginalPositions = 0;

from i10shared.localStation import *  # @UnusedWildImport

from scannable.continuous.continuous_energy_scannables_scattering import energy, mcs16, mcs17, mcs18, mcs19, mcs20, mcs21, mcs22, mcs23  # @UnusedImport

LocalProperties.set(LocalProperties.GDA_END_STATION_NAME, "RASOR")

# ##Save and reload positions of a given scannable group and/or a list of scannables
from rasor.saveAndReload import SaveAndReload  # @UnusedImport
print(SaveAndReload.__doc__)
# RASOR Multi-layer support
from rasor.scannable.polarisation_analyser_example import ml, mss, pa  # @UnusedImport
from scannable.haxpod.m4_haxpod_motors import m4fpitch  # @UnusedImport
from scannable.rasor.theta2theta_offsets import tth_off, th_off, chi_off  # @UnusedImport
from amplifiers.femto_instances import rca1, rca2, rca3  # @UnusedImport
if installation.isLive():
    from scannable.haxpod.m4_haxpod_motors import m4_x, m4_y, m4_z, m4_yaw, m4_pitch, m4_roll, M4  # @UnusedImport

from rasor.scannable.ThArea import thArea  # @UnusedImport
from rasor.scannable.TthArea import tthArea  # @UnusedImport
print("\n")
print("*"*80)
# DiffCalc
if installation.isDummy():
    # install UB matrix data files in dummy mode when first time run GDA server after checkout GDA source codes from repositories!
    from gda.configuration.properties import LocalProperties
    import os
    to_directory = LocalProperties.get(LocalProperties.GDA_VAR_DIR) + os.sep + "diffcalc"
    if not os.path.exists(to_directory):
        # install UB data
        from distutils.dir_util import copy_tree
        from_directory = LocalProperties.get(LocalProperties.GDA_CONFIG) + os.sep + "diffcalc"
        logger.info("Install 'diffcalc' directory and UB matrix data files in {}", to_directory)
        copy_tree(from_directory, to_directory)

print("import DIFFCALC support for I10")
try:
    from startup.i10 import *  # @UnusedWildImport
except Exception as e:
    localStation_exception(sys.exc_info(), "import diffcalc error")

# #Position Wrapper
print("-"*100)
print("Creating 'wa' command for returning RASOR motor positions")
wascannables = [tth, th, chi, dsu, dsd, eta, ttp, thp, py, pz, alpha_rasor, difx, lgf, lgb, lgm, sx, sy, sz]  # @UndefinedVariable
from rasor.positionWrapper import PositionWrapper
try:
    wa = PositionWrapper(wascannables)
except Exception as e:
    localStation_exception(sys.exc_info(), "create wa error")

alias('wa')

print("Creating 'wh' command for return RASOR positions in DIFFCALC HKL")
wherescannables = [tth, th, chi, phi, h, k, l, en]  # @UndefinedVariable
try:
    wh = PositionWrapper(wherescannables)  # #can only be used with diffcalc
except Exception as e:
    localStation_exception(sys.exc_info(), "create wh error")

alias('wh')

from scannable.rocking.detectorWithRockingMotion import NXDetectorWithRockingMotion  # @UnusedImport
from gdaserver import pimte, pixis  # @UnresolvedImport

thpimte = NXDetectorWithRockingMotion("thpimte", th, pimte)  # @UndefinedVariable
thpixis = NXDetectorWithRockingMotion("thpixis", th, pixis)  # @UndefinedVariable

import gdascripts
scan_processor.rootNamespaceDict = globals()
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()

from scannable.checkgatevalvescannables import checkgv12  # @UnusedImport

# NXxas App Def template objects
XAS_MODES = ['TEY', 'TFY', 'PFY']
TEY, TFY, PFY = XAS_MODES
xasmode_fast = XASMode("xasmode_fast", XAS_MODES[:-1], mode = TEY)
mode_path_fast = {TEY: "/entry/instrument/mcs17/data", TFY: "/entry/instrument/mcs18/data"}
xasmode_path_fast = XASModePathMapper("xasmode_path_fast", xasmode_fast, mode_path_fast)
xasmode_slow = XASMode("xasmode_slow", XAS_MODES, mode = TEY)
mode_path_slow = {TEY: "/entry/instrument/macr17/data", TFY: "/entry/instrument/macr18/data", PFY: "/entry/instrument/xmapMca/fullSpectrum"}
xasmode_path_slow = XASModePathMapper("xasmode_path_slow", xasmode_slow, mode_path_slow)
xasscan.NEXUS_TEMPLATE_YAML_FILE_NAME = "NXxas_template_slowscan.yaml"
xasscan.xasmode_scannable_name = "xasmode_slow"

from scannable.rasor.attocube350 import rasorphi  # @UnusedImport

if len(localStation_exceptions) > 0:
    simpleLog("=============== %r ERRORS DURING STARTUP ================" % len(localStation_exceptions))

for localStationException in localStation_exceptions:
    simpleLog(localStationException)

print("**************************************************")
print("localStation.py completed.")
print("**************************************************")
