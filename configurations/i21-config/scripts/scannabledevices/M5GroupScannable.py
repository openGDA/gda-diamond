'''
A Scannable class that moves epics_armtth, m5tth, and m5hqry concurrently for a single given position. Polynomial coefficients are required to calculate the position for m5hqry, and m5hqx, these are defined in the constructor.
Further requirements implemented are:
1. m5hqx can only move after m5hqry motion completed
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

    def __init__(self, name, armtth, m5tth, m5hqry, m5hqx, m5hqry_0=342.9979644425, m5hqry_1=-0.2487741425, m5hqry_2=0.0018219019, m5hqx_0=-363.5691038104, m5hqx_1=-2.1936146304, m5hqx_2=0.0074169737):
        '''
        create a wrapper scannable that moves ARM tth, M5 tth, m5hqry, and m5hqx for a single tth position input, it returns positions of these motor on completion.
        '''
        self.logger = LoggerFactory.getLogger(M5GroupScannable.__class__.__name__)
        self.setName(name)
        self.setInputNames([armtth.getName()])
        self.setExtraNames([m5tth.getName(), m5hqry.getName(), m5hqx.getName()])
        self.setOutputFormat([armtth.getOutputFormat()[0], m5tth.getOutputFormat()[0], m5hqry.getOutputFormat()[0], m5hqx.getOutputFormat()[0]])
        self.armtth = armtth
        self.m5tth = m5tth
        self.m5hqry = m5hqry
        self.m5hqx = m5hqx
        self.m5hqry_0 = m5hqry_0
        self.m5hqry_1 = m5hqry_1
        self.m5hqry_2 = m5hqry_2
        self.m5hqx_0 = m5hqx_0
        self.m5hqx_1 = m5hqx_1
        self.m5hqx_2 = m5hqx_2
        self.markbusy = False
        
    def asynchronousMoveTo(self, newpos):
        newpos = float(newpos)
        try:
            self.markbusy = True  # need to set this to prevent race condition due to network communication and PV request response times.
            print("moving armtth to %s ..." % newpos)
            self.armtth.asynchronousMoveTo(newpos) 
            print("moving m5tth to %s ..." % newpos)
            self.m5tth.asynchronousMoveTo(newpos)
            print("moving m5hqry to %s ..." % (self.m5hqry_0 + self.m5hqry_1 * newpos + self.m5hqry_2 * newpos ** 2))
            self.m5hqry.asynchronousMoveTo(self.m5hqry_0 + self.m5hqry_1 * newpos + self.m5hqry_2 * newpos ** 2)
            print("waiting for m5hqry to complete ...")
            self.m5hqry.waitWhileBusy()
            print("moving m5hqx to %s ..." % (self.m5hqx_0 + self.m5hqx_1 * newpos + self.m5hqx_2 * newpos ** 2))
            self.m5hqx.asynchronousMoveTo(self.m5hqx_0 + self.m5hqx_1 * newpos + self.m5hqx_2 * newpos ** 2)
        except Exception, e:
            self.logger.error("Exception throws in asynchronousMoveTo ", e)
            raise e
        finally:
            self.markbusy = False
        
    def getPosition(self):
        return float(self.armtth.getPosition()), float(self.m5tth.getPosition()), float(self.m5hqry.getPosition()), float(self.m5hqx.getPosition())
    
    def isBusy(self):
        return self.markbusy or self.armtth.isBusy() or self.m5tth.isBusy() or self.m5hqry.isBusy() or self.m5hqx.isBusy()
    
    def stop(self):
        self.armtth.stop()
        self.m5tth.stop()
        self.m5hqry.stop()
        self.m5hqx.stop()
    
            
