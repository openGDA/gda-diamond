'''
A Scannable class that moves epics_armtth, m5tth, and m5hqry concurrently for a single given position. Polynomial coefficients are required to calculate the position for m5hqry, and m5hqrx, these are defined in the constructor.
Further requirements implemented are:
1. m5hqrx can only move after m5hqry motion completed
2. this scannable should be supported in 'move' command just like 'epics_armtth'

Created on Feb 17, 2021

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from org.slf4j import LoggerFactory
from i21commands.checkedMotion import asynmove


class M5GroupScannable(ScannableMotionBase):
    '''
    A group scannable dedicated to two theta motion in I21. It has I21 arm tth motion specific logics.
    '''

    def __init__(self, name, armtth, m5tth, m5hqry, m5hqrx, m5hqry_0=342.9979644425, m5hqry_1=-0.2487741425, m5hqry_2=0.0018219019, m5hqrx_0=-363.5691038104, m5hqrx_1=-2.1936146304, m5hqrx_2=0.0074169737):
        '''
        create a wrapper scannable that moves ARM tth, M5 tth, m5hqry, and m5hqrx for a single tth position input, it returns positions of these motor on completion.
        '''
        self.logger = LoggerFactory.getLogger(M5GroupScannable.__class__.__name__)
        self.setName(name)
        self.setInputNames([])
        self.setExtraNames([armtth.getName(), m5tth.getName(), m5hqry.getName(), m5hqrx.getName()])
        self.armtth = armtth
        self.m5tth = m5tth
        self.m5hqry = m5hqry
        self.m5hqrx = m5hqrx
        self.m5hqry_0 = m5hqry_0
        self.m5hqry_1 = m5hqry_1
        self.m5hqry_2 = m5hqry_2
        self.m5hqrx_0 = m5hqrx_0
        self.m5hqrx_1 = m5hqrx_1
        self.m5hqrx_2 = m5hqrx_2
        self._busy = False
        
    def asynchronousMoveTo(self, newpos):
        try:
            self._busy = True  # need to set this to prevent race condition due to network communication and PV request response times.
            asynmove(self.armtth, newpos)  # use 'asynmove' so air supply and other dependent motor positions can be checked!
            self.m5tth.asynchronousMoveTo(newpos)
            self.m5hqry.asynchronousMoveTo(self.m5hqry_0 + self.m5hqry_1 * newpos + self.m5hqry_2 * newpos ** 2)
            self.m5hqry.waitWhileBusy()
            self.m5hqrx.asynchronousMoveTo(self.m5hqrx_0 + self.m5hqrx_1 * newpos + self.m5hqrx_2 * newpos ** 2)
        except Exception, e:
            self.logger.error("Exception throws in asynchronousMoveTo ", e)
            raise e
        finally:
            self._busy = False
        
    def getPosition(self):
        return self.armtth.getPosition(), self.m5tth.getPosition(), self.m5hqry.getPosition(), self.m5hqrx.getPosition()
    
    def isBusy(self):
        return self._busy or self.armtth.isBusy() or self.m5tth.isBusy() or self.m5hqry.isBusy() or self.m5hqrx.isBusy()
    
    def stop(self):
        self.armtth.stop()
        self.m5tth.stop()
        self.m5hqry.stop()
        self.m5hqrx.stop()
    
            
