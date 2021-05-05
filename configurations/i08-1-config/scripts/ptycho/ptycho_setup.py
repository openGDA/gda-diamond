'''
Run this to get ptychography-related metadata
'''
from ptycho.ptycho_scannables import BinnedPixelSize
from gdaserver import axis_binning_x, axis_binning_y, axis_cooler_temperature_readback, axis_cooler_temperature_setpoint
from gdaserver import axis_information, axis_region_size_x, axis_region_size_y, axis_region_start_x, axis_region_start_y
from gdaserver import axis_gain_mode, axis_bin_mode, axis_frame_format, axis_roi_mode, axis_pixel_size, ptychography_distance

# Most Axis-related scannables are already defined in Spring/XML
# This function adds custom (Jython) scannables
binned_pixel_size_x_name = "axis_binned_pixel_size_x"
binned_pixel_size_y_name = "axis_binned_pixel_size_y"

# This script may be run multiple times (e.g. by reset_namespace), so remove the scannables
# from the scannable group if they are already there.
scannable_names = [binned_pixel_size_x_name, binned_pixel_size_y_name]
for member in axis_information.getGroupMembersAsArray():
    if member.getName() in scannable_names:
        axis_information.removeGroupMemberByScannable(member)

# Create pixel size scannables and add to the scannable group
axis_binned_pixel_size_x = BinnedPixelSize(axis_pixel_size, axis_binning_x, binned_pixel_size_x_name)
axis_binned_pixel_size_y = BinnedPixelSize(axis_pixel_size, axis_binning_y, binned_pixel_size_y_name)

axis_information.addGroupMember(axis_binned_pixel_size_x, False)
axis_information.addGroupMember(axis_binned_pixel_size_y, False)

# Create a list of all Axis-related scannables
scannable_list = [ptychography_distance, axis_binning_x, axis_binning_y, axis_region_start_x,
                  axis_region_start_y, axis_region_size_x, axis_region_size_y, axis_gain_mode, axis_bin_mode, axis_frame_format,
                  axis_roi_mode, axis_pixel_size, axis_cooler_temperature_setpoint, axis_cooler_temperature_readback,
                  axis_binned_pixel_size_x, axis_binned_pixel_size_y, axis_information]
