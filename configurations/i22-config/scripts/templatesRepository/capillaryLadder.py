
# List the sample positions in terms of base_x. Using this line also allows you to include a title for storing with data

samples= {  
               5.5   : "Buffer",
              10.5   : "ATB",
              15.5    : "12 nm",
              20.5   : "12 nm + ATB",
              25.5   : "40 nm",
              30.5   : "40 nm + ATB",
              35.5   : "20 nm",
              40.5   : "20 nm + ATB"}

print "Start collecting data"

positions=samples.keys()

# This will sort the sample positions so that there is an efficient order for them even if they have not been listed that way
positions.sort()
# The loop below controls movement and data collection
for position in positions:
    sample=samples[position]
    print "Position: "+position.__str__()+"  -- Sample: "+sample
    setTitle(sample)
    pos pxy_y position
    # This line collects x-ray data but also records base_x position and beamstop diode readings for display
    staticscan ncddetectors pxy_y bs1diode


print "Script done"