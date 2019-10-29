'''
Created on 20 Mar 2012

@author: zrb13439
'''
import time

from gda.device.scannable import ScannableBase
#import org.slf4j.Logger
from org.slf4j import LoggerFactory

DEBUG = False
logger = LoggerFactory.getLogger("b16WaitForCondition")

class WaitForCondition(ScannableBase):
    """Blocks while reading out, so as to require no input from user. Condition should act on
    th variable 'val'
    """
    
    def __init__(self, name, scannable, condition):
        self.name = name
        self.scannable = scannable
        self.inputNames = [name + '_post']
        self.extraNames = [name + '_dt']
        self.outputFormat = ['%.4f', '%.4f']
        self.condition = condition
        
        self.time_started_waiting = 0
        self.post_delay = 0
        self.level = 10
    
    def atPointStart(self):
        self.time_started_waiting = time.time()
        
    def asynchronousMoveTo(self, p):
        self.post_delay = float(p)
        
    def waitWhileBusy(self):
        val = self.scannable()
        logger.debug("{}: waiting for contition: {}".format(self.name, self.condition))
        while not eval(self.condition, {'val': val}):
            time.sleep(.1)
            val = self.scannable()

    def getPosition(self):
        time_waiting = time.time() - self.time_started_waiting
        time.sleep(self.post_delay)
        return self.post_delay, time_waiting
