#Origianlly copied from i12utilities.py
from gdascripts.messages import handle_messages
from gda.data import NumTracker
import os
from gda.data import PathConstructor
from gda.factory import Finder
import sys
import gda.device.scannable.DummyScannable
from gda.configuration.properties import LocalProperties
import subprocess
from gda.device import Scannable
from gda.jython.commands.GeneralCommands import ls_names, vararg_alias
from time import sleep
from gda.jython.commands import GeneralCommands
from gda.epics import CAClient
from epics_scripts.pv_scannable_utils import caputStringAsWaveform

# set up a nice method for getting the latest file path
i11NumTracker = NumTracker("i11");
finder = Finder.getInstance()
ca=CAClient()

def wd():
    dir = PathConstructor.createFromDefaultProperty()
    return dir
    


# function to find the last file path
def pwd():
    dir = PathConstructor.createFromDefaultProperty()
    filenumber = i11NumTracker.getCurrentFileNumber();
    return os.path.join(dir, str(filenumber))
    


# function to find the next file path
def nwd():
    dir = PathConstructor.createFromDefaultProperty()
    filenumber = i11NumTracker.getCurrentFileNumber();
    return os.path.join(dir, str(filenumber + 1))
    
# function to find the next scan number
def nfn():
    filenumber = i11NumTracker.getCurrentFileNumber();
    return filenumber + 1
    
# function to find the next scan number
def cfn():
    filenumber = i11NumTracker.getCurrentFileNumber();
    return filenumber
    

# the subdirectory parts
def setSubdirectory(dirname):
    try:
        finder.find("GDAMetadata").setMetadataValue("subdirectory", dirname)
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "problem setting metadata value for 'subdirectory' to " + dirname, exceptionType, exception, traceback, False)
        print "Failed to set metadata value for 'subdirectory' to:", dirname, exception
        

def getSubdirectory():
    try:
        return finder.find("GDAMetadata").getMetadataValue("subdirectory")
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "problem getting metadata value for 'subdirectory' ", exceptionType, exception, traceback, False)
        print "Failed to get metadata value for 'subdirectory':", exception
        return None
        

from gda.data.metadata import GDAMetadataProvider
def getVisit():
    """
    Returns string representing current visit ID, eg cm4963-2
    """
    try:
        gdaMetaProvider=GDAMetadataProvider.getInstance()
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "problem getting GDA metadata provider", exceptionType, exception, traceback, False)
        print "Failed to get GDA metadata provider:", exception
    return gdaMetaProvider.getMetadataValue(GDAMetadataProvider.EXPERIMENT_IDENTIFIER)

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
    
    
def setDataWriterToNexus():
    oldDW = LocalProperties.get("gda.data.scan.datawriter.dataFormat")
    LocalProperties.set("gda.data.scan.datawriter.dataFormat", "NexusDataWriter")
    newDW = LocalProperties.get("gda.data.scan.datawriter.dataFormat")
    print "Old DataWriter: ", oldDW
    print "New DataWriter: ", newDW
    
def setDataWriterToSrs():
    oldDW = LocalProperties.get("gda.data.scan.datawriter.dataFormat")
    LocalProperties.set("gda.data.scan.datawriter.dataFormat", "SrsDataFile")
    newDW = LocalProperties.get("gda.data.scan.datawriter.dataFormat")
    print "Old DataWriter: ", oldDW
    print "New DataWriter: ", newDW
    
def getDataWriter():
    return LocalProperties.get("gda.data.scan.datawriter.dataFormat")
    
class DocumentationScannable(gda.device.scannable.DummyScannable):
    def __init__(self, name, mesg, url=None):
        super(DocumentationScannable, self).__init__(name)
        self.mesg = mesg
        self.url = url
        pass
    
    def __doc__(self):
        hSC = finder.find("helpScriptController")
        if self.url != None and hSC != None:
            #subprocess.Popen(['python2.6', '-m', 'webbrowser', '-t', self.url])
            hSC.update(hSC, "URL:" + `self.url`)
        return self.mesg

class ConstantScannable(gda.device.scannable.ScannableBase):
    def __init__(self, name, value, unit=None):
        self.setName(name)
        self.value = value
        self.unit=unit
    
    def getPosition(self):
        return self.value
    
    def asynchronousMoveTo(self, posi):
        pass

    def isBusy(self):
        return False
    
def ls_scannables():
    ls_names(Scannable)
    

def setUpCopyPluginForPCO():
    print "setting up cpy plugin for PCO"
    ca.caput( "BL12I-EA-DET-02:COPY:Run", 0)
    ca.caputStringAsWaveform( "BL12I-EA-DET-02:COPY:SourceFilePath", "d:\\i12\\data\\2014")
    ca.caputStringAsWaveform( "BL12I-EA-DET-02:COPY:DestFilePath", "t:\\i12\\data\\2014")
    ca.caput ("BL12I-EA-DET-02:COPY:Run", 1)


def setUpCopyPluginForPIXIUM():
    print "setting up cpy plugin for PIXIUM"
    ca.caput( "BL12I-EA-DET-10:FILECOPY:Run", 0)
    ca.caputStringAsWaveform( "BL12I-EA-DET-10:FILECOPY:SourceFilePath", "d:\\i12\\data\\2014")
    ca.caputStringAsWaveform( "BL12I-EA-DET-10:FILECOPY:DestFilePath", "t:\\i12\\data\\2014")
    ca.caput ("BL12I-EA-DET-10:FILECOPY:Run", 1)

from gda.jython import InterfaceProvider
from gda.device.scannable import EpicsScannable
def createScannableFromPV( name, pv, addToNameSpace=True, getAsString=True, hasUnits=False):
    """
    Description:
        utility function to create a scannable from a given PV
    Arguments:
        name - user-specified name of a scannable to be created, e.g. pixium10_DataType
        pv - EPICS identifier of pv to be used by the scannable, e.g. BL12I-EA-DET-10:CAM:DataType
        addToNameSpace = if True, the scannable is accessible from the commandline after the call
        getAsString - If True, output value is a string (useful for enum pv, in which case set getAsString=True, and set hasUnits=False)
        hasUnits - If False, output value is not converted to units - useful for enum pv with getAsString=True
    
    For example,
        createScannableFromPV("pixium10_DataType", "BL12I-EA-DET-10:CAM:DataType", True, True, False)
    creates a scannable for pv with the following enums:
    caget -d 31 BL12I-EA-DET-10:CAM:DataType
        BL12I-EA-DET-10:CAM:DataType
        Native data type: DBF_ENUM
        Request type:     DBR_CTRL_ENUM
        Element count:    1
        Value:            UInt32
        Status:           NO_ALARM
        Severity:         NO_ALARM
        Enums:            ( 8)
                          [ 0] Int8
                          [ 1] UInt8
                          [ 2] Int16
                          [ 3] UInt16
                          [ 4] Int32
                          [ 5] UInt32
                          [ 6] Float32
                          [ 7] Float64
    """
    sc = EpicsScannable()
    sc.setName(name)
    sc.setPvName(pv)
    sc.setUseNameAsInputName(True)
    sc.setGetAsString(getAsString)
    sc.setHasUnits(hasUnits)
    sc.afterPropertiesSet()
    sc.configure()
    if addToNameSpace:
        commandServer = InterfaceProvider.getJythonNamespace()
        commandServer.placeInJythonNamespace(name,sc)
    return sc
