'''
Created on Sep 24, 2021

@author: fy65
'''
import random

from gda.device.scannable import ScannableMotionBase
from gda.epics.connection import EpicsController
from i06shared import installation
from gov.aps.jca import TimeoutException  # @UnresolvedImport


GAIN_MODES = ["low noise", "high speed"]
gain_map = {
    "10^3 low noise" : (1e3, GAIN_MODES[0]),
    "10^4 low noise" : (1e4, GAIN_MODES[0]),
    "10^5 low noise" : (1e5, GAIN_MODES[0]),
    "10^6 low noise" : (1e6, GAIN_MODES[0]),
    "10^7 low noise" : (1e7, GAIN_MODES[0]),
    "10^8 low noise" : (1e8, GAIN_MODES[0]),
    "10^9 low noise" : (1e9, GAIN_MODES[0]),
    "10^5 high speed" : (1e5, GAIN_MODES[1]),
    "10^6 high speed" : (1e6, GAIN_MODES[1]),
    "10^7 high speed" : (1e7, GAIN_MODES[1]),
    "10^8 high speed" : (1e8, GAIN_MODES[1]),
    "10^9 high speed" : (1e9, GAIN_MODES[1]),
    "10^10 high speed" : (1e10, GAIN_MODES[1]),
    "10^11 high speed" : (1e11, GAIN_MODES[1]),
    }

class AmplifierGainParser(ScannableMotionBase):
    '''
    parse EPICS gain returns into gain digital value and gain mode string
    '''

    def __init__(self, name, pv_name):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([])
        self.setExtraNames(["scale", "mode"])
        self.setOutputFormat(["%e", "%s"])
        self.EPICS_CONTROLLER = EpicsController.getInstance()
        if installation.isLive():
            try:
                self.ch = self.EPICS_CONTROLLER.createChannel(pv_name)
            except TimeoutException, e:
                print("%s: %s" % (self.getName(), e.getMessage()))
        
    def getPosition(self):
        if installation.isDummy():
            return random.choice(list(gain_map.values()))
        try:
            gainstring = self.EPICS_CONTROLLER.getValue(self.ch)
            return gain_map[gainstring]
        except:
            return (-99999, "Failed to get GAIN MODE from device")
    
    def asynchronousMoveTo(self, new_pos):
        print("%s: read-only scannable" % (self.getName()))
        
    def isBusy(self):
        return False
    
