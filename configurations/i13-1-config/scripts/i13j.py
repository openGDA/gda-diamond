
"""
I13-1

This is the help for I13 Coherence branch:


Scans are recorded in the visit folder given by VisitPath.getVisitPath()


mpx_set_folder 

To take an image from the maxipix detector:

1. Set the folder, prefix and next number for the images. The folder is relative to the visit folder.
    e.g.mpx_set_folder("","sampleA",0)

2. Take an image with the maxipix detector
    pos mpx 1.
    
    The 1. is the exposure time
    
3. To read the threshold
    pos mpx_threshold

4. To change the threshold 
    pos mpx_threshold nnn

    To change the intergap fillmode
    >>>mpx_maxipix.setFillMode(MaxiPix2.FillMode.ZERO)
    >>>mpx_maxipix.setFillMode(MaxiPix2.FillMode.RAW)
    >>>mpx_maxipix.setFillMode(MaxiPix2.FillMode.DISPATCH)
    >>>mpx_maxipix.setFillMode(MaxiPix2.FillMode.MEAN)
    
    To change external trigger mode
    mpx_limaCCD.setAcqTriggerMode(LimaCCD.AcqTriggerMode.EXTERNAL_TRIGGER)
    
    To use the internal clock of the MaxiPix to take many images per step of a GDA scan
    >>>mpx_limaCCD.setAcqMode(LimaCCD.AcqMode.SINGLE)
    >>>mpx.setNumberOfFrames(100)
    >>>repscan 10 mpx .005

    This will results in 10 acquisitions, each consisting of 100 frames each 0.005 s apart. 
    There will be 10 lines of output on the GDA terminal    

    To write all images per acquisition into a single edf file set the parameter savingframePerFile to match the number of frames:
    Note that the data is not yet viewable in GDA or DAWN from a multi-image edf file.

    >>>mpx_limCCD.savingFramePerFile=100

    To reset the mpx to normal settings use the command mpx_reset_configure()

    
5. To scan a variable and at each point take an image form the maxipix    
    scan ix 0. 10. 1 mpx 0.1
    
    This scans the dummy variable ix from 0 to 10 in steps of 1 and at each takes an image using exposure time = 0.1s

    
    
6. To scan the sample stage using a list of numbers given in a 2 column file
    a)First load the file into oan object that will provider the positions for the scan command

    two_motor_positions.load(filepath, offset, scale)
    e.g.
    two_motor_positions.load("/dls_sw/i13-1/scripts/ptychography/ProbePos_10x10.txt", (1.,2.), 1.0)

    You can use command ( run "spiral.py") to generate a set of positions to describe a spiral in /dls_sw/i13-1/scripts/spiral.txt
	The file is at /dls_sw/i13-1/scripts/spiral.py    

    b)To scan the sample stage t1_sxy use the command:
    
    scan t1_sxy two_motor_positions <det> <exposure> 
    
    
6.1 To perform a STXM and plot the results as an image:
    scan t1_sx t1_sx()-5 t1_sx()+5 1 t1_sy t1_sy()-5 t1_sy()+5 1 mpx_wrap .1 t1_sxy_plotter
    [By default t1_sxy_plotter plots the field 'total' which is available by enabling imageStats
    You can change the field to be plotted using the call t1_sxy_plotter.setZ_colName("total")]
     

 
    
 To create tiff files from the edf files produce in a scan use the command:
 >>>file_converter.create_tiffs("/dls/i13-1/data/2011/mt5659-1/490.nxs")
 
7. To control the detector robot
    a)create the detector object
    import robots
    robot1=robots.Robot(ip="172.23.82.221")

    b)Send home. You will need to call gotoHome2 and resetAlarm several times. Continue until robot1.getPulses returns a list of 0's
    robot1.gotoHome2()
    robot1.resetAlarm()

    c)When homed tell the robot object to reset its internal value for the robot position
    robot1.resetPosition()

    d) You can query the internal value for the robot position by calling getPosition
    robot1.getPosition()

    e.1)To change the position first take a copy of the current position. 
    posn=robot1.getPosition()

    e.2)Change posn to the destination. # options posn.X, posn.Y, posn.Z, posn.RX posn.RY, posn.RZ
    e.g. posn.X=1000

    e.3)Make the robot move by calling the method moveTo with the required position
    robot1.moveTo(posn)

    N.B Once it has moved it will have set user frame to the current detector frame
    so you can then only move further about Y by changing posn.Y and calling moveTo
    
    If you do not want to adjust the user frame then use the command moveToDoNotSetUserCoords instead of moveTo after resetPostion
    robot1.moveToDoNotSetUserCoords(posn)
    
    
    #to calculate the position of the detector robot for a certain theta, phi use the command:
    robots.getDetectorRobotPositionFromThetaPhi(theta=45, phi=0)
    
    to get help on this function type
    
    help robots.getDetectorRobotPositionFromThetaPhi
    
    This will return an object in the same form as return by the getPosition method and used by the moveTo method.

8. To perform a flyscan:
    to perform a flyscan of scannable tx over range start, stop, end and measure detector d at each approx value of tx
    >flyscan   flyscannable(tx) start stop end d
    
    to perform a flyscan as the inner most scan of a nested scan
    e.g. perform a scan of ty over range ystart, ystop, ystep and at each value of ty perform the above flyscan of tx
    >flyscan   ty ystart ystop ystep flyscannable(tx) start stop end d
    
    
9.  EPICS
    >caput pv value  e.g. caput "BL13J-OP-ACOLL-01:AVERAGESIZE" 10.0
    >caget pv        e.g. caget "BL13J-OP-ACOLL-01:AVERAGESIZE"
    
    To make a scannable for a pv
    createPVScannable name, pv  e.g. createPVScannable "d1_total" "BL13J-DI-PHDGN-01:STAT:Total_RBV"
                                     Will make scannable d1_total
10. SCANNING
    >scan scannable start end step      e.g. scan ix 1 10 1
    >scan scannable list_of_positions   e.g. scan ix (1,2,4,5,6,5,4,3,2,1)

11. Read total count in region of interest for mpx
    Use detector mpx_wrap
    >imageStats.setEnable(True)
    >imageROI.setEnable(True)
    >imageROI.setROI(366,511,231,511)  ( y_start, y_end, x_start, x_end)
    >repscan 1 mpx_wrap 1

	Equivalent 'wrapped' detectors exist for:
	Diagnostic stick 1 camera - d1_cam
	Diagnostic stick 2 camera - d2_cam
	Diagnostic stick 3 camera - d3_cam
	Diagnostic stick 4 camera - d4_cam
    optics hutch shutter camera - oh4_shtr_cam
	PCO4000 - pco1
	sample stage camera - sample_stage_cam

    imageFitter must be enabled to make the cameras report the result of fitting the image to a 2d gaussian
	
    NOTE. After enabling or disabling imageStats or imageFitter can the command rescanProcessors on the detector:
	e.g. d4_cam.rescanProcessors()


11b Region of Interest Support for maxipix

    mpx_wrap supports  2 region of interests imageROI and imageROI2. These report the average and total of counts over the ROI
    
    mpx is also supported by scannables that reports the difference between the two regions of interest
    
    repscan 5 mpx_wrap .1 mpx_roi_average_diff mpx_roi_total_diff

12. Beammonitor
    To pause the scan if the value of a scannable goes below a minimum threshold add the scannable beammonitor to a scan command
    e.g. scan ix 0 10 1 beammonitor
    
    To view the scannable being monitored :
    >beammonitor.scannableToMonitor
    ( To change use a command of the form: beammonitor.scannableToMonitor = d3_i)
    
    To view the minimum value below which the scan pauses:
    >beammonitor.minimumThreshold

    (To change use a command of the form: beammonitor.minimumThreshold = .1)
    
    
13. repscan 10 random_move_scannable.CreateRandomMoveScannable(ix, [(0,10)]) 1 ix iy
    
14. To set a title to be recorded in the scan file use the command:
    >setTitle xxxx

    To view the current title use the command:
    >getTitle


15. To change the folder into which the data is written use the command:
    >LocalProperties.set(LocalProperties.GDA_DATAWRITER_DIR, "/dls/$instrument$/data/$year$/$visit$/" + <folder>)


16. To perform a tomogram:
    >tomographyScan.tomoScan(inBeamPosition, outOfBeamPosition, exposureTime=1, start=0., stop=180., step=0.1, darkFieldInterval=0., flatFieldInterval=0.,
              imagesPerDark=20, imagesPerFlat=20, min_i=-1.):
    
   where:
    inBeamPosition - position of X drive to move sample into the beam to take a projection
    outOfBeamPosition - position of X drive to move sample out of the beam to take a flat field image
    exposureTime - exposure time in seconds ( default = 1)
    start - first rotation angle ( default=0.)
    stop  - last rotation angle (default=180.)
    step - rotation step size (default = 0.1)
    darkFieldInterval - number of projections between each dark field. Note that a dark is always taken at the start and end of a tomogram (default=0.)
    flatFieldInterval - number of projections between each flat field. Note that a dark is always taken at the start and end of a tomogram (default=0.)
    imagesPerDark - number of images to be taken for each dark
    imagesPerFlat - number of images to be taken for each flat
    min_i - minimum value of ion chamber current required to take an image (default is -1 . A negative value means that the value is not checked )


17. Vortex detector
    this is represented in gda as xmapMca
    Edit the regions of interest in /dls_sw/i13-1/software/gda_versions/var/Vortex_Parameters.xml  and then in gda
    There are 4 elements to the detector, each with its own set of ROI, each ROI is defined by its windowStart and windowEnd value
    
        <DetectorElement>
        <name>Detector1</name>
        <number>0</number>
        <ROI>
            <name>ROI1</name>
            <windowStart>1</windowStart>
            <windowEnd>500</windowEnd>
        </ROI>
        <ROI>
            <name>ROI2</name>
            <windowStart>501</windowStart>
            <windowEnd>600</windowEnd>
        </ROI>        
        </DetectorElement>
    
    Save the changes.
    Enter the command:
    >xmapMca.loadConfigurationFromFile()
    
    Then use in an scan e.g. >repscan 10 xmapMca 2   ( to take 10 measurements of 2 seconds exposure each)
    

18 How to generate a train of triggers from the tfg
    >import tfg_commands
    >tfg_commands.sendSimplyTrigger()
    
    Type help tfg_commands.sendSimplyTrigger for full details of the command
    
19. To use PCO Edge for effective exposure times greater than 2s
    Turn on accumulation mode:
    >pco1_sw_hdf_nochunking.collectionStrategy.accumlationMode=True
    Set  exposure for the individual images that are to be accumulated together at each point
    >pco1_sw_hdf_nochunking.collectionStrategy.acc_expo_time=.1
    
    To get 1 accumulated image with effective exposure time of 4 s:
    >repscan 1 pco1_sw_hdf_nochunking 4

"""


