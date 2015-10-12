
"""
I13

This is the help for I13:


Scans are recorded in the visit folder given by VisitPath.getVisitPath()



See http://confluence.diamond.ac.uk/display/BLXIIII/I13+Data+Acquisition+User+Guide for detailed help on using I13I

1. To perform a flyscan:
    to perform a flyscan of scannable tx over range start, stop, end and measure detector d at each approx value of tx
    >flyscan   flyscannable(tx) start stop end d
    
    to perform a flyscan as the inner most scan of a nested scan
    e.g. perform a scan of ty over range ystart, ystop, ystep and at each value of ty perform the above flyscan of tx
    >flyscan   ty ystart ystop ystep flyscannable(tx) start stop end d
    
    To perform a flyscan of the id gap use the command:
    >flyscan flyscannable(id_gap, id_gap_rbv) 20. 23. .01 ionc_i
    If id_gap_nominal does not keep up with id_gap_rbv then reduce the speed of the id gap motor


    
2.  EPICS
    >caput pv value  e.g. caput "BL13J-OP-ACOLL-01:AVERAGESIZE" 10.0
    >caget pv        e.g. caget "BL13J-OP-ACOLL-01:AVERAGESIZE"
    
    To make a scannable for a pv
    createPVScannable name, pv  e.g. createPVScannable "d1_total" "BL13J-DI-PHDGN-01:STAT:Total_RBV"
                                     Will make scannable d1_total
3. SCANNING
    >scan scannable start end step      e.g. scan ix 1 10 1
    >scan scannable list_of_positions   e.g. scan ix (1,2,4,5,6,5,4,3,2,1)
    
4. Configuring the PCO camera for alignment
    >tomodet.setupForAlignment( exposureTime=.1, scale=2)


5. To get a normalised image:  (image-dark)/(flat-dark):
    >tomographyScan.showNormalisedImage(outOfBeamPosition, exposureTime=1):
   where:
    outOfBeamPosition - position of X drive to move sample out of the beam to take a flat field image
    exposureTime - exposure time in seconds ( default = 1)
    
    
5. To perform a tomogram:
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

   At each rotation angle a number of images will be taken for different sample_x motor positions
   For now these are controlled by values in /dls_sw/i13/software/gda/config/scripts/beamlineParameters:
       tomography_sample_x_step=25
       sample_x_number_of_points=1    
   and the sample_x motor is defined in /dls_sw/i13/software/gda/config/scripts/live_jythonnamespacemapping:
       tomography_sample_x=ss1_x

5a To perform a tomogram using flyscan
    >tomographyScan.tomoFlyScan(inBeamPosition, outOfBeamPosition, exposureTime=1, start=0., stop=180., step=0.1, darkFieldInterval=0., flatFieldInterval=0.,
              imagesPerDark=20, imagesPerFlat=20, min_i=-1)
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

6. To perform a raster_scan
    >help raster_scan.scan
    
7.  To save data to a unarchived folder 
    > LocalProperties.set("gda.data.scan.datawriter.datadir", "/dls/$instrument$/data/$year$/$visit$/tmp")
    NB Set it back to the default afterwards:
    > LocalProperties.set("gda.data.scan.datawriter.datadir", "/dls/$instrument$/data/$year$/$visit$/raw")
    
8.  How to close down the telnet for P2R
    > p2r_rot.motor.smc.simc.bidiAsciiCommunicator.closeConnection()
    
9.  How to set the ROI of the pco
    >tomodet.pco1_cam_base.minY=100
    >tomodet.pco1_cam_base.sizeY=500
    
10. Scannables for stroboscopic experiment: phase(in radians), frequency and amplitude

    To take mulitple images use detector pco1_multi_hdf
    Set exposure of each image by property pco1_multi_hdf.collectionStrategy.exposureTime
    To take a series of exposures at different phase with frame exposure time of 1microSec and total exposure of 1ms 
    >pco1_multi_hdf.collectionStrategy.exposureTime=1e-6
    >scan phase 0. .8 .1 pco1_multi_hdf 1e-3

    To take images without saving to file > pco1_multi_hdf.pluginList[1].enabled=False
    
11. To control whether the fast shutter is to be opened only during camera exposure see the comment on the setting for tomography_shutter in 
    /dls_sw/i13/software/gda/config/scripts/live_jythonNamespaceMapping
    
12. To use the fast shutter in a normal repscan of pco1_hw_hdf ( not a tomography scan) use the command:
    pco1_hw_hdf.collectionStrategy.useShutterPV=True
    
    
"""
