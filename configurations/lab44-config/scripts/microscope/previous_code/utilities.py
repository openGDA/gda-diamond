# -*- coding: utf-8 -*-

'''
    File name: utilities.py
    Author: xke49157
    Affiliation: Diamond Light Source
    Date created: 07/08/2019
    Python Version: 2.7

    CODE OUTLINE
        This code contains the definitions of functions that are common across multiple 
        programs. Some global constants are also defined here.
        '''
        
import os
import numpy as np
from numpy import genfromtxt
import math
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image
import datetime
from nexusformat.nexus import *


''' These variables define the y and x resolution of the image sensor in terms of pixels. '''
cam_x_resolution = 2452     #pixels
cam_y_resolution = 2056     #pixels

''' These variables denote how much the image moves in relation to how the motors move.
    For every 1mm the motors move features on the image are translated by approximaetly 5000 pixels.
    There are separate variables for the x and y axis noted as 'x_axis_pixels_per_mm' 
    and 'y_axis_pixels_per_mm'.
    The default values should perform adequately, however the values many need to be changed
    in the event of changes to the hardware.
    The calibration values are obtained from the calibration code, which is found at:
        "Calibration_program.py" '''
x_axis_pixels_per_mm = 4890     #pixels/mm
y_axis_pixels_per_mm = 4890     #pixels/mm

''' These variables denote the size of the area of sample visible in the field of view of the camera.
    These are measured in units of mm. '''
x_axis_fov_mm = float(cam_x_resolution)/float(x_axis_pixels_per_mm)     #mm
y_axis_fov_mm = float(cam_y_resolution)/float(y_axis_pixels_per_mm)     #mm


def List_files(path, file_extension):
    ''' This function creates a list of the files with a specified file extension, 
        for a given folder.
        The file extension must be specified as a string, and must contain the decimal separator.
        The folder is specified by the 'path' variable. '''
    try:
        files_list = []
        for file in os.listdir(path):
            if file.endswith(file_extension):
                files_list.append(str(os.path.join(path, file)))
        files_list.sort()
        print("    %d %s files have been found" % (len(files_list), file_extension))
        
        if len(files_list)==0:
            print("Error: No files found in folder with %s extension" % file_extension)
        return files_list
    except:
        print("Error: Folder not found")

 
def Get_image_dimension(scan_end_motor_pos, scan_start_motor_pos, axis_scan_movement):
    ''' This function calculates the number of images along an axis given the movement
    between images and the range of motor values the images were taken for. '''
    val = abs(scan_end_motor_pos-scan_start_motor_pos)
    val /= axis_scan_movement
    val = int(round(val))
    val +=1
    return val


def Check_scan_format(scan_command):
    ''' This function checks that the scan command has the correct format.
        The scan command needs to have the form:
            'scan pcssx  __  __  __ pcssy __  __  __ pcsscamtif __ '
       As an example, a scan command could be:
            'scan pcssx 11.1 13 0.1 pcssy 13 15 0.1 pcsscamtif 0.05' '''
    try:
        scan_command_accepted = True
        scan_command = scan_command.split(" ")
        if str(scan_command[1]) != "pcssx":
            scan_command_accepted = False
        elif str(scan_command[5]) != "pcssy":
            scan_command_accepted = False
        elif str(scan_command[9]) != "pcsscamtif":
            scan_command_accepted = False
    
        if scan_command_accepted == True:
            print("2) Scan command accepted")
        else:
            print("Error: Scan command is invalid")
    except:
        print("Error: Scan command is not of the correct format")
    return scan_command_accepted


def Get_file_path(folder_path, scan_number):
    ''' This function gets the file path of the .nxs file for a given scan number. '''
    files_list = List_files(folder_path, ".nxs")
    for i in range(0, len(files_list)):
        file = files_list[i]
        file = file.split("/")[-1]
        file = file.split("-")[-1]
        file = file.split(".")[0]
        if str(scan_number)==file:
            file_path = files_list[i]
            return file_path
    print("Error: file path not found")


def Get_scan_command(file_path):
    ''' This function obtains the scan command given the .nxs file. '''
    b = nxload(file_path)
    scan_command = str(b.entry1.scan_command)
    scan_command_accepted = Check_scan_format(scan_command)
    if scan_command_accepted==True:
        return scan_command
    

def Get_scan_motor_positions(file_path):
    ''' This function obtains the motor positions of a scan, given the .nxs file of the scan. '''
    b = nxload(file_path)
    x_motor_positions = np.asarray(b.entry1.instrument.pcssx.pcssx).round(4)
    x_motor_positions = list(x_motor_positions[:,0])
    y_motor_positions = np.asarray(b.entry1.instrument.pcssy.pcssy).round(4)
    y_motor_positions = list(y_motor_positions[0,:])
    return x_motor_positions, y_motor_positions


def Get_PCSS_motor_coords_for_image(file_path, scan_number):
    ''' This function generates the co-ordinates of each edge of the stitched image,
        in terms of the motor co-ordinates of the PCSS. '''
    # Get the file path of the .nxs file containing the image metadata
    print("1) Finding image folder path")
    folder_path = file_path.split("/lab44")[0]
    image_data_path = folder_path + "/" + str(scan_number) + "_pcsscamImage"
    print("    image folder path is: %s" % image_data_path)
    
    print("2) Finding the image files in the .npy data folder")
    files_list = List_files(image_data_path, ".npy")
    
    # Find the scan command entered into GDA used to collect the image data
    print("3) Finding scan command")
    scan_command = Get_scan_command(file_path)
    print("    scan command is: %s" % scan_command)
    
    # Get the number of images per column and images per row for the particular scan being analysed
    print("4) Calculating the dimensions of the image stitch")
    x_motor_positions, y_motor_positions = Get_scan_motor_positions(file_path)
    im_per_row = len(x_motor_positions)
    im_per_col = len(y_motor_positions)
    print("    images per column: %s images" % (im_per_col))
    print("    images per row:    %s images" % (im_per_row))
    
    print("6) Calculating co-ordinates for stitched image edges")
    x_scan_start_motor_pos = (x_motor_positions[0] - x_axis_fov_mm/2).round(5)
    y_scan_start_motor_pos = (y_motor_positions[0] - y_axis_fov_mm/2).round(5)
    x_scan_end_motor_pos  = (x_motor_positions[-1] + x_axis_fov_mm/2).round(5)
    y_scan_end_motor_pos  = (y_motor_positions[-1] + y_axis_fov_mm/2).round(5)
    print("    x axis ranges from %s to %s mm" % (x_scan_start_motor_pos, x_scan_end_motor_pos))
    print("    y axis ranges from %s to %s mm" % (y_scan_start_motor_pos, y_scan_end_motor_pos))
    
    # Create a list to store the range of values to plot for the x and y axis of the figure 
    extent_vals=[x_scan_start_motor_pos, x_scan_end_motor_pos, y_scan_end_motor_pos, y_scan_start_motor_pos]
    return extent_vals

def Map_PCSS_to_PEEM(value, axis, px, py):
    ''' This function maps between the PCSS and the PEEM motor co-ordinates. '''
    if axis==0:
        value *= py[0]
        value += py[1]
    if axis==1:
        value *= px[0]
        value += px[1]
    return value

def Get_PEEM_motor_coords_for_image(file_path, scan_number):
    ''' This function generates the co-ordinates of each edge of the stitched image,
        in terms of the motor co-ordinates of the PEEM. '''
    # Get extent values for PCSS motor co-ordiantes
    extent_vals = Get_PCSS_motor_coords_for_image(file_path, scan_number)

    # Convert from PCSS to PEEM co-ordinates
    path_to_calibration_data = "/dls_sw/lab44/scripts/GavinHill/Current_code"
    
    # Change the save directory to where the calibration data is stored
    os.chdir(path_to_calibration_data)
    
    # Import the data for the measurements of the sample
    PEEM_data = genfromtxt('PEEM_measurements.csv', delimiter=',')
    PCSS_data = genfromtxt('PCSS_measurements.csv', delimiter=',')
    
    # Get linear fit paramters for best angle
    px, x_residual, _, _, _ = np.polyfit(PCSS_data[:, 0], PEEM_data[:, 0], 1, full=True)
    py, y_residual, _, _, _ = np.polyfit(PCSS_data[:, 1], PEEM_data[:, 1], 1, full=True)

    extent_vals[0] = Map_PCSS_to_PEEM(extent_vals[0], 1, px, py)
    extent_vals[1] = Map_PCSS_to_PEEM(extent_vals[1], 1, px, py)
    extent_vals[2] = Map_PCSS_to_PEEM(extent_vals[2], 0, px, py)
    extent_vals[3] = Map_PCSS_to_PEEM(extent_vals[3], 0, px, py)
    return extent_vals


    