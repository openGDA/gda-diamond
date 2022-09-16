'''
a scannable intercepts a given scannable's asynchronousMoveTo(...) call to perform additional action in given function.

Created on Sep 16, 2022

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from i21commands.checkedMotion import enable_arm_motion

class InterceptedScannable(ScannableMotionBase):
    '''
    a wrapper scannable that ensure a given function is called before delegate move back to the given scannable
    '''


    def __init__(self, name, scannable, wrap_func = None):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([scannable.getName()])
        self.scannable = scannable
        self.function = wrap_func
        self._busy = False
        
    def asynchronousMoveTo(self, val):
        try:
            self._busy = True
            if self.function is not None:
                self.function.__call__()
            self.scannable.asynchronousMoveTo(val)
        finally:
            self._busy = False

    def getPosition(self):
        return self.scannable.getPosition()
    
    def isBusy(self):
        return self.scannable.isBusy() or self._busy

from gdaserver import spech  # @UnresolvedImport
spech_wraper = InterceptedScannable("spech_wraper", spech, wrap_func = enable_arm_motion)