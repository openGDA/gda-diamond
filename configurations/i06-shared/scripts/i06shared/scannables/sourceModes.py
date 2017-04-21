'''
Scannable defines the X-ray source mode to be one of ['idd','idu','dpu','dmu'] in GDA only. 
It enables and disable 'zacscan' support when sets the mode value.

Created on 13 Apr 2017

@author: fy65
'''
from gda.device.scannable import ScannableBase
from gda.jython import InterfaceProvider

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
    SOURCE_MODES=['idd','idu','dpu','dmu']
    
    def __init__(self, name, defaultmode=SourceMode.SOURCE_MODES[0]):
        '''
        Constructor - default source mode is 'idd'
        '''
        self.setName(name)
        self.amIBusy=False
        self.mode=defaultmode
        
    def getPosition(self):
        return self.mode
    
    def rawAsynchronousMoveTo(self, mode):
        if mode not in SourceMode.SOURCE_MODES:
            print "mode string is wrong: legal values are %s" % (SourceMode.SOURCE_MODES)
            return 
        self.amIBusy=True # need to block to ensure script run complete before any other actions
        if mode == SourceMode.SOURCE_MODES[0]:
            locate_script = InterfaceProvider.getCommandRunner().locateScript("idd_fast_energy_scan.py")
            InterfaceProvider.getCommandRunner().runScript(locate_script,"idd_fast_energy_scan")
        elif mode == SourceMode.SOURCE_MODES[1]:
            locate_script = InterfaceProvider.getCommandRunner().locateScript("idu_fast_energy_scan.py")
            InterfaceProvider.getCommandRunner().runScript(locate_script,"idu_fast_energy_scan")
        elif mode == SourceMode.SOURCE_MODES[2] or mode == SourceMode.SOURCE_MODES[3]:
            locate_script = InterfaceProvider.getCommandRunner().locateScript("remove_zacscan.py")
            InterfaceProvider.getCommandRunner().runScript(locate_script,"remove_zacscan")
        else:
            print "Input mode is wrong: legal values %s or [SourceModeScannable.d, SourceModeScannable.u, SourceModeScannable.dpu, SourceModeScannable.dmu]. Operation cancelled." % (SourceMode.SOURCE_MODES)
            raise ValueError("Input mode %s is not supported." % (str(mode)))
        self.mode=mode
        self.amIBusy=False
            
    def isBusy(self):
        return self.amIBusy
    