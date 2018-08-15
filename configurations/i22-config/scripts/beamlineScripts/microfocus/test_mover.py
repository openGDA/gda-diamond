# This script will carry out repeated raster scans of a sample, each time going back to a reference location
# and carrying out a reassessment of beam location

#These are the locations found previously for the edge scans of the "Reference" cross,
# i.e. where the "reference" cross blocks half the beam in both directions

Ref_x = -2.9170
Ref_y = -2.2839

#These are the locations found previously for the centre of the sample,
# In our test case where the "sample" cross completely blocks the beam in both directions

Sample_x = -2.0447
Sample_y = -2.2056

# Move stages to centre of beam on "Reference" cross

move_x = Ref_x-Sample_x
move_y = Ref_y-Sample_y

inc mfstage_x move_x
inc mfstage_y move_y