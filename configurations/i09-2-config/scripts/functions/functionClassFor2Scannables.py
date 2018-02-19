'''
Created on 7 Oct 2013

@author: fy65
'''
from gda.device.scannable import ScannableBase

ROOT_NAMESPACE_DICT = None

class ScannableFunctionClassFor2Scannables(ScannableBase):
    '''
    a class definition for creating a scannable that returns a single calculated value 
    based on the function specified while scanning scannableX and scannableY.
    Usage:
        >>>dr=ScannableFunctionClassFor2Scannables("dr", "energy", "mac15", "derivative");
        >>>scan scannableX 1 10 1 scannableY 2 dr
    '''


    def __init__(self, name, scannableX, scannableY, deviceFun):
        '''
        Constructor parameters:
                name:   Name of the new scannable
                scannableX: Name of the scannableX (for example: "Io")
                scannableY: Name of the scannableY (for example: "Ie")
                deviceFun:  Name of the function to calculate the new position based on scannableX and scannableY positions
        '''
        self.setName(name);
        self.setInputNames([name]);
        #self.Units=[strUnit]
        #self.setOutputFormat([strFormat])
        #self.setLevel(8);
        self.x1 = 0.0;
        self.x2 = 0.0;
        self.y = 0.0;
        if ROOT_NAMESPACE_DICT is not None:
            self.refObj1 = ROOT_NAMESPACE_DICT[scannableX]
            self.refObj2 = ROOT_NAMESPACE_DICT[scannableY]
        else:
            print "ROOT_NAMESPACE_DICT is None, cannot find the scannables: %s and %s",(scannableX, scannableY)
        self.deviceFun = deviceFun
        

    def getPosition(self):
        '''return the value of this scannable calculated from the scannableX and scannableY. '''
        self.x1=self.refObj1.getPosition();
        self.x2=self.refObj2.getPosition();
        self.y = self.funForeward(self.x1, self.x2);
        return self.y;

    def funForeward(self, x1, x2):
        return self.deviceFun(x1, x2);

    def asynchronousMoveTo(self, new_position):
        print "This scannable is read-only scannable.";

    def isBusy(self):
        '''returns busy if the two scannables are busy'''
        return (self.refObj1.isBusy() & self.refObj2.isBusy());
