"""
Beamline i12

This is the brief help for i12:

Please see the relevant web pages on Confluence for more details:
http://confluence.diamond.ac.uk/display/I12Tech/I12+GDA+Help

1. If your GDA Client fails to start, please try the following Linux terminal command:
    gdaclient --reset

2. Basic Jython commands relating to your scan directory:
    wd     to output the path to the current working directory, e.g. /dls/i12/data/2013/cm5936-1/rawdata/
    pwd    to output the path of the current working scan directory, e.g. /dls/i12/data/2013/cm5936-1/rawdata/14010/
    cfn    to output the ID (number) of the current scan, e.g. 14010
    nwd    to output the path to the next working scan directory, e.g. /dls/i12/data/2013/cm5936-1/rawdata/14011/
    nfn    to output the ID (number) of the next scan, e.g. 14011

3. To perform a scan, please use the following type of Jython console command:
    scan scannable start end step      e.g. scan ix 1 11 5
    scan scannable list_of_positions   e.g. scan ix (1,2,4,5,6,5,4,3,2,1)

4. To save data to a un-archived directory, please use your visit's tmp sub-directory. 

5. To reload lookup tables, please use the following Jython console commands: 
    reloadModuleLookup
    reloadCameraMotionLookup
    reloadTiltBallPositionLookup
    reloadScanResolutionLookup



"""