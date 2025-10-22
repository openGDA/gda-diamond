# localStation.py
# For beamline specific initialisation code.
#

from b07Shared.localStation import * # @UnusedWildImport
from uk.ac.diamond.osgi.services import ServiceProvider
from uk.ac.diamond.daq.configuration import BeamlineConfiguration

print "=================================================================================================================";
print "Performing beamline specific initialisation code (b07).";
print "=================================================================================================================";
print ("")

print("-"*100)
print "installing standard scans with processing"
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()
print("")

from scannables.detector_output_processing import BekhoffAdcOutputProcessing
ca35b_ca18b_quotient = BekhoffAdcOutputProcessing('ca35b_ca18b_quotient', ca35b, ca18b, 'divide_detector_output')  # @UndefinedVariable
ca36b_ca18b_quotient = BekhoffAdcOutputProcessing('ca36b_ca18b_quotient', ca36b, ca18b, 'divide_detector_output')  # @UndefinedVariable

print("-"*100)
print("setup meta-data provider commands: meta_add, meta_ll, meta_ls, meta_rm ")
from metadata.metashop import meta_add,meta_ll,meta_ls, meta_rm  # @UnusedImport
import metadata.metashop  # @UnusedImport
print("Can now add meta data items to be captured in data files.")
meta_data_list = [] #other common metadata can be added here if required!
s1b_list = [s1b_xcentre,s1b_ycentre,s1b_xsize,s1b_ysize,s1b_xpos,s1b_ypos,s1b_xneg,s1b_yneg] # @UndefinedVariable
s2b_list = [s2b_xsize,s2b_ysize,s2b_xcentre,s2b_ycentre] # @UndefinedVariable
s3b_list = [s3b_xsize,s3b_ysize,s3b_xcentre,s3b_ycentre] # @UndefinedVariable
s4b_list = [s4b_xgap, s4b_ygap,s4b_xgapsize, s4b_ygapsize,s4b_z] # @UndefinedVariable
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
shutter_list = [expt_shutter,pss_shutter1_con,pss_shutter2_con,fast_shutter_con, GV13] # @UndefinedVariable
pressures_list = [img22b,img23b,cap21b,cap22b,img10b,img51b,img53b,img60b] # @UndefinedVariable
es2_temperatures_list = [es2_21_temp_temperature,es2_21_temp_output, es2_21_temp_setpoint] # @UndefinedVariable
es1_temperatures_list = [es1_51_temp_temperature, es1_51_temp_setpoint, es1_51_temp_output, es1_52_temp_temperature, es1_52_temp_setpoint, es1_52_temp_output]  # @UndefinedVariable
mfc_list = [mfc1, mfc2, mfc3, mfc4, mfc5, mfc6, mfc7, mfc8] # @UndefinedVariable
metadata_group4 = d21b_list + sm21b_list + sm52b_list + ring_list + pgm_list + shutter_list + pressures_list + es1_temperatures_list + es2_temperatures_list

metadata_group5 = [	ca18b_current,# @UndefinedVariable
				ca18b_gain,# @UndefinedVariable
				ca18b_average_current, # @UndefinedVariable
				ca16b_sensitivity ,# @UndefinedVariable
				ca16b_sensitivity_units ,# @UndefinedVariable
				ca16b_bias_voltage_status ,# @UndefinedVariable
				ca16b_bias_voltage ,# @UndefinedVariable
				ca16b_filter_type ,# @UndefinedVariable
				ca16b_filter_highpass ,# @UndefinedVariable
				ca16b_filter_lowpass ,# @UndefinedVariable
				ca16b_gain_mode ,# @UndefinedVariable
				ca16b_offset ,# @UndefinedVariable
				ca16b_offset_units ,# @UndefinedVariable
				ca16b_offset_current ,# @UndefinedVariable
				ca16b_inverted ,# @UndefinedVariable
				ca16b_current ,# @UndefinedVariable
				ca16b_average_current ,# @UndefinedVariable
				ca35b_sensitivity ,# @UndefinedVariable
				ca35b_sensitivity_units ,# @UndefinedVariable
				ca35b_bias_voltage_status ,# @UndefinedVariable
				ca35b_bias_voltage ,# @UndefinedVariable
				ca35b_filter_type ,# @UndefinedVariable
				ca35b_filter_highpass ,# @UndefinedVariable
				ca35b_filter_lowpass ,# @UndefinedVariable
				ca35b_gain_mode ,# @UndefinedVariable
				ca35b_offset ,# @UndefinedVariable
				ca35b_offset_units ,# @UndefinedVariable
				ca35b_offset_current ,# @UndefinedVariable
				ca35b_inverted ,# @UndefinedVariable
				ca35b_current ,# @UndefinedVariable
				ca35b_average_current ,# @UndefinedVariable
				ca36b_sensitivity ,# @UndefinedVariable
				ca36b_sensitivity_units ,# @UndefinedVariable
				ca36b_bias_voltage_status ,# @UndefinedVariable
				ca36b_bias_voltage ,# @UndefinedVariable
				ca36b_filter_type ,# @UndefinedVariable
				ca36b_filter_highpass ,# @UndefinedVariable
				ca36b_filter_lowpass ,# @UndefinedVariable
				ca36b_gain_mode ,# @UndefinedVariable
				ca36b_offset ,# @UndefinedVariable
				ca36b_offset_units ,# @UndefinedVariable
				ca36b_offset_current ,# @UndefinedVariable
				ca36b_inverted ,# @UndefinedVariable
				ca36b_current ,# @UndefinedVariable
				ca36b_average_current]# @UndefinedVariable

meta_data_list = metadata_group1 + metadata_group2 + metadata_group3 + metadata_group4 + metadata_group5+[endstation]# @UndefinedVariable

[meta_add(each) for each in meta_data_list]
[meta_add(each) for each in patch_panel_ES1.getGroupMembersAsArray()]# @UndefinedVariable
[meta_add(each) for each in patch_panel_ES2.getGroupMembersAsArray()]# @UndefinedVariable

from scan.miscan import miscan  # @UnusedImport
print("-"*100)
from scan.flyscan_command import flyscannable, FlyScanPositionsProvider, flyscan  # @UnusedImport
from  scan import flyscan_command; print(flyscan_command.__doc__)  # @UndefinedVariable

print("-"*100)
from gdascripts.scannable.sample_positions import SamplePositions
sm21b_sp = SamplePositions("sm21b_sp", [sm21b_x,sm21b_y,sm21b_z,sm21b_roty]) # @UndefinedVariable
sm52b_sp = SamplePositions("sm52b_sp", [sm52b_xp,sm52b_yp,sm52b_zp,sm52b_roty,sm52b_rotz]) # @UndefinedVariable
print("Creating sample positioner objects: " + sm21b_sp.getName() + ", " + sm52b_sp.getName())
print("Store sample manipulator position components in a dictionary, save them to a file and move sample manipulator to previously saved positions in the dictionary.")
help(sm21b_sp)

spring_profiles = ServiceProvider.getService(BeamlineConfiguration).profiles.toList()

#sample temperature
from gdascripts.scannable.temperature.sample_temperature import SampleTemperature
if "es1" in spring_profiles:
	if installation.isLive():
		# there are 2 temperature es1_temp_51, and es1_temp_52, which Fajin is not sure which is sample temperature
		tsample = SampleTemperature("tsample", es1_temp_52)  # @UndefinedVariable
	else:
		# there are 2 temperature monitor in ES1 - es1_51_temp_temperature, es1_52_temp_temperature
		tsample = SampleTemperature("tsample", es1_52_temp_temperature)  # @UndefinedVariable

if "es2" in spring_profiles:
	if installation.isLive():
		tsample = SampleTemperature("tsample", es2_temp)  # @UndefinedVariable
	else:
		tsample = SampleTemperature("tsample", es2_21_temp_temperature)  # @UndefinedVariable

if not spring_profiles or ("es1" in spring_profiles and "es2" in spring_profiles):
	# no profile or both profiles default to es1_temp_51
	if installation.isLive():
		tsample = SampleTemperature("tsample", es1_temp_51)  # @UndefinedVariable
	else:
		tsample = SampleTemperature("tsample", es1_51_temp_temperature)  # @UndefinedVariable

print("-"*100)
# import sputter functions
execfile("/dls_sw/b07/scripts/Beamline/sputter_funcs.py")

print "-----------------------------------------------------------------------------------------------------------------"
