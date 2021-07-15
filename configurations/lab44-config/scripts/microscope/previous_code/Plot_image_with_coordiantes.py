# -*- coding: utf-8 -*-

'''
    File name: Plot_image_with_coordinates.py
    Author: xke49157
    Affiliation: Diamond Light Source
    Date created: 02/08/2019
    Python Version: 2.7

    CODE OUTLINE
        This program uses the matplotlib plotting library to display a stitched image
        with the PEEM or PCSS motor co-ordinates overlayed.

    HOW TO USE THIS CODE
        1) Set the scan number and file path to the nxs file
        2) Run the code
        3) Choose 'A' or 'B' to plot PEEM or PCSS coordinates respectively
        4) Wait for image window to pop up
        5) When navigating the image with the cursor, the motor co-ordinates in mm for
           the x and y axis can be read off from the bottom left corner of the window

    '''
    
# Import relevant packages and utilities
import os
import numpy as np
from numpy import genfromtxt
import matplotlib
import matplotlib.pyplot as plt
from utilities  import *

scan_number = 63
file_path = '/dls/i06/data/2019/cm22966-3/processing/optical_microscope/lab44-63.nxs'

# Ask user to decide between PEEM and PCSS co-ordinates
while True:
    input = raw_input("Do you want to: A) Plot image with PCSS co-ordinates. B) Plot image with PEEM co-ordinates. [A/B]? : ")
    # check if input is equal to one of the strings, specified in the list
    if input in ['A', 'B']:
        # if it was equal - break from the while loop
        break

# process the input
if input == "A": 
    print("Getting co-ordinates for PEEM image")
    extent_vals = Get_PEEM_motor_coords_for_image(file_path, scan_number)
elif input == "B": 
    print("Getting co-ordinates for PCSS image")
    extent_vals = Get_PCSS_motor_coords_for_image(file_path, scan_number)

### Plot the stitched image

# Load in the stitched image array
folder_path = file_path.split("/lab44")[0]
image_data_path = folder_path + "/" + str(scan_number) + "_pcsscamImage"
files_list = List_files(image_data_path, ".npy")

# Load in the stitched image to plot
final_image = np.load(files_list[0])

# Change default colour map to 'jet'
matplotlib.rc('image', cmap='jet')

# Plot figure
print("Plotting stitched image with co-ordinates")
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.imshow(final_image, interpolation='none', extent=extent_vals, aspect=1)
plt.show()
