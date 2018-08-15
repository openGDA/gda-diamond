# This script will carry out repeated raster scans of a sample, each time going back to a reference location
# and carrying out a reassessment of beam location

# These are the locations found previously for the edge scans of the "Reference" cross,
# i.e. where the "reference" cross blocks half the beam in both directions

Ref_x = -2.9170
Ref_y = -2.2839

# These are the locations found for the centre of the sample, The script presupposes this is
# the last thing you do before starting the script

# This point is taken as where the "sample" cross completely blocks the beam in both directions in our test case

Sample_x = -2.0447
Sample_y = -2.2056

# Move stages to centre of beam on "Reference" cross

move_x = Ref_x-Sample_x
move_y = Ref_y-Sample_y

inc mfstage_x move_x
inc mfstage_y move_y

# do the full experiment X times defined below

for count in range (30):
# Find the new edges if they have changed
    pos mfstage_z 5.1642
    staticscan mfgige
    inc mfstage_y -0.03
    rscan mfstage_x -0.015 0.015 0.001 topup mfbsdiode
    position_x = edge.result.pos
    go edge
    inc mfstage_x -0.03
    
    inc mfstage_y 0.03
    rscan mfstage_y -0.015 0.015 0.001 topup mfbsdiode
    position_y = edge.result.pos
    go edge
    inc mfstage_x 0.03
    staticscan mfgige
        
# move to sample position
    out_x = Sample_x-position_x
    out_y = Sample_y-position_y
    inc mfstage_x out_x
    inc mfstage_y out_y
    Sample_x = mfstage_x.getPosition()
    Sample_y = mfstage_y.getPosition()

    
# This is the gridscan bit
    pos mfstage_z 5.3130
    staticscan mfgige
    rscan mfstage_x -0.020 0.020 0.002 mfstage_y -0.020 0.020 0.002 topup mfbsdiode
    
# This takes the stages back to the reference cross
    back_x = -out_x
    back_y = -out_y
    inc mfstage_x back_x
    inc mfstage_y back_y
    pos mfstage_z 5.1642


print "script finished"
