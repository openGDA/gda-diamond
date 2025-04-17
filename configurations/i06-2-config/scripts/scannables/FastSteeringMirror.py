'''
A Scannable class supporting laser fast steering mirror

Created on 17 Apr 2025

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from i06shared import installation
import random

class FastSteeringMirror(ScannableMotionBase):
    '''
    The laser fast steering mirror control support following PVs
    Out-Monitor: BL06K-OP-FSM-01:X:OUT-MONITOR
    Error: BL06K-OP-FSM-01:X:ERR
    Command: BL06K-OP-FSM-01:X:CMD - used for 'Closed loop'
    Open loop command: BL06K-OP-FSM-01:X:OPENLOOP
    Open loop select: BL06K-OP-FSM-01:X:OLSELECT - value {0: 'Closed loop', 1: 'Open loop'}
    '''


    def __init__(self, name, pv_root):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.setOutputFormat(['%.3f'])
        self.ch_monitor = CAClient(pv_root + ":OUT-MONITOR")
        self.ch_error = CAClient(pv_root + ":ERR")
        self.ch_cmd = CAClient(pv_root + ":CMD")
        self.ch_olcmd = CAClient(pv_root + ":OPENLOOP")
        self.ch_olselect = CAClient(pv_root + ":OLSELECT")
        self._busy = False
        self.set_value = None

    def configure(self):
        if self.isConfigured():
            return
        if not self.ch_monitor.isConfigured():
            self.ch_monitor.configure()
        if not self.ch_error.isConfigured():
            self.ch_error.configure()
        if not self.ch_cmd.isConfigured():
            self.ch_cmd.configure()
        if not self.ch_olcmd.isConfigured():
            self.ch_olcmd.configure()
        if not self.ch_olselect.isConfigured():
            self.ch_olselect.configure()
        self.setConfigured(True)
            
    def getPosition(self):
        if installation.isDummy():
            if self.set_value:
                return self.set_value
            else:
                return random.randrange(1,10)
        else:
            if not self.isConfigured():
                self.configure()
            return float(self.ch_monitor.caget())
    
    def asynchronousMoveTo(self, v):
        self._busy = True
        if installation.isDummy():
            self.set_value = float(v)
        else:
            if not self.isConfigured():
                self.configure()
            olselect = int(self.ch_olselect.caget())
            if olselect == 1:
                self.ch_olcmd.caput(float(v))
            else:
                self.ch_cmd.caput(float(v))
        self._busy = False

    def isBusy(self):
        return self._busy
    
    def gerError(self):
        if installation.isDummy():
            return 0.0
        else:
            if not self.isConfigured():
                self.configure()
            return float(self.ch_error.caget())
    
fsmx = FastSteeringMirror("fsmx", "BL06K-OP-FSM-01:X")
fsmy = FastSteeringMirror("fsmy", "BL06K-OP-FSM-01:Y")
 