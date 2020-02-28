'''
Run this to get ptychography-related metadata
'''
from ptycho.ptycho_scannables import andorPixelSizeCalc
from gdaserver import andor_binning_x, andor_binning_y, andor_cooler_temperature_readback, andor_cooler_temperature_setpoint
from gdaserver import andor_information, andor_region_size_x, andor_region_size_y, andor_region_start_x, andor_region_start_y
from gdaserver import andor_vertical_shift_speed, andor_ADC_speed, ptychography_distance

# Most Andor-related scannables are already defined in Spring/XML
# This function adds custom (Jython) scannables
pixel_size_x_name = "andor_binned_pixel_size_x"
pixel_size_y_name = "andor_binned_pixel_size_y"

# This script may be run multiple times (e.g. by reset_namespace), so remove the scannables
# from the scannable group if they are already there.
scannable_names = [pixel_size_x_name, pixel_size_y_name]
for member in andor_information.getGroupMembersAsArray():
    if member.getName() in scannable_names:
        andor_information.removeGroupMemberByScannable(member)

# Create pixel size scannables and add to the scannable group
andor_binned_pixel_size_x = andorPixelSizeCalc(andor_binning_x, pixel_size_x_name)
andor_binned_pixel_size_y = andorPixelSizeCalc(andor_binning_y, pixel_size_y_name)

andor_information.addGroupMember(andor_binned_pixel_size_x, False)
andor_information.addGroupMember(andor_binned_pixel_size_y, False)

# Create a list of all Andor-related scannables
scannable_list = [ptychography_distance, andor_binning_x, andor_binning_y, andor_region_start_x,
                  andor_region_start_y, andor_region_size_x, andor_region_size_y, andor_ADC_speed,
                  andor_vertical_shift_speed, andor_cooler_temperature_setpoint, andor_cooler_temperature_readback,
                  andor_binned_pixel_size_x, andor_binned_pixel_size_y, andor_information]
