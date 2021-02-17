'''
class support addition PV value change before and after a given scannable motion.

Created on Jan 13, 2021

@author: fy65
'''

from gda.device.scannable import ScannableMotionBase
from gdascripts.utils import caput

class ScannableWithPVControl(ScannableMotionBase):
    '''
    scannable motion wrapped around a PV control, such as disable feedback before move and restore feedback after move.
    '''


    def __init__(self, name, scannable, pvname = None, pvvaluebefore=0, pvvalueafter=4):
        '''
        Constructor
        '''
        self.setName(name)
        self.scannable = scannable
        self.pvname = pvname
        self.valuebefore = pvvaluebefore
        self.valueafter = pvvalueafter
        self.SCANNING = False
    
    def rawGetPosition(self):
        return self.scannable.getPosition()
    
    def rawAsynchronousMoveTo(self, new_pos):
        try:
            if self.pvname is not None and not self.SCANNING:
                #change PV value before move and after move
                caput(self.pvname, self.valuebefore)
                self.scannable.moveTo(new_pos)
                caput(self.pvname, self.valueafter)
            else:
                self.scannable.asynchronousMoveTo(new_pos)
        except Exception, e:
            print("cannot move %s to %f" % (self.scannable.getName(), new_pos))
            raise e
        
    def rawIsBusy(self):
        return self.scannable.isBusy()
    
    def stop(self):
        self.scannable.stop()
        
    def atScanStart(self):
        self.SCANNING=True
        if self.pvname is not None:
            #set PV value before scan start
            caput(self.pvname, self.valuebefore)

    def atScanEnd(self):
        self.SCANNING=False
        if self.pvname is not None:
            #set PV value after scan end
            caput(self.pvname, self.valueafter)
            