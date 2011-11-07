
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
    
    
6. To scan the sample stage using a list of numbers given in a 2 column file
    a)First load the file into oan object that will provider the positions for the scan command

    two_motor_positions.load(filepath, offset, scale)
    e.g.
    two_motor_positions.load("/dls_sw/i13-1/scripts/ptychography/ProbePos_10x10.txt", (1.,2.), 1.0)
    
    b)scan the stage stage t1_xy
    
    scan t1_xy two_motor_positions <det> <exposure>
    
    
 To create tiff files from the edf files produce in a scan use the command:
 >>>file_converter.create_tiffs("/dls/i13-1/data/2011/mt5659-1/490.nxs")
"""


