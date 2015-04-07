
# List the sample positions in terms of base_x. Using this line also allows you to include a title for storing with data

samples= {  
             -86.0   : "1_water",
             -84.0   : "2_water",
             -82.0   : "3_water",
             -80.0   : "4_BMP2bfr",
             -78.1   : "5_BMP2",
              35.1   : "6_BMP2bfr",
              20.1   : "7_water",
               5.1   : "8_water",
              -9.8   : "9_water",
             -24.8   : "10_CHDbfr",
             -39.9   : "11_CHD",
             -54.9   : "12_CHDbfr",
                                    }

print "Start collecting data"

positions=samples.keys()

# This will sort the sample positions so that there is an efficient order for them even if they have not been listed that way
positions.sort()
# The loop below controls movement and data collection
for position in positions:
    sample=samples[position]
    print "Position: "+position.__str__()+"  -- Sample: "+sample
    setTitle(sample)
    pos base_y position
    # This line collects x-ray data but also records base_x position and beamstop diode readings for display
    staticscan ncddetectors base_y bsdiode


print "Script done"