# -*- coding: utf-8 -*-

'''
    File name: utilities.py
    Author: xke49157
    Affiliation: Diamond Light Source
    Date created: 07/08/2019
    Python Version: 2.7


    CODE OUTLINE
        This code contains the definitions of functions that are common across multiple programs.
    '''

import os
import numpy as np
from numpy import genfromtxt
import nexusformat.nexus as nx

''' These variables define the y and x resolution of the image sensor in terms of pixels. '''
CAM_X_RES = 2452     #pixels
CAM_Y_RES = 2056     #pixels

''' These variables denote how much the image moves in relation to how the motors move.
    For every 1mm the motors move features on the image are translated by approximaetly 5000 pixels.
    There are separate variables for the x and y axis noted as 'X_AXIS_PIXELS_PER_MM'
    and 'Y_AXIS_PIXELS_PER_MM'.
    The default values should perform adequately, however the values many need to be changed
    in the event of changes to the hardware.
    The calibration values are obtained from the calibration code, which is found at:
        "Calibration_program.py" '''
X_AXIS_PIXELS_PER_MM = 4890     #pixels/mm
Y_AXIS_PIXELS_PER_MM = 4890     #pixels/mm

''' These variables denote the size of the sample area visible in the field of view of the camera.
    These are measured in units of mm. '''
X_AXIS_FOV_MM = float(CAM_X_RES)/float(X_AXIS_PIXELS_PER_MM)     #mm
Y_AXIS_FOV_MM = float(CAM_Y_RES)/float(Y_AXIS_PIXELS_PER_MM)     #mm


def list_files(path, file_extension):
    ''' This function creates a list of the files with a specified file extension,
        for a given folder.
        The file extension must be specified as a string, and must contain the decimal separator.
        The folder is specified by the 'path' variable. 
    '''
    try:
        files_list = []
        for file in os.listdir(path):
            if file.endswith(file_extension):
                files_list.append(str(os.path.join(path, file)))
        files_list.sort()
        print("    %d %s files have been found" % (len(files_list), file_extension))
        if not files_list:
            print("Error: No files found in folder with %s extension" % file_extension)
        return files_list
    except:
        print("Error: Folder not found")


def check_scan_format(scan_command):
    ''' This function checks that the scan command has the correct format.
        The scan command needs to have the form:
            'scan pcssx  __  __  __ pcssy __  __  __ pcsscam __ '
       As an example, a scan command could be:
            'scan pcssx 11.1 13 0.1 pcssy 13 15 0.1 pcsscamtif 0.05' 
    '''
    try:
        scan_command_accepted = True
        scan_command = scan_command.split(" ")
        if str(scan_command[1]) != "pcssx":
            scan_command_accepted = False
        elif str(scan_command[5]) != "pcssy":
            scan_command_accepted = False
    except IndexError:
        print("Error: Scan command is not of the correct format")
    except AttributeError:
        print("Error: Scan command object is not a string type")
    return scan_command_accepted


def get_scan_command(file_path):
    ''' This function obtains the scan command given the .nxs file. '''
    nxdata = nx.nxload(file_path)
    scan_command = str(nxdata.entry1.scan_command)
    scan_command_accepted = check_scan_format(scan_command)
    if scan_command_accepted:
        return scan_command
    else:
        return None


def get_scan_motor_positions(file_path):
    ''' This function obtains the motor positions of a scan, given the .nxs file of the scan. '''
    nxdata = nx.nxload(file_path)
    x_motor_positions = np.asarray(nxdata.entry1.instrument.pcssx.pcssx).round(4)
    x_motor_positions = list(x_motor_positions[:, 0])
    y_motor_positions = np.asarray(nxdata.entry1.instrument.pcssy.pcssy).round(4)
    y_motor_positions = list(y_motor_positions[0, :])
    return x_motor_positions, y_motor_positions

