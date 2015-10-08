import os
from time import sleep
from gda.data import NumTracker
from gdascripts.messages import handle_messages
from gda.data import PathConstructor
from gda.factory import Finder
from gda.commandqueue import JythonCommandCommandProvider
from gdascripts.metadata.metadata_commands import setTitle, getTitle
import tomographyScan

print "Running i13i_utilities.py..."

# set up a nice method for getting the latest file path
i13iNumTracker = NumTracker("i13i")
finder = Finder.getInstance()

# to get working directory, eg /dls/i13/data/2015/cm12165-1/raw/
def wd():
    """
    Method to get working directory for the current visit in GDA
    """
    dir = PathConstructor.createFromDefaultProperty()
    return dir

# to get the current file (scan) number
def cfn():
    """
    Method to get the last file (scan) number used by GDA
    """
    filenumber = i13iNumTracker.getCurrentFileNumber()
    return filenumber

# to get the next file (scan) number
def nfn():
    """
    Method to get the next file (scan) number, eg 61192
    """
    filenumber = i13iNumTracker.getCurrentFileNumber()
    return filenumber + 1

# to get the last file path, eg /dls/i13/data/2015/cm12165-1/raw/61191
def pwd():
    """
    Method to get the last file path used by GDA, eg /dls/i13/data/2015/cm12165-1/raw/61192
    """
    dir = PathConstructor.createFromDefaultProperty()
    filenumber = i13iNumTracker.getCurrentFileNumber()
    return os.path.join(dir, str(filenumber))

# to get the next file path, eg /dls/i13/data/2015/cm12165-1/raw/61192
def nwd():
    """
    Method to get the next file path, eg /dls/i13/data/2015/cm12165-1/raw/61192
    """
    dir = PathConstructor.createFromDefaultProperty()
    filenumber = i13iNumTracker.getCurrentFileNumber()
    return os.path.join(dir, str(filenumber + 1))

# to change the sub-directory of the GDA current working directory
def setSubdirectory(dirname):
    """
    Method to add a sub-directory to the GDA current working directory, eg setSubdirectory('X/Y') sets the path to /dls/i13/data/2015/cm12165-1/X/Y/
    and setSubdirectory('') sets the path back to /dls/i13/data/2015/cm12165-1/
    """
    try:
        finder.find("GDAMetadata").setMetadataValue("subdirectory", dirname)
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "problem setting metadata value for 'subdirectory' to " + dirname, exceptionType, exception, traceback, False)
        print "Failed to set metadata value for 'subdirectory' to:", dirname, exception
        

# to get the sub-directory of the GDA current working directory
def getSubdirectory():
    """
    Method to get the sub-directory of the GDA current working directory, eg 'X/Y' is returned if setSubdirectory('X/Y') was executed earlier to set
    the path to /dls/i13/data/2015/cm12165-1/X/Y/.
    For the default sub-directory on i13i, getSubdirectory outputs 'raw'. 
    """
    try:
        return finder.find("GDAMetadata").getMetadataValue("subdirectory")
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "problem getting metadata value for 'subdirectory' ", exceptionType, exception, traceback, False)
        print "Failed to get metadata value for 'subdirectory':", exception
        return None

def rreplace(s, old, new, occurrence):
        li = s.rsplit(old, occurrence)
        return new.join(li)

def getVisitRootPath():
    """
    Returns string representing current visit root path, eg /dls/i12/data/2014/cm4963-2
    """
    try:
        subDirname = finder.find("GDAMetadata").getMetadataValue("subdirectory")
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "problem getting metadata value for 'subdirectory' ", exceptionType, exception, traceback, False)
        print "Failed to get metadata value for subdirectory:", exception
    workDirpath = wd()
    if (subDirname is not None) and (subDirname != ""):
        visitRootpath = rreplace(workDirpath, os.sep+subDirname,"",1)
    else:
        visitRootpath = workDirpath
    return visitRootpath

def _qFlyScanBatch(nScans, batchTitle, interWait, inBeamPosition, outOfBeamPosition, exposureTime=1., start=-90., stop=90., step=0.1, darkFieldInterval=0., flatFieldInterval=0., imagesPerDark=20, imagesPerFlat=20, min_i=-1., setupForAlignment=False, autoAnalyse=True, closeShutterAfterFlats=True):
    """
    Desc:
    Fn to submit a given number of identical tomoFlyScans to the queue for automatic execution with optional wait time between any two consecutive scans
    TO-DO: close shutter before any wait and after the batch is finished (need to get it from jythonNamespaceMapping first)
    
    Arg(s):
    nScans = total number of identical scans to be executed in this batch
        Note(s):
        (1) nScans=1 is admissible
    batchTitle = description of the sample or this batch of scans to be recorded in each Nexus scan file (each scan gets a unique post-fix ID appended to its batch title) 
    interWait = number of seconds to wait between two consecutive scans (NB. no wait is included after the last scan but note that some additional time will be spent 
        on moving to the start angle before the next scan is run)
        Note(s): 
        (1) interWait=0 is admissible 
        (2) if interWait is None, no waiting is included between scans (but note that some additional time will be spent on moving to the start angle before the next scan is run)
        (3) there is no waiting after the last scan of the batch
    """
    #tomoFlyScan(inBeamPosition, outOfBeamPosition, exposureTime=1, start=0., stop=180., step=0.1, darkFieldInterval=0., flatFieldInterval=0.,
    #          imagesPerDark=20, imagesPerFlat=20, min_i=-1., setupForAlignment=False, autoAnalyse=True, closeShutterAfterFlats=True)
    thisfn = qFlyScanBatch.__name__

    _args = []  # to store pairs (arg_name, arg_value) for executing tomoFlyScan
    _args.append(("inBeamPosition", inBeamPosition))
    _args.append(("outOfBeamPosition", outOfBeamPosition))
    _args.append(("exposureTime", exposureTime))
    _args.append(("start", start))
    _args.append(("stop", stop))
    _args.append(("step", step))
    _args.append(("darkFieldInterval", darkFieldInterval))
    _args.append(("flatFieldInterval", flatFieldInterval))
    _args.append(("imagesPerDark", imagesPerDark))
    _args.append(("imagesPerFlat", imagesPerFlat))
    _args.append(("min_i", min_i))
    _args.append(("setupForAlignment", setupForAlignment))
    _args.append(("autoAnalyse", autoAnalyse))
    _args.append(("closeShutterAfterFlats", closeShutterAfterFlats))

    def mysleep(secsToWait, v=True):
        if v:
            print "Waiting for %i sec..." %(secsToWait)  
        sleep(secsToWait)
        if v:
            print "Finished waiting for %i sec" %(secsToWait)

    cqp = finder.find("commandQueueProcessor")
    
    if (batchTitle is None) or len(batchTitle)==0:
        batchTitle = thisfn
    
    title_saved = getTitle()
    if (title_saved is None) or len(title_saved)==0:
        title_saved = "undefined" 
    
    scan_cmd = ",".join(["%s=%s" %(p[0], str(p[1])) for p in _args])
    scan_cmd = "tomographyScan.tomoFlyScan(" + scan_cmd + ")"
    print "scan_cmd = %s" %(scan_cmd)
    
    for i in range(nScans):
        title_tmp = batchTitle + "_%s/%s" %(i+1, nScans)
        print "scan %i (of %i): scan_cmd = %s, title = %s" %(i+1, nScans, scan_cmd, title_tmp)

        set_title_cmd = "setTitle(%s)" %(title_tmp)
        print "scan %i (of %i): set_title_cmd = %s, title = %s" %(i+1, nScans, set_title_cmd, title_tmp)
        cmd_tmp = set_title_cmd + ";" + scan_cmd
        print "scan %i (of %i): cmd_tmp = %s, title = %s" %(i+1, nScans, cmd_tmp, title_tmp)
        #cqp.addToTail(JythonCommandCommandProvider(cmd_tmp, title_tmp, None))
        sleep_cmd = None
        if (not (interWait is None)) and i < (nScans-1):
            sleep_cmd = "sleep(%i)" %(interWait)
            print "scan %i (of %i): sleep_cmd = %s, title = %s" %(i+1, nScans, sleep_cmd, title_tmp)
            cmd_tmp = cmd_tmp + ";" + sleep_cmd
            #cqp.addToTail(JythonCommandCommandProvider(sleep_cmd, sleep_cmd, None))
    
        print "scan %i (of %i): cmd_tmp = %s, title = %s" %(i+1, nScans, cmd_tmp, title_tmp)
        cmd_desc_tmp = set_title_cmd + "; " + "tomoFlyScan(...)" + ("; " + sleep_cmd if sleep_cmd is not None else '')
        print "scan %i (of %i): cmd_desc_tmp = %s, title = %s" %(i+1, nScans, cmd_desc_tmp, title_tmp)
        #cqp.addToTail(JythonCommandCommandProvider(cmd_tmp, cmd_desc_tmp, None)) 
        #cqp.addToTail(JythonCommandCommandProvider(cmd_tmp, title_tmp, None))
    
    # after the scans
    set_title_saved_cmd = "setTitle(%s)" %(title_saved)
    print "set_title_saved_cmd = %s" %(set_title_saved_cmd)
    #cqp.addToTail(JythonCommandCommandProvider(set_title_saved_cmd, set_title_saved_cmd, None))


