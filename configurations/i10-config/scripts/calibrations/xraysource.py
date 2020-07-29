'''
Class sets the X-ray source mode to be one of ['idd','idu'] in GDA only. 

It also moves the ID that is not used to generate X-ray beam to 200mm gap.

Created on 15 July 2020

@author: fy65
'''
from gda.device.scannable import ScannableBase
from gda.configuration.properties import LocalProperties

gda_git_loc = LocalProperties.get(LocalProperties.GDA_GIT_LOC)
X_RAY_SOURCE_MODES=['idd','idu', 'unknown']

class SourceMode(ScannableBase):
    '''
    implements the 2 X-ray beam source modes
        1. Single operation of ID1 - specified by value 'idd'
        2. Single operation of ID2 - specified by value 'idu'
        
    Instance of this Scannable set/get source mode value in GDA only.
    It opens up the ID that is not used to generate X-ray beam! 
    '''
    
    def __init__(self, name, idu_gap, idd_gap, opengap=200, defaultmode=None):
        '''
        Constructor - default source mode is None
        '''
        self.setName(name)
        self.idu_gap=idu_gap
        self.idd_gap=idd_gap
        self.opengap=opengap
        self.amIBusy=False
        self.mode=defaultmode
        
    def getPosition(self):
        return self.mode
    
    def rawAsynchronousMoveTo(self, mode):
        if mode not in X_RAY_SOURCE_MODES:
            print "mode string is wrong: legal values are %s" % (SourceMode.SOURCE_MODES)
            return 
        self.amIBusy=True # need to block to ensure script run complete before any other actions
        if mode == X_RAY_SOURCE_MODES[0]:
            #idd mode specific processing
            self.idu_gap.asynchronousMoveTo(self.opengap)
        elif mode == X_RAY_SOURCE_MODES[1]:
            #idu mode specific processing
            self.idd_gap.asynchronousMoveTo(self.opengap)
        self.mode=mode
        self.amIBusy=False
            
    def isBusy(self):
        return self.amIBusy or self.idd_gap.isBusy() or self.idu_gap.isBusy()
    