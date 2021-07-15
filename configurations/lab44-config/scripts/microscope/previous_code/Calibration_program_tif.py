# -*- coding: utf-8 -*-

'''
    File name: Calibration_program.py
    Author: xke49157
    Affiliation: Diamond Light Source
    Date created: 01/08/2019
    Python Version: 2.7

    CODE OUTLINE
        This program is used to calibrate the PCSS image stitching routine.
        When a scan is performed, images are captured across the sample.
        The range of movement of the scan is set by the scan command parameters.
        Depending on the distance moved by the camera across the sample between image
        captures, there will be an amount of overlap between successive images.
        It is known that if the motor axis are translated by 1mm, a given feature on the
        camera image will be translated by approximately 5000 pixels.
        The purpose of this code is to fine-tune this measurement of image pixels per mm of motor travel.
        The x and y axis are driven by separate motors and each have a separate calibration routine.
        
    HOW TO USE THIS CODE
        1) Go to Section 1
        2) Change the "scan_command" variable to the scan command used to collect the data
        3) Change the "file_path" variable to the file path of the scan .nxs file
        4) Run script as python script
        5) Wait for new pixels per mm values to be printed
    '''

# Import relevant packages
import os
import numpy as np
import matplotlib.pyplot as plt

from utilities  import *

def Test_overlaps(im_1, im_2, overlap_guess, guess_varianceiance, cam_y_resolution, cam_x_resolution, axis):
    ''' This function takes two images as an input and varies the overlap amount between the
        two images. A test is the performed to see how well the images align for each given
        overlap amount. The results of this test are returned at the end of the function.
        '''
    # Define a list to store the overlap_metric values for each test amount of overlap
    # Define a list to store the test result values for eacch given overlap amount
    overlap_metrics = []
    amount_of_overlap = []
    
    # Create a for loop to test a range of overlap values
    # The overlap amount, denoted 'overlap', is measured in pixels
    # For example, an overlap of ten means that the bottom ten rows of pixels in the 
    # first image are being compared to the top ten rows of pixels in the second image (for axis=0)
    for overlap in range(overlap_guess-guess_varianceiance, overlap_guess+guess_varianceiance):
        # Create new arrays for the overlap sections of each image
        # Depending on the axis of the stitching the overlap section must be appropriately chosen 
        if axis==0:
            im_1_overlap = im_1[(cam_y_resolution-overlap):,:]
            im_2_overlap = im_2[:overlap,:]
        if axis==1:
            im_1_overlap = im_1[:,(cam_x_resolution-overlap):]
            im_2_overlap = im_2[:,:overlap]
        
        # Convert the overlap images to binary images for values above/below a chosen threshold
        # This converts the image from monochromatic, with pixels values ranging from 0-255,
        # to a binary image where every pixel is either 0 or 1 
        # The threshold values specifies the maximum pixel intensity for which a value is set to 0,
        # all pixels with intensities greater than 'threshold-value' are set to 1.
        threshold_value = 75
        im_1_overlap = np.where(im_1_overlap <= threshold_value, 0, 1)
        im_2_overlap = np.where(im_2_overlap <= threshold_value, 0, 1)
        
        # Check how well the overlapping sections match by subtracting im_2 from im_1
        # If the images match perfectly then one image subtracted from the other should return
        # an array of zeros, as something minus itself is zero. 
        # The mean is taken to normalise the metric for different overlap array sizes
        check_im = np.abs(im_2_overlap - im_1_overlap)
        overlap_metric = np.mean(check_im)
        
        overlap_metrics.append(overlap_metric)
        amount_of_overlap.append(overlap)
    return amount_of_overlap, overlap_metrics 

def Find_optimal_overlap(amount_of_overlap, overlap_metrics, overlap_guess, guess_variance):
    ''' This function takes the test results from the Test_overlaps function and 
        computes the optimal overlap amount needed to align the images.
        The optimal overlap is computed by two separate methods.
        Firstly the minimum is found by simply computing the minimum of the
        overlap fit metrics.
        To check that this is actually the local minimum a quadratic curve
        is also fitted to the data.
        '''
    # Firstly compute the optimal overlap from the minimum of the overlap metrics
    min_metric_val = int(np.argmin(overlap_metrics))
    optimal_overlap = overlap_guess-guess_variance+min_metric_val
    
    # Also compute the minimum from a quadratic fit to the data
    
    z = np.polyfit(np.asanyarray(amount_of_overlap), np.asanyarray(overlap_metrics), 2)
    poly_min = -z[1]/(2*z[0])
    return optimal_overlap, z, poly_min

def Perform_overlap_test(im_1, im_2, cam_y_resolution, cam_x_resolution, files_list, overlap_guess, guess_variance, graph, axis):
    ''' This function performs an overlap test on two inputted images im_1 and im_2.
        The function returns the optimal overlap of the images in case it was successfully found,
        and returns 0 if no optimum could be computed.
        '''
    # Test a range of overlaps and return the overlap_metric as a function of the amount of overlap
    amount_of_overlap, overlap_metrics = Test_overlaps(im_1, im_2, overlap_guess, guess_variance, cam_y_resolution, cam_x_resolution, axis)
    
    # Find the optimal overlap
    optimal_overlap, quadratic_fit, poly_min = Find_optimal_overlap(amount_of_overlap, overlap_metrics, overlap_guess, guess_variance)
    
    # Save the optimal overlap to the overlap values array in the case that an optimal overlap was found
    # Success case criteria:
        #1) The optimal overlap value is sufficiently close to the minimum of the quadratic curve
        #2) The optimal overlap is not found at the min or max end of the test values
    if abs(optimal_overlap-poly_min)<=5 and abs(overlap_guess-poly_min)<=guess_variance-3:
        overlap_output = int(poly_min)
        print("    optimal overlap found: %s pixels" % int(poly_min))
    else:
        overlap_output = 0
        print("    optimal overlap not found")

    # Plot graph of the overlap points and the curve fit
    if graph==True:
        # Plot a graph showing the overlap_metric as a function of overlap
        xp = np.linspace(np.min(amount_of_overlap), np.max(amount_of_overlap), 20)
        yp = (quadratic_fit[0]*(xp**2))+(quadratic_fit[1]*xp)+quadratic_fit[2]
        plt.plot(xp, yp, '--')
        
        plt.scatter(amount_of_overlap, overlap_metrics)
        plt.ylim(float(np.min(overlap_metrics)), float(np.max(overlap_metrics)))
        plt.show()
        
    return overlap_output

#######    MAIN CODE    #######   


### SECTION 1) Things that currently need to be defined by the user of the program

scan_number = 63
file_path = '/dls/i06/data/2019/cm22966-3/processing/optical_microscope/lab44-63.nxs'


### SECTION 2) Get the images data and scan metadata

# Get the file path of the .nxs file containing the image metadata
print("1) Finding image folder path")
folder_path = file_path.split("/lab44")[0]
image_data_path = folder_path + "/" + str(scan_number) + "_pcsscamImage"
print("    image folder path is: %s" % image_data_path)

print("2) Finding the image files in the .tif data folder")
files_list = List_files(image_data_path, ".tif")

# Find the scan command entered into GDA used to collect the image data
print("3) Finding scan command")
scan_command = Get_scan_command(file_path)
print("    scan command is: %s" % scan_command)


### SECTION 3) Definitions of parameters from the scan command and other hardware parameters

# Define the initial calibration for how many pixels in the image represent a mm of travel 
# for the motors
x_axis_pixels_per_mm = 4890     #pixels/mm
y_axis_pixels_per_mm = 4890     #pixels/mm

# Get the number of images per column and images per row for the particular scan being analysed
print("4) Calculating the dimensions of the image stitch")
x_motor_positions, y_motor_positions = Get_scan_motor_positions(file_path)
im_per_row = len(x_motor_positions)
im_per_col = len(y_motor_positions)
print("    images per column: %s images" % (im_per_col))
print("    images per row:    %s images" % (im_per_row))

print("5) Calculating scan steps in x and y axis")
x_axis_scan_movement = abs(x_motor_positions[0]-x_motor_positions[1]).round(5)
y_axis_scan_movement = abs(y_motor_positions[0]-y_motor_positions[1]).round(5)
print("    motor step in x axis: %s" % (x_axis_scan_movement))
print("    motor step in y axis: %s" % (x_axis_scan_movement))

# Guess the necessary amount of overlap to align the images
print("6) Estimating the required image overlap amounts")
x_overlap_guess = cam_x_resolution-((x_axis_scan_movement/x_axis_fov_mm)*cam_x_resolution)
y_overlap_guess = cam_y_resolution-((y_axis_scan_movement/y_axis_fov_mm)*cam_y_resolution)
print("    x axis overlap guess: %s pixels" % int(x_overlap_guess))
print("    y axis overlap guess: %s pixels" % int(y_overlap_guess))


### SECTION 4) Calculation of optimal overlap value for y axis
# Set the initial overlap guess
overlap_guess = int(y_overlap_guess)

# During optimisation the size of the overlap guess is varied to find the optimal overlap.
# The 'guess_variance' defines the range of values either side of the initial overlap_guess to test
guess_variance = 12

# Create an array to store the overlap values once calculated.
# This array is one smaller than the number of images per column,
# since for every two images there is only one overlap value
overlap_vals = np.zeros((im_per_col-1, im_per_row))

# Set the initial image number to be analysed
image_number = -1

# Iterate over all columns of the scan
print("7) Optimising the y axis overlap value")
print("    stitching images vertically")
for col in range(0, im_per_row):
    image_number += 1
    
    # Iterate over all rows of the scan
    for row in range(0, im_per_col-1):
        print("Testing column %s of %s, row %s of %s" % (col, im_per_col, row, im_per_row))
        
        # Read in the two images to be compared
        im_1 = plt.imread(files_list[image_number])
        im_2 = plt.imread(files_list[image_number+1])
        
        graph = False
        overlap_output = Perform_overlap_test(im_1, im_2, cam_y_resolution, cam_x_resolution, files_list, overlap_guess, guess_variance, graph, 0)
        overlap_vals[row, col] = int(overlap_output)
        image_number += 1
        
# Calculate the mean optimal overlap amount
y_overlap_optimised = overlap_vals[np.nonzero(overlap_vals)].mean()
print(overlap_vals)


### SECTION 5) Calculation of optimal overlap value for x axis

# Set the initial overlap guess and the range of values either side of this to test
overlap_guess = int(x_overlap_guess)
guess_variance = 12

# Create an array to store the overlap values once calculated
overlap_vals = np.zeros((im_per_col, im_per_row-1))

# Set the initial image number to be analysed
image_number = 0

# Iterate over all columns of the scan
print("8) Optimising the x axis overlap value")
print("    stitching images horizontally")
for col in range(0, im_per_row-1):
    
    # Iterate over all rows of the scan
    for row in range(0, im_per_col):
        print("Testing column %s of %s, row %s of %s" % (col, im_per_col, row, im_per_row))
        
        # Read in the two images to be compared
        im_1 = plt.imread(files_list[image_number])
        im_2 = plt.imread(files_list[image_number+im_per_col])
        
        graph = False
        overlap_output = Perform_overlap_test(im_1, im_2, cam_y_resolution, cam_x_resolution, files_list, overlap_guess, guess_variance, graph, 1)
        overlap_vals[row, col] = int(overlap_output)
        image_number += 1


### SECTION 6) Calculation and printing of results
x_overlap_optimised = overlap_vals[np.nonzero(overlap_vals)].mean()
print(overlap_vals)

x_axis_pixels_per_mm_new = int((cam_x_resolution-x_overlap_optimised)/x_axis_scan_movement)
y_axis_pixels_per_mm_new = int((cam_y_resolution-y_overlap_optimised)/y_axis_scan_movement)

# Print results of optimisation
print("Optimised overlap value for y axis is: %s " % int(y_overlap_optimised))
print("Optimised overlap value for x axis is: %s " % int(x_overlap_optimised))

print("y axis pixels per mm new value is: %s " % y_axis_pixels_per_mm_new)
print("x axis pixels per mm new value is: %s " % x_axis_pixels_per_mm_new)
                                                                                                                                                                                                                                                                                                                                       