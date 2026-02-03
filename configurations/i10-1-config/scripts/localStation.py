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

from uk.ac.diamond.osgi.services import ServiceProvider # @UnresolvedImport
from uk.ac.diamond.daq.configuration import BeamlineConfiguration
spring_profiles = ServiceProvider.getService(BeamlineConfiguration).profiles.toList()

from scannable.haxpod.m6_haxpod_motors import m6fpitch  # @UnusedImport
from amplifiers.femto_instances import ca1je, ca2je, ca3je  # @UnusedImport
if installation.isLive():
    from scannable.haxpod.m6_haxpod_motors import m6_x, m6_y, m6_z, m6_yaw, m6_pitch, m6_roll, M6  # @UnusedImport

from gdascripts.scannable.temperature.sample_temperature import SampleTemperature
if "hfm" in spring_profiles:
    LocalProperties.set(LocalProperties.GDA_END_STATION_NAME, "HFM")
    # High Field Magnet support
    from high_field_magnet.scannable.intelligent_power_supply_instances import ips_field, ips_sweeprate, itc2, itc3, hfmpitch_off, hfmfield, hfmsweeprate  # @UnusedImport
    from scannable.continuous.continuous_energy_scannables_hfm import energy, mcsh16, mcsh17, mcsh18, mcsh19, mcsh20, mcsh21, mcsh22, mcsh23  # @UnusedImport
    if installation.isLive():
        try:
            from Diamond.PseudoDevices.EpicsDevices import EpicsDeviceClass
            gflow2 = EpicsDeviceClass(name = 'gflow2', pvSet = "BL10J-EA-TCTRL-02:GFLOW:SET", pvGet = "BL10J-EA-TCTRL-02:GFLOW", pvStatus = None, strUnit = "", strFormat = "%.2f", timeout = None)
        except Exception as e:
            localStation_exception(sys.exc_info(), "creating gflow2 scannable error")
    print("create 'xasmode_fast' for using in cvscan, and 'xasmode_slow' for using in xasscan in HFM end station")
    # NXxas App Def template objects
    XAS_MODES = ['TEY', 'TFY_front', 'TFY_side', 'PFY'] # this is different from i06.
    TEY, TFY_front, TFY_side, PFY = XAS_MODES
    xasmode_fast = XASMode("xasmode_fast", XAS_MODES[:-1], mode = TEY)
    mode_path_fast = {TEY: "/entry/instrument/mcsh17/data", TFY_front: "/entry/instrument/mcsh18/data", TFY_side: "/entry/instrument/mcsh19/data"}
    xasmode_path_fast = XASModePathMapper("xasmode_path_fast", xasmode_fast, mode_path_fast)
    xasmode_slow = XASMode("xasmode_slow", XAS_MODES, mode = TEY)
    mode_path_slow = {TEY: "/entry/instrument/macj217/data", TFY_front: "/entry/instrument/macj218/data", TFY_side: "/entry/instrument/macj219/data", PFY: "/entry/instrument/xmapMca/fullSpectrum"}
    xasmode_path_slow = XASModePathMapper("xasmode_path_slow", xasmode_slow, mode_path_slow)
    xasscan.NEXUS_TEMPLATE_YAML_FILE_NAME = "NXxas_template_hfm_slowscan.yaml"
    xasscan.xasmode_scannable_name = "xasmode_slow"
    from scans.fastFieldScan import fastfieldscan, magnetflyscannable, magnet_field_show_demand_value, set_magnet_field_ramp_rate_factor  # @UnusedImport
    tsample = SampleTemperature("tsample", itc3, channel_number = 1)  # @UndefinedVariable
    from gdaserver import ips_field_wrapper, itc3_wrapper  # @UnresolvedImport
    ips_field_wrapper.connectScannable()
    itc3_wrapper.connectScannable()
    
if "em" in spring_profiles:
    LocalProperties.set(LocalProperties.GDA_END_STATION_NAME, "EM")
    from scannable.positions.magnet_instances import magnetCurrent, magnetField  # @UnusedImport
    from scannable.continuous.continuous_energy_scannables_em import energy, mcse16, mcse17, mcse18, mcse19, mcse20, mcse21, mcse22, mcse23  # @UnusedImport
    print("create 'xasmode_fast' for using in cvscan, and 'xasmode_slow' for using in xasscan in EM end station")
    # NXxas App Def template objects
    XAS_MODES = ['TEY', 'TFY', 'PFY'] # this is different from i06.
    TEY, TFY, PFY = XAS_MODES
    xasmode_fast = XASMode("xasmode_fast", XAS_MODES[:-1], mode = TEY)
    mode_path_fast = {TEY: "/entry/instrument/mcse17/data", TFY: "/entry/instrument/mcse18/data"}
    xasmode_path_fast = XASModePathMapper("xasmode_path_fast", xasmode_fast, mode_path_fast)
    xasmode_slow = XASMode("xasmode_slow", XAS_MODES, mode = TEY)
    mode_path_slow = {TEY: "/entry/instrument/macj317/data", TFY: "/entry/instrument/macj318/data", PFY: "/entry/instrument/xmapMca/fullSpectrum"}
    xasmode_path_slow = XASModePathMapper("xasmode_path_slow", xasmode_slow, mode_path_slow)
    xasscan.NEXUS_TEMPLATE_YAML_FILE_NAME = "NXxas_template_em_slowscan.yaml"
    xasscan.xasmode_scannable_name = "xasmode_slow"
    #sample temperature
    tsample = SampleTemperature("tsample", ls336, channel_number = 1)  # @UndefinedVariable

#--new default processor DP 20/01/26
from gda.device.scannable import ProcessingScannable
from gda.jython.commands.ScannableCommands import add_default
nexus_processor = ProcessingScannable('nexus_processor')
nexus_processor['mmg-nexus'] = [{}]
add_default(nexus_processor)

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
