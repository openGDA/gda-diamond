# localStation.py
# For beamline specific initialisation code.
#

from b07Shared.localStation import * # @UnusedWildImport
from b07Shared.utils.ExceptionLogs import localStation_exceptions, localStation_exception

print("=================================================================================================================")
print("Performing beamline specific initialisation code (b07-1).")
print("=================================================================================================================")
print("")

import sys
from gdascripts.messages.handle_messages import simpleLog
from uk.ac.diamond.daq.configuration import ConfigUtils

print("-"*100)
print "installing standard scans with processing"
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()
print("")

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
from metadata.metashop import meta_add, meta_ll, meta_ls, meta_rm  # @UnusedImport
import metadata.metashop as metashop  # @UnusedImport

print("-"*100)
meta_data_list = [endstation, ring_current, analyser_sledge] # @UndefinedVariable
# add sample positions depending on endstation in use
if installation.isLive():
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

meta_shutter_list = [expt_shutter,fast_shutter] # @UndefinedVariable
patch_panel_list = [ppc_temp_1, ppc_temp_2, ppc_temp_3, ppc_temp_4, # @UndefinedVariable
					ppc_ai_1, ppc_ai_2, ppc_ai_3, ppc_ai_4,  # @UndefinedVariable
					ppc_ao_1, ppc_ao_2, ppc_ao_3, ppc_ao_4,  # @UndefinedVariable
					ppc_di_1, ppc_di_2, ppc_di_3, ppc_di_4,  # @UndefinedVariable
					ppc_do_5, ppc_do_6, ppc_do_7, ppc_do_8]  # @UndefinedVariable
crystal_monochromator_list = [ccmc_x, ccmc_y, ccmc_z, ccmc_named_position]  # @UndefinedVariable
diagnosis_list = [d9c_y_positioner, d9c_y,d7c_y,d21c_positioner,d21c_x]  # @UndefinedVariable
meta_pgm_list = [pgm_energy, pgm_cff, pgm_mirror_pitch, pgm_mirror_x, pgm_grating_pitch, pgm_grating_x,pgm_grating,pgm_mirror,pgm_override] # @UndefinedVariable
meta_mirrors_list = [m1b_mask_temp,	m1b_mirror_temp, # @UndefinedVariable
					m1c_x,m1c_y,m1c_pitch,m1c_roll,	m1c_yaw,m1c_mask_temp,m1c_mirror_temp, # @UndefinedVariable
					m3c_x,m3c_y,m3c_pitch,m3c_roll,m3c_yaw, # @UndefinedVariable
					m4c_x,m4c_y,m4c_pitch,m4c_roll,m4c_yaw, # @UndefinedVariable
					m5c_x,m5c_y,m5c_pitch,m5c_roll,	m5c_yaw]# @UndefinedVariable
meta_slit_list = [s1c_xcentre,s1c_xsize,s1c_xpos,s1c_xneg,s1c_ycentre,s1c_ysize,s1c_ypos,s1c_yneg,s2c_xcentre,s2c_xsize, # @UndefinedVariable
					s2c_ycentre,s2c_ysize,s3c_xcentre,s3c_xsize,s3c_ycentre,s3c_ysize,s4c_xgap,s4c_xgapsize,s4c_ygap,s4c_ygapsize,s4c_z]# @UndefinedVariable
meta_temperature_list = [es_01_temp_output,es_01_temp_temperature,es_01_temp_setpoint,es_01_temp_ramprate]# @UndefinedVariable
meta_stanfords_list = [ca31c_sensitivity, # @UndefinedVariable
						ca31c_sensitivity_units, # @UndefinedVariable
						ca31c_bias_voltage_status,# @UndefinedVariable
						ca31c_bias_voltage,# @UndefinedVariable
						ca31c_filter_type,# @UndefinedVariable
						ca31c_filter_highpass,# @UndefinedVariable
						ca31c_filter_lowpass,# @UndefinedVariable
						ca31c_gain_mode,# @UndefinedVariable
						ca31c_offset,# @UndefinedVariable
						ca31c_offset_units,# @UndefinedVariable
						ca31c_offset_current,# @UndefinedVariable
						ca31c_inverted,# @UndefinedVariable
						ca31c_current,# @UndefinedVariable
						ca31c_average_current,# @UndefinedVariable
						ca32c_sensitivity,# @UndefinedVariable
						ca32c_sensitivity_units,# @UndefinedVariable
						ca32c_bias_voltage_status,# @UndefinedVariable
						ca32c_bias_voltage,# @UndefinedVariable
						ca32c_filter_type,# @UndefinedVariable
						ca32c_filter_highpass,# @UndefinedVariable
						ca32c_filter_lowpass,# @UndefinedVariable
						ca32c_gain_mode,# @UndefinedVariable
						ca32c_offset,# @UndefinedVariable
						ca32c_offset_units,# @UndefinedVariable
						ca32c_offset_current,# @UndefinedVariable
						ca32c_inverted,# @UndefinedVariable
						ca32c_current,# @UndefinedVariable
						ca32c_average_current,# @UndefinedVariable
						ca33c_sensitivity,# @UndefinedVariable
						ca33c_sensitivity_units,# @UndefinedVariable
						ca33c_bias_voltage_status,# @UndefinedVariable
						ca33c_bias_voltage,# @UndefinedVariable
						ca33c_filter_type,# @UndefinedVariable
						ca33c_filter_highpass,# @UndefinedVariable
						ca33c_filter_lowpass,# @UndefinedVariable
						ca33c_gain_mode,# @UndefinedVariable
						ca33c_offset,# @UndefinedVariable
						ca33c_offset_units,# @UndefinedVariable#
						ca33c_offset_current,# @UndefinedVariable
						ca33c_inverted,# @UndefinedVariable
						ca33c_current,# @UndefinedVariable
						ca33c_average_current,# @UndefinedVariable
						ca34c_sensitivity,# @UndefinedVariable
						ca34c_sensitivity_units,# @UndefinedVariable
						ca34c_bias_voltage_status,# @UndefinedVariable
						ca34c_bias_voltage,# @UndefinedVariable
						ca34c_filter_type,# @UndefinedVariable
						ca34c_filter_highpass,# @UndefinedVariable
						ca34c_filter_lowpass,# @UndefinedVariable
						ca34c_gain_mode,# @UndefinedVariable
						ca34c_offset,# @UndefinedVariable
						ca34c_offset_units,# @UndefinedVariable
						ca34c_offset_current,# @UndefinedVariable
						ca34c_inverted,# @UndefinedVariable
						ca34c_current,# @UndefinedVariable
						ca34c_average_current,# @UndefinedVariable
						ca99c_sensitivity,# @UndefinedVariable
						ca99c_time_constant,# @UndefinedVariable
						ca99c_channel_one,# @UndefinedVariable
						ca99c_channel_two]# @UndefinedVariable

meta_vacuum_list = [cap03c, cap04c, pir82c, pir83c, # @UndefinedVariable
					img01c,	img02c, img03c, img04c, img05c,	img06c,	img07c,	img08c, img09c, img10c, img11c] # @UndefinedVariable

meta_data_list += patch_panel_list+crystal_monochromator_list+diagnosis_list+meta_temperature_list+meta_pgm_list+meta_vacuum_list+meta_mirrors_list+meta_slit_list+meta_stanfords_list+meta_shutter_list

for each in meta_data_list:
		meta_add(each)

print("-"*100)
from scannables.pgm_energy_multilayer_grating import pgm_energy_mlg
help(pgm_energy_mlg)

print("-"*100)
if len(localStation_exceptions) > 0:
	simpleLog("=============== %r ERRORS DURING STARTUP ================" % len(localStation_exceptions))
	for localStationException in localStation_exceptions:
		simpleLog(localStationException)

print("**************************************************")
print("localStation.py completed.")
print("**************************************************")

