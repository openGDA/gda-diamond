'''
A scan that moves a scannable from start position to stop position non-stop or on the fly while collecting data 
    at specified step points.
    If detector exposure time is specified, scannable motor speed will be adjusted during the fly scan.

:Usage:

To perform a flyscan of scannable 'tx' over range (start, stop, step) and measure detector 'det' at each step of 'tx'
    >>>flyscan sx start stop step det [exposure_time] [dead_time] [optional_scannables_to_collect_data_from]
    
To perform a flyscan as the inner most scan of a nested scan
    e.g. perform a scan of 'ty' over range (ystart, ystop, ystep) and at each value of 'ty' perform the above flyscan of 'tx'
    >>>scan sy ystart ystop ystep flyscannable(sx) FlyScanPositionsProvider(sx, start, stop, step) det [exposure_time] [dead_time]

'''
from gda.device.scannable import ScannableBase, ScannableUtils
from gda.scan import ScanPositionProvider, ScanBase
import time
import math
from gda.device import Scannable, Detector
from types import IntType, FloatType
import sys
from time import sleep
from gda.configuration.properties import LocalProperties
from gdascripts.metadata.metadata_commands import meta_add, meta_rm
from gda.jython import InterfaceProvider
from gdascripts.scan.installStandardScansWithProcessing import scan

if LocalProperties.get(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT) == "NexusScanDataWriter":
    from gdascripts.metadata.nexus_metadata_class import meta

SHOW_DEMAND_VALUE=False
        
class FlyScanPosition:
    ''' define a position required by :class:FlyScannable
    '''
    def __init__(self, stop, position, step):
        self.stop = stop
        self.position = position
        self.step = step
        
    def __repr__(self):
        return '[' +str(self.stop)+', '+ str(self.position)+', '+ str(self.step) +']'
    

class   FlyScanPositionsProvider(ScanPositionProvider):
    ''' A scan position provider that provides a list of :class:FlyScanPosition
    '''
    def __init__(self, scannable, start, stop, step):
        self.scannable = scannable
        self.start = start
        self.stop = stop
        self.step = ScanBase.sortArguments(start, stop, step);
        number_steps = ScannableUtils.getNumberSteps(scannable, self.start, self.stop, self.step)
        self.points = []
        self.points.append(start)
        previous_point = start
        for i in range(number_steps):
            next_point = ScannableUtils.calculateNextPoint(previous_point, self.step);
            self.points.append(next_point)
            previous_point = next_point

    def get(self, index):
        max_index = self.size()-1
        if index > max_index:
            raise ValueError("Position %d is outside possible range : %d" % (index, max_index))
        val = self.points[index]
        stoppos = self.stop
        return FlyScanPosition(stoppos, val, self.step);
    
    def size(self):
        return len(self.points)
    
    def __str__(self):
        return "("+",".join(map(str,self.points))+")"
     
    def toString(self):
        return self.__str__()

class ScannableError(Exception):
    pass

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
            raise ScannableError("scannable '%s mus have single inputName" % (self.scannable.getName()))
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
        clock_at_start=time.clock()
        while self.isBusy() and (time.clock()-clock_at_start < self.timeout_secs or math.fabs((self.lastreadPosition-self.requiredPosVal)/self.stepVal)> 4):
            time.sleep(.01)

    def getScannableMaxSpeed(self):
        return self.scannable.getMotor().getMaxSpeed()
        
    def setSpeed(self, speed):
        self.speed=speed        

    def atScanStart(self):
        self.alreadyStarted=False
                    
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
            print("\n")
            print("Start position is reached after %f seconds" % (count))
            self.moveToStartCompleted=True
    
    def atScanEnd(self):
        self.restoreMotorSpeed()
        
    def restoreMotorSpeed(self):
        if self.origionalSpeed is not None:
            print("Restore motor speed from %r to %r" % (self.speed, self.origionalSpeed))
            if self.scannable.isBusy():
                self.scannable.stop()
                sleep(2)
            try:
                self.scannable.setSpeed(self.origionalSpeed)
            except:
                print("Restore motor speed failed with Exception, try again after 5 second sleep")
                sleep(5)
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
                print("change motor speed from %r to %r" % (self.origionalSpeed, self.speed))
                self.scannable.setSpeed(self.speed)
            return
        stop_position = new_position.stop
        print("Move to stop position %f" % stop_position)
        self.scannable.asynchronousMoveTo(stop_position)
        self.alreadyStarted=True
            
        self.stopVal = ScannableUtils.positionToArray(stop_position, self.scannable)[0]
        self.positive = self.stopVal > self.requiredPosVal

    def rawGetPosition(self):
        if self.showDemandValue:
            return [self.scannable.getPosition(), self.requiredPosVal]
        else:
            return self.scannable.getPosition()

#define a global variable for detector dead time - see I16-757
detector_dead_time = 0.0

def setflyscandeadtime(arg):
    '''set global variable 'detector_dead_time' for 'flyscan' function to use - see I16-757 for the reason
    '''
    globals()["detector_dead_time"] = float(arg)
    
def getflyscandeadtime():
    return globals()["detector_dead_time"]

def flyscan(*args):
    ''' A scan that moves a scannable from start position to stop position non-stop or on the fly and collecting data 
    at specified step points.
    
    :usage: 
        flyscan scannable start stop step det [exposure_time] [dead_time] [other_scannables]
    '''
    if len(args) < 4:
        raise SyntaxError("Not enough parameters provided: You must provide '<scannable> <start> <stop> <step>' and may be followed by other optional scannables!")
    
    deadtime_index = -1
    command = "flyscan "
    newargs=[]
    i=0;
    while i< len(args):
        arg = args[i]
        if i==0 :
            if not isinstance(arg, Scannable):
                raise SyntaxError("The first argument is not a Scannable!")
            else:
                startpos=args[i + 1]
                stoppos=args[i+2]
                stepsize=args[i+3]
                number_steps = ScannableUtils.getNumberSteps(arg, startpos, stoppos, stepsize)
                
                newargs, command, flyscannablewraper = create_fly_scannable_and_positions(newargs, command, arg, startpos, stoppos, stepsize)
                command += " ".join(map(str, [startpos, stoppos, stepsize])) + " "
                configure_fly_scannable_extraname(arg, flyscannablewraper)
                i=i+4
        else:
            if i != deadtime_index:
                newargs.append(arg)
            if isinstance(arg, Scannable):
                command += arg.getName() + " "
            if type(arg)==IntType or type(arg)== FloatType:
                command += str(arg) + " "  
            i=i+1
            if isinstance(arg, Detector) and i < len(args) and (type(args[i]) == IntType or type(args[i]) == FloatType):
                i,deadtime_index = parse_detector_parameters_set_flying_speed(args, i, number_steps, startpos, stoppos, flyscannablewraper)

    jython_namespace, existing_info = add_command_metadata(command)
    try:
        scan([e for e in newargs])
    finally:
        remove_command_metadata(jython_namespace, existing_info)

def flyscannable(scannable, timeout_secs=1.):
    return FlyScannable(scannable, timeout_secs)

from gda.jython.commands.GeneralCommands import alias
alias('flyscan')


def create_fly_scannable_and_positions(newargs, command, arg, startpos, stoppos, stepsize):
    flyscannablewraper = FlyScannable(arg)
    flyscannablewraper.startVal = startpos
    newargs.append(flyscannablewraper)
    command += arg.getName() + " "
    newargs.append(FlyScanPositionsProvider(flyscannablewraper.scannable, startpos, stoppos, stepsize))
    return newargs, command, flyscannablewraper


def configure_fly_scannable_extraname(arg, flyscannablewraper):
    flyscannablewraper.showDemandValue = SHOW_DEMAND_VALUE
    if SHOW_DEMAND_VALUE:
        flyscannablewraper.setExtraNames([arg.getInputNames()[0] + "_demand"])
        flyscannablewraper.setOutputFormat(["%.5g", "%.5g"])
    else:
        flyscannablewraper.setExtraNames([])
        flyscannablewraper.setOutputFormat(["%.5g"])


def parse_detector_parameters_set_flying_speed(args, i, numpoints, startpos, stoppos, flyscannablewraper):
#adjust motor speed based on total detector exposure time over the flying range
    if (i + 1) < len(args) and (type(args[i + 1]) == IntType or type(args[i + 1]) == FloatType): # calculate detector total time including dead time given
        total_time = (float(args[i]) + float(args[i + 1])) * numpoints
        deadtime_index = i + 1
    elif globals()['detector_dead_time'] != 0: # I personally don't like this way adding detector dead time but see I16-757 for the reason!
        total_time = (float(args[i]) + globals()['detector_dead_time']) * numpoints
        deadtime_index = -1 # no dead time input
    else:
        total_time = float(args[i]) * numpoints # calculate detector total time without dead times
        deadtime_index = -1 # no dead time input
    motor_speed = math.fabs((float(stoppos - startpos)) / float(total_time))
    max_speed = flyscannablewraper.getScannableMaxSpeed()
    if motor_speed > 0 and motor_speed <= max_speed: #when exposure time is too large, change motor speed to roughly match
        flyscannablewraper.setSpeed(motor_speed)
    elif motor_speed > max_speed: #when exposure time is small enough use maximum speed of the motor
        flyscannablewraper.setSpeed(max_speed)
    return i, deadtime_index


def add_command_metadata(command):
    if LocalProperties.get(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT) == "NexusScanDataWriter":
        meta.addScalar("user_input", "cmd", command)
    if LocalProperties.get(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT) == "NexusDataWriter":
        meta_add("cmd", command)
    cmd_string = "cmd='" + str(command).strip() + "'\n"
    jython_namespace = InterfaceProvider.getJythonNamespace()
    existing_info = jython_namespace.getFromJythonNamespace("SRSWriteAtFileCreation")
    if existing_info:
        ascii_info = str(existing_info) + "\n" + cmd_string
    else:
        ascii_info = cmd_string
    jython_namespace.placeInJythonNamespace("SRSWriteAtFileCreation", ascii_info)
    return jython_namespace, existing_info


def remove_command_metadata(jython_namespace, existing_info):
    if LocalProperties.get(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT) == "NexusScanDataWriter":
        meta.rm("user_input", "cmd")
    if LocalProperties.get(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT) == "NexusDataWriter":
        meta_rm("cmd")
    jython_namespace.placeInJythonNamespace("SRSWriteAtFileCreation", existing_info)


def flyscancn(*args):
    ''' 
    USAGE:
    
    flyscancn scn stepsize numpoints det [exposure_time] [dead_time] [other_scannables]
  
    Performs a scan with specified stepsize and numpoints centred on the current scn position, and returns to original position.
    scn scannable is moving continuousely from start position to stop position non-stop or on the fly and collecting data 
    at specified step points.
    '''
    if len(args) < 3:
        raise SyntaxError("Not enough parameters provided: You must provide '<scannable> <step_size> <number_of_points>' and may be followed by other optional scannables!")
    
    deadtime_index = -1 # signify no dead time input
    command = "flyscancn "
    newargs=[]
    i=0;
    while i< len(args):
        arg = args[i]
        if i==0 :
            if not isinstance(arg, Scannable):
                raise SyntaxError("The first argument is not a Scannable!")
            else:
                current_position = float(arg.getPosition())
                stepsize = float(args[i + 1])
                numpoints = float(args[i + 2])
                intervals = float(numpoints - 1)
                halfwidth = stepsize * intervals/2.
                neg_halfwidth =  stepsize * (-intervals/2.)
                startpos =  current_position + neg_halfwidth
                stoppos = current_position + halfwidth
                
                newargs, command, flyscannablewraper = create_fly_scannable_and_positions(newargs, command, arg, startpos, stoppos, stepsize)
                command += " ".join(map(str, [stepsize, numpoints])) + " "
                configure_fly_scannable_extraname(arg, flyscannablewraper)
                i=i+3
        else:
            if i != deadtime_index:
                newargs.append(arg)
            if isinstance(arg, Scannable):
                command += arg.getName() + " "
            if type(arg) == IntType or type(arg) == FloatType:
                command += str(arg) + " "  
            i = i + 1
            if isinstance(arg, Detector) and i < len(args) and (type(args[i]) == IntType or type(args[i]) == FloatType):
                i,deadtime_index = parse_detector_parameters_set_flying_speed(args, i, numpoints, startpos, stoppos, flyscannablewraper)

    jython_namespace, existing_info = add_command_metadata(command)
    try:
        scan([e for e in newargs])
    finally:
        remove_command_metadata(jython_namespace, existing_info)
        # return to original position
        flyscannablewraper.scannable.moveTo(current_position)
        
alias('flyscancn')
    