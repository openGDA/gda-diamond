from gda.device.scannable import ScannableBase, ScannableUtils
from gda.scan import ScanPositionProvider, ScanBase
import gda.jython.commands.ScannableCommands.scan

class   flyscan_positions(ScanPositionProvider):
    def __init__(self, firstScannable, start, stop, step):
        self.firstScannable = firstScannable
        self.start = start
        self.stop = stop
        self.step = ScanBase.sortArguments(start, stop, step);
        numberSteps = ScannableUtils.getNumberSteps(firstScannable, self.start, self.stop, self.step)
        self.points = []
        self.points.append(flyscan_position(stop, start))
        previousPoint = start
        for i in range(numberSteps):
            nextPoint = ScannableUtils.calculateNextPoint(previousPoint, step);
            self.points.append(flyscan_position(None, nextPoint))
            previousPoint = nextPoint
        self.forward=True

    def get(self, index):
        max_index = self.size()-1
        if index > max_index:
            raise Exception("Position %d is outside possible range : %d" % (index, max_index))
        if self.forward:
            val = self.points[index]
            if index == max_index:
                self.forward = False
        else:
            val = self.points[max_index-index]
            if index == max_index:
                self.forward = True
        return val;
    
    def size(self):
        return len(self.points)
    
    def __str__(self):
        return "Scan %s from %s to %s in steps of %s. No of points = %d" % (self.firstScannable.getName(), `self.start`,`self.stop`,`self.step`, self.size() ) 
    def toString(self):
        return self.__str__()


class fly_scannable(ScannableBase):
    """
    Class that takes a scannable 
    Each position it receives contains is a tuple with the first element being the stop value to be sent to the scannable on first point in scan
    The scond value is the value that the scannable should reach for thiis scannable to report isBusy = false
    It has 1 input
    getposition returns the value at which the isBusy is to return false
    
    
    scan command 
    from flyscan_position_provider import flyscan_positions
    from  flyscan_scannable import flyscannable
    scan flyscannable(scannableA) flyscan_positions(scannableA, 0, 10, 1) det
    """
    def __init__(self, scannable):
        self.scannable = scannable
        if len( self.scannable.getInputNames()) != 1:
            raise Exception("No support for scannables with inputNames != 1")
        self.name = scannable.getName()+"_scanner"
        self.inputNames = [scannable.getInputNames() [0]+"_nominal"]
        self.extraNames= []
        self.outputFormats=[ "%.5g"]
        self.level = 3
        self.positive = True
        self.requiredPosVal = 0.
        self.stopVal=0.
        
    def getCurrentPositionOfScannable(self):
        return  ScannableUtils.positionToArray(self.scannable.getPosition(), self.scannable)[0]
    def isBusy(self):
        currentVal = self.getCurrentPositionOfScannable()
        if self.positive:
            return self.requiredPosVal > currentVal
        else:
            return self.requiredPosVal < currentVal

    def rawAsynchronousMoveTo(self,new_position):
        if  not  isinstance( new_position,  flyscan_position):
            raise "I only support positions of type flyscan_position_provider"
        self.scannable_position = new_position.position
        self.requiredPosVal = ScannableUtils.positionToArray(self.scannable_position, self.scannable)[0]
        if new_position.stop is None:
            return;
        """
        first move to start"
        """
        self.scannable.moveTo(self.scannable_position)
        
        stopPosition = new_position.stop
        self.scannable.asynchronousMoveTo(stopPosition)
        self.stopVal = ScannableUtils.positionToArray(stopPosition, self.scannable)[0]
        self.positive = self.stopVal > self.requiredPosVal
        return

    def rawGetPosition(self):
        return self.requiredPosVal

class flyscan_position:
    def __init__(self, stop, position):
        self.stop = stop
        self.position = position

def flyscan(args):
    newargs=[]
    i=0;
    while i< len(args):
        arg = args[i]
        newargs.append(arg)
        i=i+1
        if isinstance( arg,  fly_scannable):
            newargs.append( flyscan_positions(arg.scannable, args[i], args[i+1], args[i+2] ))
            newargs.append( arg.scannable) # to read the actual position
            i=i+3
        
    gda.jython.commands.ScannableCommands.scan(newargs)

def flyscannable(scannable):
    return fly_scannable(scannable);

