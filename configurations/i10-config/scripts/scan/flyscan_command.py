'''
A scan that moves a scannable from start position to stop position non-stop or on the fly while collecting data 
    at specified step points.
    If detector exposure time is specified, scannable motor speed will be adjusted during the fly scan.

:Usage:

To perform a flyscan of scannable 'tx' over range (start, stop, step) and measure detector 'det' at each step of 'tx'
    >>>flyscan tx start stop step det [exposure_time] [optional_scannables_to_collect_data_from]
    
To perform a flyscan as the inner most scan of a nested scan
    e.g. perform a scan of 'ty' over range (ystart, ystop, ystep) and at each value of 'ty' perform the above flyscan of 'tx'
    >>>scan ty ystart ystop ystep flyscannable(tx) FlyScanPositionsProvider(tx, start, stop, step) det [exposure_time]
'''
from gda.device.scannable import ScannableBase, ScannableUtils
from gda.scan import ScanPositionProvider, ScanBase
import gda.jython.commands.ScannableCommands.scan
import time
import math
from gda.device import Scannable, Detector
from types import IntType, FloatType
import sys
from time import sleep

SHOW_DEMAND_VALUE=False
class PositionReader(ScannableBase):
    '''returns the actual position of the given scannable irrespective of its moving state.
    '''
    def __init__(self, scannable):
        self.name = scannable.getName()+"_actual"
        self.inputNames = [scannable.getInputNames() [0]+"_actual"]
        self.scannable=scannable
    
    def getPosition(self):
        return self.scannable.getPosition()
    
    def isBusy(self):
        return False
    
    def asynchronousMoveTo(self):
        pass
    
        
class FlyScanPosition:
    ''' define a position required by :class:FlyScannable
    '''
    def __init__(self, stop, position, step):
        self.stop = stop
        self.position = position
        self.step = step
        
    def __repr__(self):
        return '[' +`self.stop`+', '+ `self.position`+', '+ `self.step`+']'
    

class   FlyScanPositionsProvider(ScanPositionProvider):
    ''' A scan position provider that provides a list of :class:FlyScanPosition
    '''
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

    def get(self, index):
        max_index = self.size()-1
        if index > max_index:
            raise Exception("Position %d is outside possible range : %d" % (index, max_index))
        val = self.points[index]
        stoppos = self.stop
        return FlyScanPosition(stoppos, val, self.step);
    
    def size(self):
        return len(self.points)
    
    def __str__(self):
        return "Scan %s from %s to %s in steps of %s. No of points = %d" % (self.firstScannable.getName(), `self.start`,`self.stop`,`self.step`, self.size() )
     
    def toString(self):
        return self.__str__()
    

class FlyScannable(ScannableBase):
    """
    define a scannable that moves a given scannable from start position to stop position continuously while collecting data at each step point specified.
     
    This class takes a 'standard' scannable and convert it to :class:`FlyScannable`
     
    It takes 1 position input of type :class:`FlyScanPosition`: 
        Each position it receives is a tuple with 
        - the first element being the stop value to be sent to the scannable on first point in scan
        - the second element is the position of the scannable at which data is collected i.e.it reports isBusy = false
        - the third element is the step size of this scannable

    :method: `rawGetPosition` returns the demand value at which the isBusy is to return false    
    
    :usage: scan command 
    from  flyscan_script import flyscannable, FlyScanPositionsProvider
    scan flyscannable(scannable) FlyScanPositionsProvider(scannable, 0, 10, 1) det [exposure_time]
    
    @param param: scannable - the scannable to move in fly mode
    @param param: timeout_secs - time out in seconds, default is 1.0 second
    """
    def __init__(self, scannable, timeout_secs=1.0):
        self.scannable = scannable
        if len( self.scannable.getInputNames()) != 1:
            raise Exception("No support for scannables with inputNames != 1")
        self.name = scannable.getName()+"_fly"
        self.inputNames = [scannable.getInputNames() [0]+"_actual"]
        self.extraNames= []
        self.outputFormats=[ "%.5g", "%.5g"]
        self.level = 3
        self.positive = True
        self.requiredPosVal = 0.
        self.startVal=None
        self.stopVal=0.
        self.stepVal=0.1
        self.timeout_secs = timeout_secs
        self.lastreadPosition=0.
        self.speed=None
        self.origionalSpeed=None
        self.alreadyStarted=False
        self.moveToStartCompleted=False
        self.showDemandValue=False
        
    def getCurrentPositionOfScannable(self):
        return ScannableUtils.positionToArray(self.scannable.getPosition(), self.scannable)[0]
    
    def isBusy(self):
        if not self.scannable.isBusy():
            res = False;
        else:
            self.lastreadPosition = self.getCurrentPositionOfScannable()
            if self.positive:
                res = self.requiredPosVal > self.lastreadPosition
            else:
                res = self.requiredPosVal < self.lastreadPosition
        return res

    def waitWhileBusy(self):
        clockAtStart=time.clock()
        while self.isBusy() and (time.clock()-clockAtStart < self.timeout_secs or math.fabs((self.lastreadPosition-self.requiredPosVal)/self.stepVal)> 4):
            time.sleep(.01)

    def getScannableMaxSpeed(self):
        return self.scannable.getMotor().getMaxSpeed()
        
    def setSpeed(self, speed):
        self.speed=speed        

    def atScanStart(self):
#         self.moveToStart()
        self.alreadyStarted=False
#         if self.speed is not None:
#             self.origionalSpeed= self.scannable.getSpeed()
#             print "change motor speed from %r to %r" % (self.origionalSpeed, self.speed)
#             self.scannable.setSpeed(self.speed)
                    
    def moveToStart(self):
        if self.startVal is not None:
            print( "move to start position %f " % (self.startVal))
            self.scannable.asynchronousMoveTo(self.startVal)
            count=0
            while self.scannable.isBusy():
                sleep(1)
                sys.stdout.write(".")
                count=count+1
                if count % 80 == 0 :
                    sys.stdout.write("\n")
            print
            print "Start position is reached after %f seconds" % (count)
            self.moveToStartCompleted=True
    
    def atScanEnd(self):
        self.restoreMotorSpeed()
        
    def restoreMotorSpeed(self):
        if self.origionalSpeed is not None:
            print "Restore motor speed from %r to %r" % (self.speed, self.origionalSpeed)
            self.scannable.setSpeed(self.origionalSpeed)
            self.origionalSpeed=None
        self.speed=None
        self.alreadyStarted=False
        self.moveToStartCompleted=False
        
    def stop(self):
        self.scannable.stop()
        self.restoreMotorSpeed()
        
    def atCommandFailure(self):
        self.restoreMotorSpeed()
        
    def rawAsynchronousMoveTo(self,new_position):
        if  not  isinstance( new_position,  FlyScanPosition):
            raise TypeError("Only support positions of type FlyScanPosition")
        self.scannable_position = new_position.position
        self.requiredPosVal = ScannableUtils.positionToArray(self.scannable_position, self.scannable)[0]
        self.stepVal = ScannableUtils.positionToArray(new_position.step, self.scannable)[0]
        
        if new_position.stop is None:
            return;
        if self.alreadyStarted:
            return
        elif not self.moveToStartCompleted:
            self.moveToStart()
            if self.speed is not None:
                self.origionalSpeed= self.scannable.getSpeed()
                print "change motor speed from %r to %r" % (self.origionalSpeed, self.speed)
                self.scannable.setSpeed(self.speed)
            return
        stopPosition = new_position.stop
        print "Move to stop position " + `stopPosition`
        self.scannable.asynchronousMoveTo(stopPosition)
        self.alreadyStarted=True
            
        self.stopVal = ScannableUtils.positionToArray(stopPosition, self.scannable)[0]
        self.positive = self.stopVal > self.requiredPosVal
        return

    def rawGetPosition(self):
        if self.showDemandValue:
            return [self.scannable.getPosition(), self.requiredPosVal]
        else:
            return self.scannable.getPosition()


def flyscan(*args):
    ''' A scan that moves a scannable from start position to stop position non-stop or on the fly and collecting data 
    at specified step points.
    
    :usage: 
        flyscan scannable start stop step det [exposure_time] [other_scannables]
    '''
    if len(args) < 4:
        raise Exception("Not enough parameters provided: You must provide '<scannable> <start> <stop> <step>' and may be followed by other optional scannables!")
    newargs=[]
    i=0;
    while i< len(args):
        arg = args[i]
        if i==0 :
            if not isinstance(arg, Scannable):
                raise Exception("The first argument is not a Scannable!")
            else:
                startpos=args[i + 1]
                stoppos=args[i+2]
                stepsize=args[i+3]
                numberSteps = ScannableUtils.getNumberSteps(arg, startpos, stoppos, stepsize)
                flyscannablewraper = FlyScannable(arg)
                flyscannablewraper.startVal=startpos
                newargs.append( flyscannablewraper )
                newargs.append( FlyScanPositionsProvider(flyscannablewraper.scannable, startpos, stoppos, stepsize) )
                flyscannablewraper.showDemandValue=SHOW_DEMAND_VALUE
                if SHOW_DEMAND_VALUE:
                    flyscannablewraper.setExtraNames([arg.getInputNames() [0]+"_demand"])
                    flyscannablewraper.setOutputFormat([ "%.5g", "%.5g"])
                else:
                    flyscannablewraper.setExtraNames([])
                    flyscannablewraper.setOutputFormat([ "%.5g"])
                    
#                 newargs.append( PositionReader(arg) ) # to read the actual position
                i=i+4
        else:
            newargs.append(arg) 
            i=i+1
            if isinstance(arg, Detector):
                if i<len(args) and (type(args[i])==IntType or type(args[i])==FloatType):
                    #detector has exposure time set so need to adjust motor speed to match number of of points
                    totalTime=float(args[i])*numberSteps
                    motorSpeed=math.fabs((float(stoppos-startpos))/float(totalTime))
                    maxSpeed=flyscannablewraper.getScannableMaxSpeed()
                    if motorSpeed>0 and motorSpeed<=maxSpeed:
                        #when exposure time is too large, change motor speed to roughly match
                        flyscannablewraper.setSpeed(motorSpeed)
                    elif motorSpeed>maxSpeed:
                        #when exposure time is small enough use maximum speed of the motor
                        flyscannablewraper.setSpeed(maxSpeed)
        
    gda.jython.commands.ScannableCommands.scan([e for e in newargs])

def flyscannable(scannable, timeout_secs=1.):
    return FlyScannable(scannable, timeout_secs)

from gda.jython.commands.GeneralCommands import alias
alias('flyscan')
