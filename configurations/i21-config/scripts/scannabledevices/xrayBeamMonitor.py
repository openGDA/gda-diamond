'''
Created on 3 Jul 2017

@author: fy65
'''
from gda.device.scannable import ScannableBase
from org.eclipse.scanning.sequencer import ServiceHolder

class XRayBeamMonitor(ScannableBase):
    '''
    A warpper object of X-ray beam watch dog, which allows switch or change test expression for a given scannable and threshold.
    The watch dog is activated, and enabled by default, but can be disabled via this object.
    The watch dog only kick into action at scan start and stopped at scan end or stop.
    '''

    def __init__(self, name, xraywatchdog="XRayWatchdog"):
        '''
        requires a watch dog object configured in Spring bean
        '''
        self.setName(name)
        self.setInputNames([name])
        self.setOutputFormat(["%s"])
        self.watchdog=ServiceHolder.getWatchdogService().getWatchdog(xraywatchdog)
        self.model=self.watchdog.getModel()
        
    def setExpression(self, expressions):
        self.model.setExpression(expressions)
        
    def getExpression(self):
        return self.model.getExpression()
    
    def getPosition(self):
        return self.getExpression()
    
    def asynchronousMoveTo(self, expression):
        self.setExpression(expression)
    
    def isBusy(self):
        return False
    
    def isEnabled(self):
        return self.watchdog.isEnabled()
    
    def enable(self):
        self.watchdog.setEnabled(True)
        
    def disable(self):
        self.watchdog.setEnabled(False)
        
    def toFormattedString(self):
        return self.getPosition()
        
