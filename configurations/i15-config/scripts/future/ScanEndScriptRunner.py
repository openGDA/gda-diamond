from gda.jython import InterfaceProvider
from gda.device.scannable import ScannableBase
from gda.util import OSCommandRunner
#from gdascripts.parameters import beamline_parameters
from time import sleep

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

    def atScanEnd(self):
        sleep(self.delay_sec)
        self.run_exe()

    def run_exe(self):
        path = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
        #filenumber = i12NumTracker.getCurrentFileNumber();
        filenumber = "scan_filename_unknown"
        fpath = os.path.join(path, str(filenumber)) + '.nxs'
        print('Executing script %s for Nexus scan file %s at the end of scan.' %(self.exepath,fpath))
        OSCommandRunner.runNoWait([self.exepath, fpath], OSCommandRunner.LOGOPTION.ALWAYS, None)

    def isBusy(self):
        return False

    def rawAsynchronousMoveTo(self,new_position):
        pass

    def rawGetPosition(self):
        return 0
