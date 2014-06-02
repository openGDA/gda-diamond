"""
Beamline i12

This is the brief help for i12:

Please see the appropriate web pages on Confluence for more details:
http://confluence.diamond.ac.uk/display/I12Tech/I12+GDA+Help

1. To start GDA client if it fails to launch on the first attempt, please try the following Linux terminal command:
    gdaclient --reset

2. To identify the path to your scan directory, please use the following Jython console commands:
    wd     to return the path to the current working directory, e.g. /dls/i12/data/2013/cm5936-1/rawdata/
    pwd    to return the path of the current working scan directory, e.g. /dls/i12/data/2013/cm5936-1/rawdata/14010/
    cfn    to return the ID (number) of the current scan, e.g. 14010
    nwd    to return the path to the next working scan directory, e.g. /dls/i12/data/2013/cm5936-1/rawdata/14011/
    nfn    to return the ID (number) of the next scan, e.g. 14011

3. To perform a simple scan in GDA, please use an appropriate Jython console command from the following list of examples:
    scan <scannable> <start> <end> <step> <detector> <exposure-time>
        e.g. scan ix 1 11 5 
        In the above example, scannable=ix, start=1, end=11, step=5.
    scan <scannable> <list-of-positions>
        e.g. scan ix (1,2,4,5,6,5,4,3,2,1)
        In the above example, scannable=ix, list-of-positions=(1,2,4,5,6,5,4,3,2,1)

4. If the Stop-All (red) button is used to abort data acquisition, then one must wait until "!!!Stop-all complete" is displayed in the Jython console.

5. To save data to a non-archived (and periodically cleared) directory, please use your visit's tmp sub-directory, i.e. 
    /dls/i12/data/<year>/<science_code><proposal_number>-<visit_number>/tmp/. 
    For example, /dls/i12/data/2013/cm5936-1/tmp/.
    IMPORTANT: Please remember to set it back to the original location when appropriate.

6. To view or change the type of data writer which is used when scanning, please use an appropriate Jython command from the following list:
    getDataWriter
    setDataWriterToNexus
    setDataWriterToSRS

7. To reload a lookup table, please use an appropriate Jython console command from the following list: 
    reloadModuleLookup
    reloadCameraMotionLookup
    reloadTiltBallPositionLookup
    reloadScanResolutionLookup
    
    For completeness, the path to the lookup-table files: /dls_sw/i12/software/gda/config/lookupTables/tomo

8. To identify the current mapping of objects which are used by tomoScan, please use the following Jython command:
    reportTomo 
    or 
    reportJythonNamespaceMapping

9. To view or modify the list of default objects whose values are recorded at each scan point of every scan, please use an appropriate Jython command from the following list:
    list_defaults.................to return the current content of the list of default scannables
    add_default <scannable>.......to add a given scannable to the list of default scannables
    remove_default <scannable>....to remove a given scannable from the list of default scannables

10. To close down the telnet connection for P2R, please use the following Jython console command:
    p2r_rot.motor.smc.bidiAsciiCommunicator.closeConnection()

11. flyscanning using zebra
    clear_defaults
    import i13tomographyScan
    i13tomographyScan.tomoFlyScan(description="Hello World", inBeamPosition=0.,outOfBeamPosition=1., exposureTime=.05, start=0., stop=180., step=.1, imagesPerDark=0, imagesPerFlat=0, extraFlatsAtEnd=False, closeShutterAfterScan=False, beamline="I12")

    (If the time/angle curve is not a straight line then adjust zebraSM1.scurveTimeToVelocity)

"""