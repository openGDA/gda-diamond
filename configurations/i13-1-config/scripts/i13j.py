
"""
I13-1

This is the help for I13:


Scans are recorded in the visit folder given by VisitPath.getVisitPath()


mpx_set_folder 

To take an image from the maxipix detector:

1. Set the folder and prefix for the images. The folder is relative to the visit folder.
    e.g.mpx_set_folder("","sampleA")

2. Take an image with the maxipix detector
    pos mpx 1.
    
    The 1. is the exposure time
    
3. To read the threshold
    pos mpx_threshold

4. To change the threshold 
    pos mpx_threshold nnn
    
5. To scan a variable and at each point take an image form the maxipix    
    scan ix 0. 10. 1 mpx 0.1
    
    This scans the dummy variable ix from 0 to 10 in steps of 1 and at each takes an image using exposure time = 0.1s
    
"""


