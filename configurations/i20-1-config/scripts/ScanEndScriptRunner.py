from gda.data import PathConstructor
from gda.device.scannable import ScannableBase
from gda.util import OSCommandRunner
#from gdascripts.parameters import beamline_parameters
from time import sleep
from gda.jython import InterfaceProvider

import os

class ScanEndScriptRunner(ScannableBase):
    """
    Class that runs a script at scan end.
    
    Example:
    
      pixium_redux=ScanEndScriptRunner('pixium_redux', '/dls_sw/apps/dawn_autoprocessing/autoprocess')
    """
    
    def __init__(self, name, exepath, delay_sec=0):
        self.name = name
        self.inputNames = [name]
        self.exepath = exepath
        self.delay_sec = delay_sec
        self.onOffPositioner = None
        self.setOutputFormat({});
        self.setInputNames({});
    
    def setProcessingOnOffPositioner(self, onOffPositioner):
        self.onOffPositioner = onOffPositioner
    
    def isRunProcessing(self):
        if self.onOffPositioner == None :
            return True
        return self.onOffPositioner.getPosition() == "true"

    def setRunProcessing(self, tf):
        if self.onOffPositioner != None :
            trueFalse = str(tf).lower()
            if trueFalse in self.onOffPositioner.getPositions() :
                self.onOffPositioner.moveTo(tf)

    def atScanEnd(self):
        sleep(self.delay_sec)
        self.run_exe()

# Get name of last scan that was run
    def get_last_scan_filename(self):
        sdpp = InterfaceProvider.getScanDataPointProvider()
        sdp = sdpp.getLastScanDataPoint()
        return sdp.getCurrentFilename()


    def run_exe(self):
        #path = PathConstructor.createFromDefaultProperty()
        #filenumber = "scan_filename_unknown"
        #fpath = os.path.join(path, str(filenumber)) + '.nxs'
        if self.isRunProcessing() :
            fpath=self.get_last_scan_filename()
            print('Executing script %s for Nexus scan file %s at the end of scan.' %(self.exepath,fpath))
            OSCommandRunner.runNoWait([self.exepath, fpath], OSCommandRunner.LOGOPTION.ALWAYS, None)

    def isBusy(self):
        return False

    def rawAsynchronousMoveTo(self,new_position):
        pass

    def rawGetPosition(self):
        return None
