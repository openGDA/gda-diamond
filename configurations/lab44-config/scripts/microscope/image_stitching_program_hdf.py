# -*- coding: utf-8 -*-


''' File name: image_stitching_program_hdf.py
    Author: xke49157
    Affiliation: Diamond Light Source
    Date created: 15/08/2019
    Python Version: 2.7

    CODE OUTLINE
    This is a code for stitching together the images generated from a sample scan.
    Given the data folder containing the images and the scan command used to collect
    the image data this code will stitch together the images from the scan,
    and save the result to the same folder containing the image data.
    The result is saved as a nxs file which can then be viewed in DAWN.
    The coordinates of the PEEM are calculated and saved as axes which are then
    displayed on the image in DAWN.
    '''

# Import necessary packages
import sys
import os
import datetime
import numpy as np
import matplotlib
from PIL import Image
import h5py

# Add current folder to system directory to locate utilities module
#dirname = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(dirname)

from utilities import get_scan_motor_positions
from utilities import CAM_X_RES, CAM_Y_RES
from utilities import X_AXIS_PIXELS_PER_MM, Y_AXIS_PIXELS_PER_MM
from utilities import X_AXIS_FOV_MM, Y_AXIS_FOV_MM

def get_stitch_paramters(filename):
    '''The function obtains the parameters needed to stitch the images together.
    '''
    x_motor_positions, y_motor_positions = get_scan_motor_positions(filename)
    positions = (x_motor_positions, y_motor_positions)

    # Calculating the necessary amount of overlap needed to align the images")
    x_axis_scan_movement = abs(x_motor_positions[0]-x_motor_positions[1]).round(5)
    y_axis_scan_movement = abs(y_motor_positions[0]-y_motor_positions[1]).round(5)
    x_overlap = CAM_X_RES-(x_axis_scan_movement*X_AXIS_PIXELS_PER_MM)
    y_overlap = CAM_Y_RES-(y_axis_scan_movement*Y_AXIS_PIXELS_PER_MM)
    x_overlap = int(int(x_overlap/2)*2)
    y_overlap = int(int(y_overlap/2)*2)

    # Calculating the array size for a single vertically stitched column of images
    x_column_shape = int((CAM_Y_RES-y_overlap)*(len(y_motor_positions)-1)+CAM_Y_RES)
    y_column_shape = int(CAM_X_RES)
    return positions, (x_overlap, y_overlap), (x_column_shape, y_column_shape)

def get_image_dataset(filename):
    ''' This function creates a numpy array of the image data from the .hdf file.
    '''
    scanfilenamehdf = filename.replace("lab44", "pcsscam").replace(".nxs", ".hdf")
    data = h5py.File(scanfilenamehdf, 'r')
    data = data['entry']['data']['data']
    data = np.asarray(data)
    return data

def perform_vertical_stiching(dataset, motor_positions, column_shape, overlap_val):
    ''' In this section images with the same x-axis motor position are stitched together.
    This part of the code performs all of the vertical stitching of images, creating
    a column for each pcssx value.
    '''
    # Create an empty array to store the stitched column images
    stitched_columns = np.empty((len(motor_positions[0]), column_shape[0], column_shape[1]))
    col_index, row_index = 0, 0
    for col in motor_positions[0]:
        row_index = 0
        col_1 = np.empty([])
        for row in motor_positions[1]:
            if row == motor_positions[1][-1]:
                stitched_columns[col_index] = col_1
            else:
                if row == motor_positions[1][0]:
                    im_1 = dataset[col_index, row_index, :, :]
                    im_2 = dataset[col_index, row_index+1, int(overlap_val/2):, :]
                else:
                    im_1 = col_1
                    im_2 = dataset[col_index, row_index+1, int(overlap_val/2):, :]
                current_y_size = int(np.shape(im_1)[0])
                # Get the necessary regions of im_1 and im_2 and stitch them together
                im_1 = im_1[:int(current_y_size-overlap_val/2), :]
                col_1 = np.vstack((im_1, im_2))
            row_index += 1
        col_index += 1
    return stitched_columns

def perform_horizontal_stitching(images, motor_positions, overlap_val):
    ''' In this function the image columns are combined horizontally to form the complete image.
    '''
    x_final_image_shape = int((CAM_X_RES-overlap_val)*(len(motor_positions[0])-1)+CAM_X_RES)
    y_final_image_shape = np.shape(images)[1]
    final_image = np.empty((y_final_image_shape, x_final_image_shape))
    col_index = 0
    x_pos1, x_pos2 = 0, 0
    for col in motor_positions[0]:
        if col == motor_positions[0][0]:
            im_1 = images[col_index, :, :int(CAM_X_RES-(overlap_val/2))]
            x_pos1 = 0
        elif col == motor_positions[0][-1]:
            im_1 = images[col_index, :, int(overlap_val/2):]
            x_pos1 = x_pos2
        else:
            im_1 = images[col_index, :, int(overlap_val/2):int(CAM_X_RES-(overlap_val/2))]
            x_pos1 = x_pos2
        x_pos2 = x_pos1+(np.shape(im_1)[1])
        final_image[:, x_pos1:x_pos2] = im_1
        col_index += 1
    return final_image

def rescale_image(image, scale_factor=2):
    ''' This function takes a numpy array as an input and uses the PIL resize function to
    resize the array to a smaller size. This speeds up the saving and plotting process.
    '''
    # Generate the new dimensions of the image as a tuple
    new_shape = (int((np.shape(image)[1])/scale_factor), int((np.shape(image)[0])/scale_factor))

    img = Image.fromarray(np.uint8(image))
    img = img.resize(new_shape, Image.ANTIALIAS)
    image = np.array(img)
    return image

def create_filename(path, scannumber, add_time=False):
    ''' This function generates a filename for the stitched image based on the data folder
    and time of image creation.
    '''
    filename = path.split("lab44-")[0]
    filename += 'scan_' + str(scannumber) + '_stitched_image'
    if add_time:
        time_val = str(datetime.datetime.now())
        time_val = time_val.replace(" ", "_")
        time_val = (time_val.split("."))[0]
        time_val = time_val.replace(":", "_")
        filename += '_' + time_val
    return filename

def get_pcss_motor_coords_for_image(x_motor_positions, y_motor_positions):
    ''' This function generates the co-ordinates of each edge of the stitched image,
        in terms of the motor co-ordinates of the PCSS. 
    '''
    x_scan_start_motor_pos = (x_motor_positions[0] - X_AXIS_FOV_MM/2).round(5)
    y_scan_start_motor_pos = (y_motor_positions[0] - Y_AXIS_FOV_MM/2).round(5)
    x_scan_end_motor_pos = (x_motor_positions[-1] + X_AXIS_FOV_MM/2).round(5)
    y_scan_end_motor_pos = (y_motor_positions[-1] + Y_AXIS_FOV_MM/2).round(5)
    extent_vals = [x_scan_start_motor_pos, x_scan_end_motor_pos,
                   y_scan_start_motor_pos, y_scan_end_motor_pos]
    return extent_vals

def map_pcss_to_peem(value, axis, lin_fit_x, lin_fit_y):
    ''' This function maps between the PCSS and the PEEM motor co-ordinates. 
    '''
    if axis == 0:
        value *= lin_fit_y[0]
        value += lin_fit_y[1]
    if axis == 1:
        value *= lin_fit_x[0]
        value += lin_fit_x[1]
    return value

def get_peem_motor_coords_for_image(motor_positions, calibration_data_path):
    ''' This function generates the co-ordinates of each edge of the stitched image,
        in terms of the motor co-ordinates of the PEEM. 
    '''
    # Get extent values for PCSS motor co-ordiantes
    extent_vals = get_pcss_motor_coords_for_image(motor_positions[0], motor_positions[1])

    # Change the save directory to where the calibration data is stored
    # Then import the data for the measurements of the sample
    os.chdir(calibration_data_path)
    peem_data = np.genfromtxt('calibration_data_PEEM_measurements2.csv', delimiter=',')
    pcss_data = np.genfromtxt('calibration_data_PCSS_measurements2.csv', delimiter=',')

    # Get linear fit paramters for best angle
    lin_fit_x, x_residual, _, _, _ = np.polyfit(pcss_data[:, 0], peem_data[:, 0], 1, full=True)
    lin_fit_y, y_residual, _, _, _ = np.polyfit(pcss_data[:, 1], peem_data[:, 1], 1, full=True)

    extent_vals[0] = map_pcss_to_peem(extent_vals[0], 1, lin_fit_x, lin_fit_y)
    extent_vals[1] = map_pcss_to_peem(extent_vals[1], 1, lin_fit_x, lin_fit_y)
    extent_vals[2] = map_pcss_to_peem(extent_vals[2], 0, lin_fit_x, lin_fit_y)
    extent_vals[3] = map_pcss_to_peem(extent_vals[3], 0, lin_fit_x, lin_fit_y)
    return extent_vals

def get_nxs_file_axes_arrays(extent_vals, img_shape):
    x_axes = np.linspace(extent_vals[0], extent_vals[1], img_shape[1])
    y_axes = np.linspace(extent_vals[2], extent_vals[3], img_shape[0])
    return x_axes, y_axes

def write_nexus(nexuspath, image, x_axes, y_axes):
    ''' This function creates a nexus file which will display the stitched
        image with the PEEM co-ordinates when opened in DAWN.
    '''
    with h5py.File(nexuspath, "w") as file:
        file["/entry/image/data"] = image
        file["/entry"].attrs["NX_class"] = "NXentry"
        nxdata = file["/entry/image"]
        nxdata.attrs["NX_class"] = "NXdata"
        nxdata.attrs["signal"] = "data"
        nxdata.attrs["axes"] = ["pcssy", "pcssx"]
        nxdata["pcssy"] = y_axes
        nxdata["pcssy"].attrs["primary"] = "1"
        nxdata["pcssy"].attrs["axis"] = "1,2"
        nxdata["pcssx"] = x_axes
        nxdata["pcssx"].attrs["primary"] = "1"
        nxdata["pcssx"].attrs["axis"] = "1,2"
        nxdata.attrs["pcssy_indices"] = 0
        nxdata.attrs["pcssx_indices"] = 1

def process_stitching(nxs_filename, scannumber):
    ''' This function is a wrapper, containing the whole image stitching and
        co-ordinate mapping processes.
    '''
    calibration_data_path = "/dls_sw/lab44/scripts/xke49157/Current_code"
    save_to_png = False
    motor_positions, overlap_vals, column_shape = get_stitch_paramters(nxs_filename)
    dataset = get_image_dataset(nxs_filename)
    stitched_columns = perform_vertical_stiching(dataset, motor_positions, column_shape, overlap_vals[1])
    stitched_image = perform_horizontal_stitching(stitched_columns, motor_positions, overlap_vals[0])
    stitched_image = rescale_image(stitched_image)
    save_filename = create_filename(nxs_filename, scannumber)
    extent_vals = get_peem_motor_coords_for_image(motor_positions, calibration_data_path)
    x_axes, y_axes = get_nxs_file_axes_arrays(extent_vals, stitched_image.shape)
    write_nexus(save_filename+".nxs", stitched_image, x_axes, y_axes)
    if save_to_png==True:
        matplotlib.rc('image', cmap='jet')
        matplotlib.image.imsave((save_filename +'.png'), stitched_image)
    return str("processing complete")

#scanfilename = "/dls/i06/data/2019/cm22966-3/processing/optical_microscope/lab44-98.nxs"
#scannumber = 98
#process_stitching(scanfilename, scannumber)

