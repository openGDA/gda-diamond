# localStation.py
# For beamline specific initialisation code.
#
import sys
from gda.configuration.properties import LocalProperties
from uk.ac.diamond.daq.configuration import ConfigUtils
from utils.ExceptionLogs import localStation_exceptions, localStation_exception
from gdascripts.messages.handle_messages import simpleLog

print("=================================================================================================================")
print("Performing beamline specific initialisation code (b07-1).")
print("=================================================================================================================")
print

print("Load EPICS pseudo device utilities for creating scannable object from a PV name.")
from gdascripts.pd.epics_pds import *  # @UnusedWildImport

print("Load time utilities.")
from gdascripts.pd.time_pds import *  # @UnusedWildImport
# Make time scannable
# Example: scan timeScannable 0 3600 30 analyser - Make a scan starting now, for 1 hour, recording the analyser every 30 secs
from gdascripts.scannable.timerelated import TimeSinceScanStart, clock, epoch  # @UnusedImport
timeScannable = TimeSinceScanStart('timeScannable')

print("Load utilities: caget(pv), caput(pv,value), attributes(object), iterableprint(iterable), listprint(list), frange(start,end,step)")
from gdascripts.utils import *  # @UnusedWildImport

print("Installing standard scans with processing")
from gdascripts.scan.installStandardScansWithProcessing import *  # @UnusedWildImport
scan_processor.rootNamespaceDict = globals()

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

# check beam scannables
from scannables.checkbeanscannables import checkbeam, checkfe, checkrc, checktopup_time  # @UnusedImport

print("-"*100)
print("setup meta-data provider commands: meta_add, meta_ll, meta_ls, meta_rm ")
from metadata.metashop import meta_add, meta_ll, meta_ls, meta_rm  # @UnusedImport
import metadata.metashop as metashop  # @UnusedImport

print("-"*100)
import installation
meta_data_list = []  # other common metadata can be added here if required!
if installation.isLive():
		meta_data_list = meta_data_list + [rga]  # @UndefinedVariable
		if ConfigUtils.profileActive("TPOT"):
				print("add TPOT scannables to metadata list ...")
				try:
						meta_data_list = meta_data_list + [sm_xp, sm_yp, sm_zp, sm_polar_rotation, sm_azimuth_rotation]  # @UndefinedVariable
				except Exception as e:
						print("adding TPOT to metadata failed.")
						localStation_exception(sys.exc_info(), "adding TPOT to metadata error")
		if ConfigUtils.profileActive("TCUP"):
				print("add TCUP metadata scannables to be captured in data files.")
				try:
						meta_data_list = meta_data_list + [sm2_xp, sm2_yp, sm2_zp]  # @UndefinedVariable
				except Exception as e:
						print("adding TCUP to metadata failed.")
						localStation_exception(sys.exc_info(), "adding TCUP to metadata error")
else:
		if ConfigUtils.profileActive("TPOT"):
				print("add TPOT metadata scannables to be captured in data files.")
				meta_data_list = meta_data_list + [sm_xp, sm_yp, sm_zp, sm_polar_rotation, sm_azimuth_rotation]  # @UndefinedVariable
		if ConfigUtils.profileActive("TCUP"):
				print("add TCUP metadata scannables to be captured in data files.")
				meta_data_list = meta_data_list + [sm2_xp, sm2_yp, sm2_zp]  # @UndefinedVariable

patch_panel_list = [ppc_temp_1, ppc_temp_2, ppc_temp_3, ppc_temp_4, ppc_ai_1, ppc_ai_2, ppc_ai_3, ppc_ai_4, ppc_ao_1, ppc_ao_2, ppc_ao_3, ppc_ao_4, ppc_di_1, ppc_di_2, ppc_di_3, ppc_di_4, ppc_do_5, ppc_do_6, ppc_do_7, ppc_do_8]  # @UndefinedVariable
crystal_monochromator_list = [ccmc_x, ccmc_y, ccmc_z]  # @UndefinedVariable
diagnosis_list = [d9c_y_positioner, d9c_y]  # @UndefinedVariable
meta_data_list = meta_data_list + patch_panel_list + crystal_monochromator_list + diagnosis_list

for each in meta_data_list:
		meta_add(each)

print("-"*100)
from scannables.pgm_energy_multilayer_grating import pgm_energy_mlg
help(pgm_energy_mlg)
print("-"*100)
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

