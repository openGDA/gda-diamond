'''
a scannable that moves CFF which ensure the b2 shadow is always updated after CFF motion completed.

Created on Sep 15, 2022

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.device import DeviceException
import threading

class CoupledScannable(ScannableMotionBase):
    '''
    a special scannable that couples scannable cff, b2, and pgmB2Shadow together.
    '''


    def __init__(self, name, cff, b2, b2shadow):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.cff = cff
        self.b2 = b2
        self.b2shadow = b2shadow
        self.event = threading.Event()

        
    def asynchrouoseMoveTo(self, cffval):        
        # use thread to not block this method
        th = threading.Thread(target=self.move_cff_update_b2shadow, args=(cffval,))
        #use threading event to share boolean status
        self.event.set()
        th.start()
        
    
    def move_cff_update_b2shadow(self, cffval):
        try: 
            self.cff.moveTo(cffval)
            newb2 = float(self.b2.getPosition())
            self.b2shadow.moveTo(newb2)
        except Exception, e:
            raise DeviceException(self.getName() + " : " + e.message)
        finally:
            self.event.clear()
        
            
    def getPosition(self):
        return float(self.cff.getPsition())
    
    
    def isBusy(self):
        return self.cff.isBusy() or self.b2shadow.isBusy() or self.event.is_set()
    

from gdaserver import cff, b2, pgmB2Shadow    # @UnresolvedImport
cff_b2 = CoupledScannable("cff_b2", cff, b2, pgmB2Shadow)
    