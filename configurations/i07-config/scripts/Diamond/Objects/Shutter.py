
import __main__ as gdamain
from time import sleep

class ShutterDeviceClass(object):
    def __init__(self, shutterName=None):
        self.shutter = None;
        self.addShutter(shutterName);

    def addShutter(self, shutterName):
        if shutterName is None:
            self.removeShutter();
            return;
        if shutterName in vars(gdamain).keys():
            self.shutter = vars(gdamain)[shutterName];
        elif shutterName in vars(gdamain).values():
            self.shutter = shutterName;
        else:
            raise ValueError("Shutter does not exist!")
        
    def removeShutter(self):
        self.shutter=None;

            
    def listShutter(self):
        if self.shutter is not None:
            return self.shutter.getName();
        else:
            return None;
        
    def closeShutter(self):
        if self.shutter is not None:
            self.shutter.moveTo('0');
#            print "Shutter Closed"
            
    def openShutter(self):
        if self.shutter is not None:
            self.shutter.moveTo('1');
            sleep(0.5)
#            print "Shutter Opened"

