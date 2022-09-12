# localStation.py
# For beamline specific initialisation code.
#
import java
from gda.configuration.properties import LocalProperties
import sys
from utils.ExceptionLogs import localStation_exceptions, localStation_exception
from gdascripts.messages.handle_messages import simpleLog

print("=================================================================================================================")
print("Performing beamline specific initialisation code (b07-1).")
print("=================================================================================================================")
print

print("Load EPICS pseudo device utilities for creating scannable object from a PV name.")
from gdascripts.pd.epics_pds import * #@UnusedWildImport

print("Load time utilities.")
from gdascripts.pd.time_pds import * #@UnusedWildImport
# Make time scannable 
# Example: scan timeScannable 0 3600 30 analyser - Make a scan starting now, for 1 hour, recording the analyser every 30 secs
from gdascripts.scannable.timerelated import TimeSinceScanStart
timeScannable = TimeSinceScanStart('timeScannable')

print("Load utilities: caget(pv), caput(pv,value), attributes(object), iterableprint(iterable), listprint(list), frange(start,end,step)")
from gdascripts.utils import * #@UnusedWildImport

print("Installing standard scans with processing")
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()

print("Installing regional scan")
from gdascripts.scan.RegionalScan import RegionalScanClass
mrscan = RegionalScanClass()
alias('mrscan')

print("Installing configure_analyser_fixed_transmission")
from beamline.configure_analyser_fixed_transmission import configure_analyser_fixed_transmission

print("Installing EPICS archiver client")
from gdascripts.archiver.archiver import archive
alias('archive')
from gdaserver import archiver  # @UnresolvedImport @UnusedImport

from scannables.rga21 import rga21, rga21AR, rga21CF3, rga21CH2, rga21CH3, rga21CH4, rga21CO, rga21CO2, rga21H2, rga21H2O, rga21HE, rga21O2, rga21sumofpeaks, rga21tot  # @UnusedImport
from scannables.rga24 import rga24, rga24AR, rga24CF3, rga24CH2, rga24CH3, rga24CH4, rga24CO, rga24CO2, rga24H2, rga24H2O, rga24HE, rga24O2, rga24sumofpeaks, rga24tot  # @UnusedImport

from scannables.PLV1000 import plv1, plv2  # @UnusedImport

print("-"*100)
print("setup meta-data provider commands: meta_add, meta_ll, meta_ls, meta_rm ")
from metadata.metashop import meta_add,meta_ll,meta_ls, meta_rm  # @UnusedImport
import metadata.metashop as metashop  # @UnusedImport

print("-"*100)
import installation
meta_data_list = [] #other common metadata can be added here if required!
if installation.isLive():
    meta_data_list = meta_data_list +[rga]  # @UndefinedVariable
    end_station_configuration = int(caget("BL07C-EA-ENDST-01:CFG:HW_RBV"))
    if end_station_configuration == 1: #TPOT
        print("add TPOT scannables to metadata list ...")
        try:
            meta_data_list = meta_data_list + [sm_xp, sm_yp, sm_zp, sm_polar_rotation, sm_azimuth_rotation] #@UndefinedVariable
        except Exception as e:
            print("adding TPOT to metadata failed.")
            localStation_exception(sys.exc_info(), "adding TPOT to metadata error")
    if end_station_configuration == 2: #TCUP
        print("add TCUP metadata scannables to be captured in data files.")
        try:
            meta_data_list = meta_data_list + [sm2_xp, sm2_yp, sm2_zp, sm2_xpc, sm2_ypc, sm2_zpc] #@UndefinedVariable
        except Exception as e:
            print("adding TCUP to metadata failed.")
            localStation_exception(sys.exc_info(), "adding TCUP to metadata error")
else:
    from java.lang import System  # @UnresolvedImport
    spring_profiles = System.getProperty("gda.spring.profiles.active")
    if "TPOT" in spring_profiles:
        print("add TPOT metadata scannables to be captured in data files.")
        meta_data_list = meta_data_list + [sm_xp, sm_yp, sm_zp, sm_polar_rotation, sm_azimuth_rotation] #@UndefinedVariable
    if "TCUP" in spring_profiles:
        print("add TCUP metadata scannables to be captured in data files.")
        meta_data_list = meta_data_list + [sm2_xp, sm2_yp, sm2_zp, sm2_xpc, sm2_ypc, sm2_zpc] #@UndefinedVariable

patch_panel_list = [ppc_temp_1,ppc_temp_2,ppc_temp_3,ppc_temp_4,ppc_ai_1,ppc_ai_2,ppc_ai_3,ppc_ai_4,ppc_ao_1,ppc_ao_2,ppc_ao_3,ppc_ao_4,ppc_di_1,ppc_di_2,ppc_di_3,ppc_di_4,ppc_do_5,ppc_do_6,ppc_do_7,ppc_do_8]  # @UndefinedVariable
meta_data_list = meta_data_list + patch_panel_list

for each in meta_data_list:
    meta_add(each)

# Add a string to hold extra detectors it will be appended to analyser scans run from the GUI
# See uk.ac.diamond.daq.devices.specs.phoibos.ui.handlers.RunSequenceHandler
extraDetectors = ""

print("-"*100)
print("To create a PVScannable from a PV:")
print("   >>> my_scannable = PVScannable('my_scannable', 'PV_name')")
print("   >>> my_scannable.configure()")
from gda.device.scannable import PVScannable  # @UnusedImport

print("-"*100)

if len(localStation_exceptions) > 0:
    simpleLog("=============== %r ERRORS DURING STARTUP ================" % len(localStation_exceptions))

for localStationException in localStation_exceptions:
    simpleLog(localStationException)

print("**************************************************")
print("localStation.py completed.")
print("**************************************************")

