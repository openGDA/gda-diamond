'''
A scan that moves a magnet field scannable from start position to stop position non-stop at a given field ramp rate while collecting data 
    at specified integration time back to back continuously

:Usage:

To perform a fasfieldscan of scannable 'magz' over range (start, stop) with a given ramp rate and measure scalar channels with a given integration time
    >>>fastfieldscan magz start stop ramp_rate integration_time [optional_scannables_to_collect_data_from]
    
To perform a fast field scan as the inner most scan in a nested scan
    e.g. perform a scan of 'sy' over range (ystart, ystop, ystep) and at each value of 'sy' perform the above fastfieldscan of 'magz'
    >>>scan sy ystart ystop ystep magnetflyscannable(magz) FlyScanPositionsProvider(magz, start, stop, step) scalar_scannable integration_time

'''
from gda.device.scannable import ScannableBase, ScannableUtils
import time
import math
from gda.device import Scannable
from types import IntType, FloatType
import sys
from time import sleep
from gdascripts.scan.installStandardScansWithProcessing import scan
from gdascripts.metadata.nexus_metadata_class import meta
from i06shared.scannables.checkbeanscannables import checkbeam
from i06shared.scan.flyscan_command import ScannableError, FlyScanPosition,\
    FlyScanPositionsProvider, configure_fly_scannable_extraname

SHOW_DEMAND_VALUE=False

from magnet.useMagnet import magx, magy, magz
from Diamond.PseudoDevices.SuperconductingMagnetController import magz_ramp_rate, magx_ramp_rate, magy_ramp_rate
SUPPORTED_MAGNET_SCANNABLES = {magx : magx_ramp_rate, magy : magy_ramp_rate, magz : magz_ramp_rate}

from Beamline.U2Scaler8513 import ca61sr, ca62sr, ca63sr, ca64sr, ca65sr
SUPPORTED_DETECTOR_SCANNABLES = [ca61sr, ca62sr, ca63sr, ca64sr, ca65sr]


class MagnetFieldFlyScannable(ScannableBase):
    """
    define a scannable that moves a given magnet field scannable from start position to stop position continuously while collecting data at each step point specified.
     
    This class takes a 'standard' scannable and convert it to :class:`MagnetFieldFlyScannable`
     
    It takes 1 position input of type :class:`FlyScanPosition`: 
        Each position it receives is a tuple with 
        - the first element being the stop value to be sent to the scannable on first point in scan
        - the second element is the position of the scannable at which data is collected i.e.it reports isBusy = false
        - the third element is the step size of this scannable

    :method: `rawGetPosition` returns the demand value at which the isBusy is to return false    
    
    :usage: scan command 
    from  fastFieldScan import magnetflyscannable, FlyScanPositionsProvider
    scan magnetflyscannable(scannable) FlyScanPositionsProvider(scannable, 0, 10, 1) scaler_scannable integration_time
    
    @param param: scannable - the scannable to move in fly mode
    @param ramp_rate  - the magnet field rame rate 
    @param param: timeout_secs - time out in seconds, default is 1.0 second
    """
    def __init__(self, scannable, ramp_rate, timeout_secs=1.0):
        self.scannable = scannable
        self.ramp_rate = ramp_rate
        if len( self.scannable.getInputNames()) != 1:
            raise ScannableError("scannable '%s must have single inputName" % (self.scannable.getName()))
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
        self.rampRate=None
        self.origionalRampRate=None
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
        clock_at_start = time.clock()
        while self.isBusy() and (time.clock()-clock_at_start < self.timeout_secs or math.fabs((self.lastreadPosition-self.requiredPosVal)/self.stepVal) > 4):
            time.sleep(.01)

    def setRampRate(self, speed):
        SUPPORTED_MAGNET_SCANNABLES[self.scannable].asynchronousMoveTo(speed)

    def getRampRate(self):
        return SUPPORTED_MAGNET_SCANNABLES[self.scannable].getPosition()
    
    def atScanStart(self):
        self.alreadyStarted=False
                    
    def moveToStart(self):
        if self.startVal is not None:
            print( "move magnet field to start position %f " % (self.startVal))
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
        if self.origionalRampRate is not None:
            print("Restore magnet field ramp rate from %r to %r" % (self.rampRate, self.origionalRampRate))
            if self.scannable.isBusy():
                self.scannable.stop()
                sleep(2)
            try:
                self.setRampRate(self.origionalRampRate)
            except:
                print("Restore magnet field ramp rate failed with Exception, try again after 5 second sleep")
                sleep(5)
                self.setRampRate(self.origionalRampRate)
            self.origionalRampRate=None
        self.rampRate=None
        self.alreadyStarted=False
        self.moveToStartCompleted=False
        
    def stop(self):
        self.scannable.stop()
        self.restoreMotorSpeed()
        
    def atCommandFailure(self):
        self.restoreMotorSpeed()
    
    def moveTo(self, val):
        self.scannable.moveTo(val)
        
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
            if self.rampRate is not None:
                self.origionalRampRate= self.getRampRate()
                print("change magnet field ramp rate from %r to %r" % (self.origionalRampRate, self.rampRate))
                self.setRampRate(self.rampRate)
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


def fastfieldscan(*args):
    ''' A scan that moves a magnet field scannable from start field position to stop field position non-stop at the given ramp rate and collecting data 
    from scaler channels at specified integration time back to back.
    
    :usage: 
        fastfieldscan magz start_T stop_T ramp_rate_T integration_time_in_seconds [other_scannables]
    '''
    if len(args) < 5:
        raise SyntaxError("Not enough parameters provided: You must provide '<magnet_scannable> <start_field> <stop_field> <field_ramp_rate_in_TPM> <integration_time>' and may be followed by other optional scannables!")
    
    command = "fastfieldscan "
    newargs=[]
    i=0;
    while i< len(args):
        arg = args[i]
        if i==0 :
            if arg not in SUPPORTED_MAGNET_SCANNABLES.keys():
                raise SyntaxError("The first argument is not a magnet Scannable in the list %r!" % [x.getName() for x in SUPPORTED_MAGNET_SCANNABLES.keys()])
            else:
                startpos = args[i + 1]
                stoppos = args[i + 2]
                ramprate = args[i + 3]
                if args[i + 4] in SUPPORTED_DETECTOR_SCANNABLES:
                    #scalar channel scannable is provided in command
                    integrationtime = args[i + 5]
                    stepsize = float(ramprate)*float(integrationtime)/60.0
                    number_steps = ScannableUtils.getNumberSteps(arg, startpos, stoppos, stepsize)
                    newargs, command, flyscannablewraper = create_magnet_field_fly_scannable_and_positions(newargs, command, arg, startpos, stoppos, stepsize, ramprate)
                    newargs.append(args[i + 4])
                    newargs.append(integrationtime)
                    i = i + 6
                if (type(args[i + 4]) == IntType or type(args[i + 4]) == FloatType):
                    # no scalar channel scannable is provided in command
                    integrationtime = args[i + 4]
                    stepsize = float(ramprate)*float(integrationtime)/60.0
                    number_steps = ScannableUtils.getNumberSteps(arg, startpos, stoppos, stepsize)
                    newargs, command, flyscannablewraper = create_magnet_field_fly_scannable_and_positions(newargs, command, arg, startpos, stoppos, stepsize, ramprate)
                    for scn in SUPPORTED_DETECTOR_SCANNABLES:
                        newargs.append(scn)
                        newargs.append(integrationtime)
                    i = i + 5                
                command += " ".join(map(str, [startpos, stoppos, ramprate, integrationtime])) + " "
                configure_fly_scannable_extraname(arg, flyscannablewraper)
        else:
            newargs.append(arg)
            if isinstance(arg, Scannable):
                command += arg.getName() + " "
            if type(arg)==IntType or type(arg)== FloatType:
                command += str(arg) + " "  
            i=i+1
    # if beam chack is provided in command
    original_topup_threshold = None
    if checkbeam in args:
        topup_checker = checkbeam.getDelegate().getGroupMember("checktopup_time")
        original_topup_threshold = topup_checker.minimumThreshold
        topup_checker.minimumThreshold = integrationtime * number_steps + original_topup_threshold
        
    meta.addScalar("user_input", "cmd", command)
    try:
        scan([e for e in newargs])
    finally:
        meta.rm("user_input", "cmd")
        if original_topup_threshold:
            topup_checker = checkbeam.getDelegate().getGroupMember("checktopup_time")
            topup_checker.minimumThreshold = original_topup_threshold
            
def magnetflyscannable(scannable, timeout_secs=1.):
    return MagnetFieldFlyScannable(scannable, timeout_secs)

from gda.jython.commands.GeneralCommands import alias
alias('fastfieldscan')


def create_magnet_field_fly_scannable_and_positions(newargs, command, arg, startpos, stoppos, stepsize, ramprate):
    flyscannablewraper = MagnetFieldFlyScannable(arg, ramprate)
    flyscannablewraper.startVal = startpos
    newargs.append(flyscannablewraper)
    command += arg.getName() + " "
    newargs.append(FlyScanPositionsProvider(flyscannablewraper.scannable, startpos, stoppos, stepsize))
    return newargs, command, flyscannablewraper
