from gda.jython.commands import GeneralCommands
from gda.jython.commands import ScannableCommands
from i12utilities import wd, pwd, nwd, nfn, cfn
from gdascripts.metadata.metadata_commands import setTitle, getTitle
import i13tomographyScan 

from gda.factory import Finder
finder = Finder.getInstance()
p2r_rot=finder.find("p2r_rot")

def flyp2r(title, inBeamPosition, outOfBeamPosition, exposureTime=1., start=0., stop=180., step=0.1, imagesPerDark=20, imagesPerFlat=20, speedForRewind=180.0):
    """
    Function to perform a tomography FLY SCAN with p2r rotation rig. 
    Arguments:
    title - description of the scan or the sample that is being scanned. This is generally user-specific information that may be used to map to this scan later and is available in the NeXus file)
    inBeamPosition - position of X drive to move sample into the beam to take a projection
    outOfBeamPosition - position of X drive to move sample out of the beam to take a flat field image
    exposureTime - exposure time in seconds (default = 1.0)
    start - first rotation angle (default=0.0)
    stop  - last rotation angle (default=180.0)
    step - rotation step size (default = 0.1)
    imagesPerDark - number of images to be taken for each dark-field sub-sequence (default=20)
    imagesPerFlat - number of images to be taken for each flat-field sub-sequence (default=20)
    
    General scan sequence is: D, F, P,..., P
    where D stands for dark field, F - for flat field, and P - for projection.
    speedForRewind - speed to be temporarily used by p2r to go back to start angle (this speed is re-set to original value before scan is executed.
    """
    
    print("Starting flyp2r scan with arguments:")
    
    scanfile=nwd()
    scanfile += ".nxs"
    print "Scan file will be: %s"%scanfile
    
    print("title = " + title)
    print("inBeamPosition = " + `inBeamPosition`)
    print("outOfBeamPosition = " + `outOfBeamPosition`)
    print("exposureTime = " + `exposureTime`)
    print("start angle = " + `start`)
    print("stop angle = " + `stop`)
    print("step angle = " + `step`)
    print("imagesPerDark = " + `imagesPerDark`)
    print("imagesPerFlat = " + `imagesPerFlat`)
    print("speed for rewinding = " + `speedForRewind`)
    
    speedBefore = p2r_rot.getSpeed()
    print("speed before = " + `speedBefore`)
    
    print("About to set p2r_rot speed to temporary rewind speed:" + `speedForRewind`)
    p2r_rot.setSpeed(speedForRewind)
    print("Finished setting p2r_rot speed to temporary rewind speed:" + `speedForRewind`)
    
    speedUserModified1 = p2r_rot.getSpeed()
    print("p2r_rot speed after setting it to temporary rewind speed:" + `speedUserModified1`)
    
    print("About to set p2r_rot rotation angle to:" + `start` + " (with temporary rewind speed = "+`speedUserModified1`+")")
    p2r_rot.moveTo(start)
    print("Finished setting p2r_rot rotation angle to:" + `start`)
    
    posBeforeScan = p2r_rot.getPosition()
    print("p2r_rot rotation angle after setting it to start angle:" + `posBeforeScan`)
    
    print("About to re-set p2r_rot speed to original value:" + `speedBefore`)
    p2r_rot.setSpeed(speedBefore)
    print("Finished re-setting p2r_rot speed to original value:" + `speedBefore`)
    
    speedUserModified2 = p2r_rot.getSpeed()
    print("p2r_rot speed after re-setting it to original value:" + `speedUserModified2`)
    
    print("About to run tomoFlyScan...")
#    clear_defaults()
    setTitle(title)
    #tomoFlyScan(inBeamPosition, outOfBeamPosition, exposureTime=1, start=0., stop=180., step=0.1, darkFieldInterval=0., flatFieldInterval=0.,
    #          imagesPerDark=20, imagesPerFlat=20, min_i=-1., setupForAlignment=True, beamline="I13")
    
    i13tomographyScan.tomoFlyScan(inBeamPosition=inBeamPosition,outOfBeamPosition=outOfBeamPosition, exposureTime=exposureTime, start=start, stop=stop, step=step, imagesPerDark=imagesPerDark, imagesPerFlat=imagesPerFlat, beamline="I12")
    setTitle("undefined")
    print("Finished tomoFlyScan.")
    
    scanfile=pwd()
    print "Scan file was: %s"%scanfile

    print("Finished flyp2r scan")

def stepp2r(title, inBeamPosition, outOfBeamPosition, exposureTime=1., start=0., stop=180., step=0.1, darkFieldInterval=0, flatFieldInterval=0, imagesPerDark=20, imagesPerFlat=20, speedForRewind=180.0):
    """
    Function to perform a tomography STEP SCAN with p2r rotation rig. 
    Arguments:
    title - description of the scan or the sample that is being scanned. This is generally user-specific information that may be used to map to this scan later and is available in the NeXus file)
    inBeamPosition - position of X drive to move sample into the beam to take a projection
    outOfBeamPosition - position of X drive to move sample out of the beam to take a flat field image
    exposureTime - exposure time in seconds (default = 1.0)
    start - first rotation angle (default=0.0)
    stop  - last rotation angle (default=180.0)
    step - rotation step size (default = 0.1)
    darkFieldInterval - number of projections between each dark-field sub-sequence. NOTE: at least 1 dark is ALWAYS taken both at the start and end of a tomogram (default=0: use this value if you DON'T want to take any darks between projections)
    flatFieldInterval - number of projections between each flat-field sub-sequence. NOTE: at least 1 flat is ALWAYS taken both at the start and end of a tomogram (default=0: use this value if you DON'T want to take any flats between projections)
    imagesPerDark - number of images to be taken for each dark-field sub-sequence (default=20)
    imagesPerFlat - number of images to be taken for each flat-field sub-sequence (default=20)
    
    General scan sequence is: D, F, P,..., P, F, D
    where D stands for dark field, F - for flat field, and P - for projection.
    speedForRewind - speed to be temporarily used by p2r to go back to start angle (this speed is re-set to original value before scan is executed.
    """
    
    print("Starting stepp2r scan with arguments:")
    
    scanfolder=nwd()
    print "Scan folder will be: %s"%scanfolder
    
    print("title = " + title)
    print("inBeamPosition = " + `inBeamPosition`)
    print("outOfBeamPosition = " + `outOfBeamPosition`)
    print("exposureTime = " + `exposureTime`)
    print("start angle = " + `start`)
    print("stop angle = " + `stop`)
    print("step angle = " + `step`)
    print("darkFieldInterval = " + `darkFieldInterval`)
    print("flatFieldInterval = " + `flatFieldInterval`)
    print("imagesPerDark = " + `imagesPerDark`)
    print("imagesPerFlat = " + `imagesPerFlat`)
    print("speed for rewinding = " + `speedForRewind`)
    
    speedBefore = p2r_rot.getSpeed()
    print("speed before = " + `speedBefore`)
    
    print("About to set p2r_rot speed to temporary rewind speed:" + `speedForRewind`)
    p2r_rot.setSpeed(speedForRewind)
    print("Finished setting p2r_rot speed to temporary rewind speed:" + `speedForRewind`)
    
    speedUserModified1 = p2r_rot.getSpeed()
    print("p2r_rot speed after setting it to temporary rewind speed:" + `speedUserModified1`)
    
    print("About to set p2r_rot rotation angle to:" + `start`+ " (with temporary rewind speed = "+`speedUserModified1`+")")
    p2r_rot.moveTo(start)
    print("Finished setting p2r_rot rotation angle to:" + `start`)
    
    posBeforeScan = p2r_rot.getPosition()
    print("p2r_rot rotation angle after setting it to start angle:" + `posBeforeScan`)
    
    print("About to re-set p2r_rot speed to original value:" + `speedBefore`)
    p2r_rot.setSpeed(speedBefore)
    print("Finished re-setting p2r_rot speed to original value:" + `speedBefore`)
    
    speedUserModified2 = p2r_rot.getSpeed()
    print("p2r_rot speed after re-setting it to original value:" + `speedUserModified2`)
    
    print("About to run tomoScan...")
#    for s in _default_scannables_i12:
#        add_default(s)
    
    #tomoScan(description, inBeamPosition, outOfBeamPosition, exposureTime=1.0, start=0.0, stop=180.0, step=0.1, darkFieldInterval=0, flatFieldInterval=0, imagesPerDark=10, imagesPerFlat=10, optimizeBeamInterval=0, pattern='default', tomoRotationAxis=0, addNXEntry=True, autoAnalyse=True, additionalScannables=[])
    tomoScan(description=title,inBeamPosition=inBeamPosition,outOfBeamPosition=outOfBeamPosition, exposureTime=exposureTime, start=start, stop=stop, step=step, darkFieldInterval=darkFieldInterval, flatFieldInterval=flatFieldInterval, imagesPerDark=imagesPerDark, imagesPerFlat=imagesPerFlat)
    print("Finished tomoScan.")
    setTitle("undefined")
    
    scanfolder=pwd()
    print "Scan folder was: %s"%scanfolder
    
    print("Finished stepp2r scan")




