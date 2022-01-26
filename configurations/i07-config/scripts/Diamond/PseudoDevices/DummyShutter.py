#from gda.device.scannable import ScannableMotionBase
from gda.device.scannable import ScannableBase
from gda.epics import CAClient 
from time import sleep



class DummyShutterClass(ScannableBase):
    SHUTTER_COMMAND={'Open' : '1',
                     'Close': '0'};
    SHUTTER_STATUS={'1' : 'Open',
                    '0' : 'Closed'};
    
    def __init__(self, name, delayAfterOpening=0.5, delayAfterClosing=0):
        self.name = name
        self.inputNames = [name]
        self.outputFormat = ['%d']
        self.level = 6
        self.delayAfterOpening = delayAfterOpening
        self.delayAfterClosing = delayAfterClosing
        
        self.valvePosition = 0; # default is 0: Closed

    def isBusy(self):
        return 0

    def getPosition(self):
        return self.valvePosition;

    def asynchronousMoveTo(self, newPosition):
        if str(newPosition) in DummyShutterClass.SHUTTER_COMMAND.keys():
            self.operateShutter(DummyShutterClass.SHUTTER_COMMAND[str(newPosition)])
        elif newPosition in DummyShutterClass.SHUTTER_COMMAND.values():
            self.operateShutter(newPosition)
        else:
            pass
            #work out what's consistent with the new fastShutter implementation
            #and hopefully get rid of this one day.
            #print "Wrong requirement. Please use 'Open'/'Close' or 1/0."
            
    def operateShutter(self, newpos, report=False):
        self.valvePosition = newpos;
        sleep(self.delayAfterOpening)
            
    def toFormattedString(self):
        st = DummyShutterClass.SHUTTER_STATUS[ self.valvePosition ]
        return st
    
    def stop(self):
        self.asynchronousMoveTo('Close')
       
        
#Example:
dummyShutter = DummyShutterClass('dummyShutter', delayAfterOpening=0.5, delayAfterClosing=0);


