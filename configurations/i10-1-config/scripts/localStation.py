from utils.ExceptionLogs import localStation_exceptions, localStation_exception
from gdascripts.messages.handle_messages import simpleLog
import sys
from org.slf4j import LoggerFactory

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

from uk.ac.diamond.osgi.services import ServiceProvider # @UnresolvedImport
from uk.ac.diamond.daq.configuration import BeamlineConfiguration
spring_profiles = ServiceProvider.getService(BeamlineConfiguration).profiles.toList()

from scannable.haxpod.m6_haxpod_motors import m6fpitch  # @UnusedImport
from amplifiers.femto_instances import ca1je, ca2je, ca3je  # @UnusedImport
if installation.isLive():
    from scannable.haxpod.m6_haxpod_motors import m6_x, m6_y, m6_z, m6_yaw, m6_pitch, m6_roll, M6  # @UnusedImport

if "hfm" in spring_profiles:
    # High Field Magnet support
    from high_field_magnet.scannable.intelligent_power_supply_instances import ips_field, ips_sweeprate, itc2, itc3, hfmpitch_off  # @UnusedImport
    from scannable.continuous.continuous_energy_scannables_hfm import energy, mcsh16, mcsh17, mcsh18, mcsh19, mcsh20, mcsh21, mcsh22, mcsh23  # @UnusedImport
    if installation.isLive():
        try:
            from Diamond.PseudoDevices.EpicsDevices import EpicsDeviceClass
            gflow2 = EpicsDeviceClass(name = 'gflow2', pvSet = "BL10J-EA-TCTRL-02:GFLOW:SET", pvGet = "BL10J-EA-TCTRL-02:GFLOW", pvStatus = None, strUnit = "", strFormat = "%.2f", timeout = None)
        except Exception as e:
            localStation_exception(sys.exc_info(), "creating gflow2 scannable error")
    # NXxas App Def template objects
    xasmode = XASMode("xasmode", XAS_MODES, mode = TEY)
    mode_path_fast = {TEY: "/entry/instrument/mcsh17/data", PEY: "NA", TFY: "NA", PFY: "NA", TFY_front: "/entry/instrument/mcsh18/data", TFY_side: "/entry/instrument/mcsh19/data"}
    mode_path_slow = {TEY: "/entry/instrument/macj217/data", PEY: "NA", TFY: "NA", PFY: "/entry/instrument/xmapMca/fullSpectrum", TFY_front: "/entry/instrument/macj218/data", TFY_side: "/entry/instrument/macj219/data"}
    xasmode_fast = XASModePathMapper("xasmode_fast", xasmode, mode_path_fast)
    xasmode_slow = XASModePathMapper("xasmode_slow", xasmode, mode_path_slow)

if "em" in spring_profiles:
    from scannable.positions.magnet_instances import magnetCurrent, magnetField  # @UnusedImport
    from scannable.continuous.continuous_energy_scannables_em import energy, mcse16, mcse17, mcse18, mcse19, mcse20, mcse21, mcse22, mcse23  # @UnusedImport
    # NXxas App Def template objects
    xasmode = XASMode("xasmode", XAS_MODES, mode = TEY)
    mode_path_fast = {TEY: "/entry/instrument/mcse17/data", PEY: "NA", TFY: "/entry/instrument/mcse18/data", PFY: "NA", TFY_front: "NA", TFY_side: "NA"}
    mode_path_slow = {TEY: "/entry/instrument/macj317/data", PEY: "NA", TFY: "/entry/instrument/macj318/data", PFY: "/entry/instrument/xmapMca/fullSpectrum", TFY_front: "NA", TFY_side: "NA"}
    xasmode_fast = XASModePathMapper("xasmode_fast", xasmode, mode_path_fast)
    xasmode_slow = XASModePathMapper("xasmode_slow", xasmode, mode_path_slow)

import gdascripts
scan_processor.rootNamespaceDict = globals()
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()

if len(localStation_exceptions) > 0:
    simpleLog("=============== %r ERRORS DURING STARTUP ================" % len(localStation_exceptions))

for localStationException in localStation_exceptions:
    simpleLog(localStationException)

print("**************************************************")
print("localStation.py completed.")
print("**************************************************")
