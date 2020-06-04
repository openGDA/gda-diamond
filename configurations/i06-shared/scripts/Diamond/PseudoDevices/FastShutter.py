#from gda.device.scannable import ScannableMotionBase
from gda.device.scannable import ScannableBase
from gda.epics import CAClient 
from time import sleep



class FastShutterClass(ScannableBase):
    SHUTTER_COMMAND={'Open' : 1,
                     'Close': 0};
    SHUTTER_STATUS={1 : 'Open',
                    0 : 'Closed'};
    
    
    """ This class is a template and can't be initialised or easily extended """
    """ This is an example constructor.  Make sure to call completeInitialisationt(). """

    def __init__(self, name, pvstring, delayAfterOpening=0.5, delayAfterClosing=0):
        self.name = name
        self.inputNames = [name]
        self.outputFormat = ['%d']
        self.level = 6
        self.delayAfterOpening = delayAfterOpening
        self.delayAfterClosing = delayAfterClosing
        self.pv = CAClient(pvstring)
        self.pv.configure()

    def isBusy(self):
        return 0

    def getPosition(self):
        return int(float(self.pv.caget()))

    def asynchronousMoveTo(self, newPosition):
        if str(newPosition) in FastShutterClass.SHUTTER_COMMAND.keys():
            self.operateShutter(FastShutterClass.SHUTTER_COMMAND[str(newPosition)])
        elif newPosition in FastShutterClass.SHUTTER_COMMAND.values():
            self.operateShutter(newPosition)
        else:
            print "Wrong requirement. Please use 'Open'/'Close' or 1/0."
            
    def operateShutter(self, newpos, report=False):
        self.pv.caput( int(newpos) )
        sleep(self.delayAfterOpening)
        if report:
            st = FastShutterClass.SHUTTER_STATUS[self.pv.caget()]
            print st, self.name
            
    def toFormattedString(self):
        st = FastShutterClass.SHUTTER_STATUS[int(self.pv.caget())]
        return st
      
    def stop(self):
        self.asynchronousMoveTo('Close')
        
#Example:
#fs = FastShutterClass('fs', "BL07I-EA-SHTR-01:CON", delayAfterOpening=0.5, delayAfterClosing=0);


