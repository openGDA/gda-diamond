from gda.device.scannable import ScannableBase, ScannableUtils
from gda.scan import ScanPositionProvider, ScanBase
import gda.jython.commands.ScannableCommands.scan
import time
import math

class   flyscan_positionsOneWay(ScanPositionProvider):
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
            nextPoint = ScannableUtils.calculateNextPoint(previousPoint, self.step);
            self.points.append(flyscan_position(None, nextPoint))
            previousPoint = nextPoint
        self.forward=True

    def get(self, index):
        max_index = self.size()-1
        if index > max_index:
            raise Exception("Position %d is outside possible range : %d" % (index, max_index))
        self.forward = True
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


class   flyscan_positions(ScanPositionProvider):
    def __init__(self, firstScannable, start, stop, step):
        self.firstScannable = firstScannable
        self.start = start
        self.stop = stop
        self.step = ScanBase.sortArguments(start, stop, step);
        numberSteps = ScannableUtils.getNumberSteps(firstScannable, self.start, self.stop, self.step)
        self.points = []
        self.points.append(start)
        previousPoint = start
        for i in range(numberSteps):
            nextPoint = ScannableUtils.calculateNextPoint(previousPoint, self.step);
            self.points.append(nextPoint)
            previousPoint = nextPoint
        self.forward=True

    def get(self, index):
        max_index = self.size()-1
        if index > max_index:
            raise Exception("Position %d is outside possible range : %d" % (index, max_index))
        stoppos=None
        if self.forward:
            val = self.points[index]
            if index == 0:
                stoppos = self.stop
            if index == max_index:
                self.forward = False
        else:
            val = self.points[max_index-index]
            if index == 0:
                stoppos = self.start
            if index == max_index:
                self.forward = True
        return flyscan_position(stoppos, val, self.step);
    
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
    def __init__(self, scannable, timeout_secs=0.01):
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
        self.stepVal=0.1
        self.timeout_secs = timeout_secs
        self.lastreadPosition=0.
        
    def getCurrentPositionOfScannable(self):
        return  ScannableUtils.positionToArray(self.scannable.getPosition(), self.scannable)[0]
    def isBusy(self):
        if not self.scannable.isBusy():
#            print "Scannable is not busy"
            res = False;
        else:
            self.lastreadPosition = self.getCurrentPositionOfScannable()
#            print "currentVal:"+`currentVal`
            if self.positive:
                res = self.requiredPosVal > self.lastreadPosition
            else:
                res = self.requiredPosVal < self.lastreadPosition
                
#        print "isBusy returns " +`res`
        return res
    def waitWhileBusy(self):
        clockAtStart=time.clock()
        while self.isBusy() and (time.clock()-clockAtStart < self.timeout_secs or math.fabs((self.lastreadPosition-self.requiredPosVal)/self.stepVal)> 4):
            time.sleep(self.timeout_secs/2)
        
    def rawAsynchronousMoveTo(self,new_position):
        if  not  isinstance( new_position,  flyscan_position):
            raise TypeError("I only support positions of type flyscan_position_provider")
        self.scannable_position = new_position.position
        self.requiredPosVal = ScannableUtils.positionToArray(self.scannable_position, self.scannable)[0]
        self.stepVal = ScannableUtils.positionToArray(new_position.step, self.scannable)[0]
        
#        print "rawAsynchronousMoveTo " + `self.scannable_position` + "  requiredPosVal:%s" +`self.requiredPosVal`
        if new_position.stop is None:
            return;
        """
        first move to start"
        """
        self.scannable.waitWhileBusy()
#        print "calling moveTo " + `self.scannable_position`
        self.scannable.moveTo(self.scannable_position)
        stopPosition = new_position.stop
#        print "calling asynchronousMoveTo " + `stopPosition`
        self.scannable.asynchronousMoveTo(stopPosition)
#        if self.scannable.isBusy():
#            print "scannable is busy"
#        else:
#            print "scannable is not busy!"
            
        self.stopVal = ScannableUtils.positionToArray(stopPosition, self.scannable)[0]
        self.positive = self.stopVal > self.requiredPosVal
        return

    def rawGetPosition(self):
        return self.requiredPosVal

class flyscan_position:
    def __init__(self, stop, position, step):
        self.stop = stop
        self.position = position
        self.step = step

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

def flyscannable(scannable, timeout_secs=0.01):
    return fly_scannable(scannable, timeout_secs);

class WaitForScannableAtLineEnd(ScannableBase):
    '''NOTE: Should be called ...atLineStart'''
    
    def __init__(self, name, scannable_to_check):
        self.name = name
        self.scn = scannable_to_check
        self.inputNames = []
        self.extraNames = []
        self.outputFormat = []
        self.sleep_time = 10 # seconds
        
    def getPosition(self):
        return None
    
    def isBusy(self):
        return False
    
    def atScanLineStart(self):
        print self.name, "atScanStart starting"
        print self.name, "waiting for ", self.scn.name, " to become unbusy"
        self.scn.waitWhileBusy()
        print self.name, "sleeping for ", self.sleep_time, " s"
        time.sleep(self.sleep_time)
        print self.name, "waiting for ", self.scn.name, " to become unbusy"
        self.scn.waitWhileBusy()
        print self.name, "atScanStart complete"
        
