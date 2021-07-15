# -*- coding: utf-8 -*-

'''
    File name: Calibrate_sample_holder_rotation.py
    Author: xke49157
    Affiliation: Diamond Light Source
    Date created: 02/08/2019
    Python Version: 2.7

    CODE OUTLINE
    This code calculates the rotation of the sample holder of the PCSS relative to the PEEM.
    
    In order to simplify the co-ordinate mapping from PCSS to PEEM, it is necessary to ensure
    that the axis of the PCCS relative to the sample are the same in the PCSS as they are 
    in the PEEM. This implies makes the x axis PEEM co-ordinate a function only of the PCSS
    x co-ordinate, and likewise for y.
    The rotation of the sample holder is measured by comparing the coordinates of features
    on a sample as measured by the PEEM compared to the PCSS. 
    The co-ordinates of sample features are taken as an input and the rotation of the sample
    holder is returned at the end of the program.
    '''

import numpy as np
from numpy import genfromtxt
import os

# Import the data for the measurements of the sample
PEEM_data = genfromtxt('PEEM_measurements.csv', delimiter=',')
PCSS_data = genfromtxt('PCSS_measurements.csv', delimiter=',')

def Rotate_points(data_points, rotation_angle):
    ''' This function performs a rotation on the set of data_points inputted. 
        The points are rotated by an angle of 'rotation_angle'
        which has units of degrees'''
    rotation_matrix = np.asarray([[np.cos(rotation_angle/180.0*np.pi), np.sin(rotation_angle/180.0*np.pi)],
                        [-np.sin(rotation_angle/180.0*np.pi), np.cos(rotation_angle/180.0*np.pi)]])
    
    # Multiply the set of points by the rotation matrix
    data_points = np.matmul(data_points, rotation_matrix)
    return data_points

# Generate a set of angles to test
angles = np.linspace(-1,1,1000)
linear_fit_residuals = []

for angle in angles:
    # Rotate the PCSS data by the test angle
    PEEM_data_rotated = Rotate_points(PEEM_data, angle)
    
    # Perform a linear fit between the PCSS points and the PEEM points
    px, x_residual, _, _, _ = np.polyfit(PCSS_data[:, 0], PEEM_data_rotated[:, 0], 1, full=True)
    py, y_residual, _, _, _ = np.polyfit(PCSS_data[:, 1], PEEM_data_rotated[:, 1], 1, full=True)
    linear_fit_residuals.append(x_residual+y_residual)

# Find the rotation value that has smallest linear fit residuals
rotation = angles[np.argmin(np.asarray(linear_fit_residuals))]
print("The sample holder is rotated by an angle of %s degrees" % round(rotation, 3))

# Get linear fit paramters for best angle
px, x_residual, _, _, _ = np.polyfit(PCSS_data[:, 0], PEEM_data[:, 0], 1, full=True)
py, y_residual, _, _, _ = np.polyfit(PCSS_data[:, 1], PEEM_data[:, 1], 1, full=True)
print(px)
print("---------")
print(py)
print("---------")

