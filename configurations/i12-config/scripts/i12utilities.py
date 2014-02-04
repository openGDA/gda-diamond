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
i12NumTracker = NumTracker("i12");
finder = Finder.getInstance()
ca=CAClient()

def wd():
    dir = PathConstructor.createFromDefaultProperty()
    return dir
    


# function to find the last file path
def pwd():
    dir = PathConstructor.createFromDefaultProperty()
    filenumber = i12NumTracker.getCurrentFileNumber();
    return os.path.join(dir, str(filenumber))
    


# function to find the next file path
def nwd():
    dir = PathConstructor.createFromDefaultProperty()
    filenumber = i12NumTracker.getCurrentFileNumber();
    return os.path.join(dir, str(filenumber + 1))
    
# function to find the next scan number
def nfn():
    filenumber = i12NumTracker.getCurrentFileNumber();
    return filenumber + 1
    
# function to find the next scan number
def cfn():
    filenumber = i12NumTracker.getCurrentFileNumber();
    return filenumber
    

# the subdirectory parts
def setSubdirectory(dirname):
    try:
        finder.find("GDAMetadata").setMetadataValue("subdirectory", dirname)
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "problem setting metadata value -'subdirectory' to " + dirname, exceptionType, exception, traceback, False)
        print "Failed to set metadata (subdirectory) value to:", dirname, exception
        

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

