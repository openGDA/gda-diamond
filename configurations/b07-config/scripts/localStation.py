# localStation.py
# For beamline specific initialisation code.
#
from gda.configuration.properties import LocalProperties
from gda.device.scannable import DummyScannable
import installation

print "=================================================================================================================";
print "Performing beamline specific initialisation code (b07).";
print "=================================================================================================================";
print

print "Load EPICS pseudo device utilities for creating scannable object from a PV name."
from gdascripts.pd.epics_pds import * #@UnusedWildImport

print "Load time utilities."
from gdascripts.pd.time_pds import * #@UnusedWildImport
# Make time scannable
# Example: scan timeScannable 0 3600 30 analyser - Make a scan starting now, for 1 hour, recording the analyser every 30 secs
from gdascripts.scannable.timerelated import TimeSinceScanStart, clock, epoch  # @UnusedImport
timeScannable = TimeSinceScanStart('timeScannable')

print "Load utilities: caget(pv), caput(pv,value), attributes(object), iterableprint(iterable), listprint(list), frange(start,end,step)"
from gdascripts.utils import * #@UnusedWildImport

print "Installing standard scans with processing"
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()

print "Installing regional scan"
from gdascripts.scan.RegionalScan import RegionalScanClass
mrscan = RegionalScanClass()
alias('mrscan')

# Add a string to hold extra detectors it will be appended to analyser scans run from the GUI
# See uk.ac.diamond.daq.devices.specs.phoibos.ui.handlers.RunSequenceHandler
extraDetectors = ""

if installation.isLive():
    from scannables.detector_output_processing import BekhoffAdcOutputProcessing
    #dummy_quotient = BekhoffAdcOutputProcessing('dummy_quotient', ds1, ds2, 'divide_detector_output')
    ca35b_ca18b_quotient = BekhoffAdcOutputProcessing('ca35b_ca18b_quotient', ca35b, ca18b, 'divide_detector_output')  # @UndefinedVariable
    ca36b_ca18b_quotient = BekhoffAdcOutputProcessing('ca36b_ca18b_quotient', ca36b, ca18b, 'divide_detector_output')  # @UndefinedVariable

#check beam scannables
from scannables.checkbeanscannables import checkbeam, checkfe, checkrc, checktopup_time  # @UnusedImport

print("-"*100)
print("To create a PVScannable from a PV:")
print("   >>> my_scannable = PVScannable('my_scannable', 'PV_name')")
print("   >>> my_scannable.configure()")
from gda.device.scannable import PVScannable  # @UnusedImport

print("-"*100)
print("setup meta-data provider commands: meta_add, meta_ll, meta_ls, meta_rm ")
from metadata.metashop import meta_add,meta_ll,meta_ls, meta_rm  # @UnusedImport
import metadata.metashop  # @UnusedImport
print("Can now add meta data items to be captured in data files.")
meta_data_list = [] #other common metadata can be added here if required!
s1b_list = [s1b_xcentre,s1b_xsize,s1b_ysize,s1b_xpos,s1b_xneg] # @UndefinedVariable
s2b_list = [s2b_xsize,s2b_ysize,s2b_xcentre,s2b_ycentre] # @UndefinedVariable
s3b_list = [s3b_xsize,s3b_ysize,s3b_xcentre,s3b_ycentre] # @UndefinedVariable
s4b_list = [s4b_xgapsize,s4b_ygapsize,s4b_z] # @UndefinedVariable
metadata_group1 = s1b_list + s2b_list + s3b_list + s4b_list
m1b_list = [m1b_x,m1b_y,m1b_pitch,m1b_roll,m1b_yaw,m1b_mask_temp,m1b_mirror_temp,m1b_chiller] # @UndefinedVariable
m1c_list = [m1c_mirror_temp,m1c_mask_temp] # @UndefinedVariable
m3b_list = [m3b_x,m3b_y,m3b_pitch,m3b_roll,m3b_yaw] # @UndefinedVariable
m4b_list = [m4b_x,m4b_y,m4b_pitch,m4b_roll,m4b_yaw,m4b_y_base,m4b_y_base_positioner,m4b_y_combined,m4b_mirror] # @UndefinedVariable
m5b_list = [m5b_x,m5b_y,m5b_pitch,m5b_roll,m5b_yaw,m5b_y_base,m5b_y_base_positioner,m5b_y_combined,m5b_mirror] # @UndefinedVariable
metadata_group2 = m1b_list + m1c_list + m3b_list + m4b_list + m5b_list
d1b_list = [d1b_y] # @UndefinedVariable
d2b_list = [d2b_y,d2b_y_positioner] # @UndefinedVariable
d3b_list = [d3b_y,d3b_y_positioner] # @UndefinedVariable
d4b_list = [d4b_y,d4b_y_positioner] # @UndefinedVariable
d5b_list = [d5b_y_positioner] # @UndefinedVariable
d6b_list = [d6b_y,d6b_y_positioner] # @UndefinedVariable
d7b_list = [d7b_y,d7b_y_positioner] # @UndefinedVariable
d8b_list = [d8b_y,d8b_y_positioner] # @UndefinedVariable
d9b_list = [d9b_y,d9b_y_positioner] # @UndefinedVariable
d10b_list = [d10b_x,d10b_x_positioner] # @UndefinedVariable
metadata_group3 = d1b_list + d2b_list + d3b_list + d4b_list + d5b_list + d6b_list + d7b_list + d8b_list + d9b_list + d10b_list
d21b_list = [d21b_y,d21b_y_positioner] # @UndefinedVariable
sm21b_list = [sm21b_x,sm21b_y,sm21b_z,sm21b_roty] # @UndefinedVariable
sm52b_list = [sm52b_x,sm52b_y,sm52b_z,sm52b_roty,sm52b_rotz,sm52b_xp,sm52b_yp,sm52b_zp] # @UndefinedVariable
ring_list = [ring_current] # @UndefinedVariable
pgm_list = [pgm_energy,pgm_cff,pgm_grating_pitch,pgm_grating_x,pgm_mirror_pitch,pgm_mirror_x,pgm_grating,pgm_mirror,pgm_override] # @UndefinedVariable
shutter_list = [expt_shutter,pss_shutter1_con,pss_shutter2_con,fast_shutter_con] # @UndefinedVariable
other_list = [img22b,img23b,cap21b,cap22b,_es2_temp_temperature_monitor,_es2_temp_output_monitor, _es2_temp_setpoint_monitor] # @UndefinedVariable
es1_list = [_es1_temp_51_temperature_monitor, _es1_temp_51_setpoint_monitor, _es1_temp_51_output_monitor, _es1_temp_52_temperature_monitor, _es1_temp_52_setpoint_monitor, _es1_temp_52_output_monitor]  # @UndefinedVariable
mfc_list = [mfc1, mfc2, mfc3, mfc4, mfc5, mfc6, mfc7, mfc8] # @UndefinedVariable
metadata_group4 = d21b_list + sm21b_list + sm52b_list + ring_list + pgm_list + shutter_list + other_list + es1_list
meta_data_list = metadata_group1 + metadata_group2 + metadata_group3 + metadata_group4

[meta_add(each) for each in meta_data_list]
[meta_add(each) for each in patch_panel_ES1.getGroupMembersAsArray()]# @UndefinedVariable
[meta_add(each) for each in patch_panel_ES2.getGroupMembersAsArray()]# @UndefinedVariable

from scan.miscan import miscan  # @UnusedImport
print("-"*100)
from scan.flyscan_command import flyscannable, FlyScanPositionsProvider, flyscan  # @UnusedImport
from  scan import flyscan_command; print(flyscan_command.__doc__)  # @UndefinedVariable

print("-"*100)
# import sputter functions
execfile("/dls_sw/b07/scripts/Beamline/sputter_funcs.py")

print "-----------------------------------------------------------------------------------------------------------------"
