'''
Scannable defines the X-ray source mode to be one of ['idd','idu','dpu','dmu'] in GDA only. 
It enables and disable 'zacscan' support when sets the mode value.

Created on 13 Apr 2017

@author: fy65
'''
from gda.device.scannable import ScannableBase
from gda.jython import InterfaceProvider
from gda.configuration.properties import LocalProperties
from java.io import File
from time import sleep
from gda.jython.commands import GeneralCommands

gda_git_loc = LocalProperties.get(LocalProperties.GDA_GIT_LOC)

class SourceMode(ScannableBase):
    '''
    implements the 4 X-ray beam source modes
        1. Single operation of HU64a - specified by value 'idd'
        2. Single operation of HU64b - specified by value 'idu'
        3. Operation of HU64a and HU64b in the same polarisation - specified by value 'dpu'
        4. Operation of HU64a and HU64b, but with different polarisations - specified by value 'dmu'
        
    Instance of this Scannable set/get source mode value in GDA only which 
        - enables 'zacscan' for the single source modes - 'idd' and 'idu'
        - disables 'zacscan' for combined source modes - 'dpu' and 'dmu'
    '''
    SOURCE_MODES=['idd','idu','dpu','dmu','unknown']
    
    def __init__(self, name, defaultmode='unknown'):
        '''
        Constructor - default source mode is 'idd'
        '''
        self.setName(name)
        self.amIBusy=False
        self.mode=defaultmode
        self.idd_fast_energy_scan_script=str(gda_git_loc+"/gda-diamond.git/configurations/i06-shared/scripts/i06shared/scan/idd_fast_energy_scan.py")
        self.idu_fast_energy_scan_script=str(gda_git_loc+"/gda-diamond.git/configurations/i06-shared/scripts/i06shared/scan/idu_fast_energy_scan.py")
        self.remove_zacscan_script=str(gda_git_loc+"/gda-diamond.git/configurations/i06-shared/scripts/i06shared/scan/remove_zacscan.py")
        GeneralCommands.run(self.idd_fast_energy_scan_script)
        
    def getPosition(self):
        return self.mode
    
    def rawAsynchronousMoveTo(self, mode):
        if mode not in SourceMode.SOURCE_MODES:
            print "mode string is wrong: legal values are %s" % (SourceMode.SOURCE_MODES)
            return 
        self.amIBusy=True # need to block to ensure script run complete before any other actions
        if mode == SourceMode.SOURCE_MODES[0]:
            scriptfile=File(self.remove_zacscan_script)
            InterfaceProvider.getCommandRunner().runScript(scriptfile)
            sleep(1)
            scriptfile=File(self.idd_fast_energy_scan_script)
            InterfaceProvider.getCommandRunner().runScript(scriptfile)
        elif mode == SourceMode.SOURCE_MODES[1]:
            scriptfile=File(self.remove_zacscan_script)
            InterfaceProvider.getCommandRunner().runScript(scriptfile)
            sleep(1)
            scriptfile=File(self.idu_fast_energy_scan_script)
            InterfaceProvider.getCommandRunner().runScript(scriptfile)
        elif mode == SourceMode.SOURCE_MODES[2] or mode == SourceMode.SOURCE_MODES[3]:
            scriptfile=File(self.remove_zacscan_script)
            InterfaceProvider.getCommandRunner().runScript(scriptfile)
            sleep(1)
        else:
            print "Input mode is wrong: legal values %s or [SourceModeScannable.idd, SourceModeScannable.idu, SourceModeScannable.dpu, SourceModeScannable.dmu]." % (SourceMode.SOURCE_MODES)
            self.mode=SourceMode.SOURCE_MODES[4]
            raise ValueError("Input mode %s is not supported." % (str(mode)))
        self.mode=mode
        self.amIBusy=False
            
    def isBusy(self):
        return self.amIBusy
    