"""
Beamline i12

This is a brief help document for i12:

Please see the appropriate web pages on Confluence for more details:
http://confluence.diamond.ac.uk/display/I12Tech/I12+GDA+Help

1. To start GDA client if it fails to launch on the first attempt, execute:
    gdaclient --reset

2. To identify the path to your scan directory, please use the following Jython console commands:
    wd     to return the path to the current working directory, e.g. /dls/i12/data/2013/cm5936-1/rawdata/
    pwd    to return the path of the current working scan directory, e.g. /dls/i12/data/2013/cm5936-1/rawdata/14010/
    cfn    to return the ID (number) of the current scan, e.g. 14010
    nwd    to return the path to the next working scan directory, e.g. /dls/i12/data/2013/cm5936-1/rawdata/14011/
    nfn    to return the ID (number) of the next scan, e.g. 14011

3. To perform a simple scan in GDA, execute an appropriate command from the following list of examples:
    scan <scannable> <start> <end> <step> <detector> <exposure-time>
        e.g. scan ix 1 11 5 
        In the above example, scannable=ix, start=1, end=11, step=5.
    scan <scannable> <list-of-positions>
        e.g. scan ix (1,2,4,5,6,5,4,3,2,1)
        In the above example, scannable=ix, list-of-positions=(1,2,4,5,6,5,4,3,2,1)

4. If the Stop-All (round red) button is used to abort data acquisition, then one must wait until "!!!Stop-all complete" is displayed in the Jython console.
    However, it is recommended to use the Abort-all-running-commands-scripts-and-scans (square blue) button instead!

5. To save data to a non-archived (and periodically cleared) directory, please use your visit's tmp sub-directory, i.e. 
    /dls/i12/data/<year>/<science_code><proposal_number>-<visit_number>/tmp/. 
    For example, /dls/i12/data/2013/cm5936-1/tmp/. The command to use is: setSubdirectory("tmp").
    IMPORTANT: Please remember to set it back to the original location when appropriate, eg setSubdirectory("rawdata").

6. To view or change the type of data writer which is used when scanning, execute an appropriate command from the following list:
    getDataWriter
    setDataWriterToNexus
    setDataWriterToSRS

7. To reload a lookup table, execute an appropriate command from the following list: 
    reloadModuleLookup
    reloadCameraMotionLookup
    reloadTiltBallPositionLookup
    reloadScanResolutionLookup
    
    For completeness, the path to the directory containing lookup-table files is: /dls_sw/i12/software/gda/config/lookupTables/tomo_lookup

8. To identify the current mapping of objects which are used by tomoScan, execute:
    reportTomo 
    or 
    reportJythonNamespaceMapping

9. To view or modify the list of default objects whose values are recorded at each scan point of every step scan, execute:
    list_defaults.................to return the current content of the list of default scannables
    add_default <scannable>.......to add a given scannable to the list of default scannables
    remove_default <scannable>....to remove a given scannable from the list of default scannables

10. To close down the telnet connection for P2R, execute:
    p2r_rot.motor.smc.bidiAsciiCommunicator.closeConnection()

11. To run a fly scan using Zebra box, execute:
    i12tomoFlyScan(description="Hello World", inBeamPosition=0.0,outOfBeamPosition=1.0, exposureTime=.05, start=0.0, stop=180.0, step=0.1, imagesPerDark=20.0, imagesPerFlat=20.0, extraFlatsAtEnd=True, closeShutterAfterScan=False)

    Notes:
    (a) To display the readout time (sec) used by GDA, execute: 
        flyScanDetector.readOutTime
        (0.011s is routinely used for PCO Edge) 
    (b) To modify the readout time used by GDA, execute: 
        flyScanDetector.readOutTime=<new readout time in sec>
    (c) If the time/angle curve is not a straight line, then adjust zebraSM1.scurveTimeToVelocity

12. To start GDA log panel, execute: 
    gda_start_logpanel

13. To move between different camera modules, execute:
    tomoAlignment.moveToModule(<module_number>)
    where module_number = 1, 2, 3, or 4.

14. To display the pre-acquisition wait time (in msec, ie millisec) for Pilatus, execute:
    pilatus_eh1_sw_{tif | cbf}.getCollectionStrategy().getSleepMillis()
    To modify the pre-acquisition wait time for Pilatus, execute
    pilatus_eh1_sw_{tif | cbf}.getCollectionStrategy().setSleepMillis(<new readout time in millisec>)

15. To view or modify the list of default objects whose values are recorded once per scan, execute:
    meta_{ls | ll}.................to return the current content of the list of meta scannables
    meta_add <scannable>...........to add a given scannable to the list of meta scannables
    meta_rm <scannable>............to remove a given scannable from the list of meta scannables

"""
