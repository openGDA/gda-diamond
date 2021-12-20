from gda.device.scannable import ScannableBase
from org.slf4j import LoggerFactory
import threading

"""  Class to move a scannable back and forth between two position at specified speed in a background thread :
       atScanStart, atScanLineStart start the motor moves in a background thread
       atScanEnd, atScanLineEnd stop, atCommandFailure stop the thread by setting stopFlag = 1 and calling stop method on scannable being moved
    
    Parameters :
       rangeStart, rangeEnd - range over which motor should be moved
       initialPosition - initial (start) position for the motor. Motor moves from initial position to rangeEnd, then rangeStart, rangeEnd ...
       speed - the speed the motor should move at
       motorStartLine - which 'line' of the scan the motor should start and stop moving. 
       startStopEveryLine - set to true to have the motor start and stop every scan line.
    
    This can be used as a default scannable, so that the moves are started/stopped automatically and start/end of a scan or for a particular 
    line of a scan.
    
"""
class ScannableBouncer(ScannableBase):

    def __init__(self, name, scannableToMove):
        self.setName(name)
        
        self.setScannableToMove(scannableToMove)
        
        self.stopFlag = 0
        self.logger = LoggerFactory.getLogger("ScannableBouncer")
        
        self.setOutputFormat({});
        self.setInputNames({});
        
        self.rangeStart = 0.0
        self.rangeEnd = 1.0
        self.initialPosition = self.rangeStart
        
        self.speed = 0.1
        self.originalMotorSpeed = self.scannableToMove.getSpeed()
        self.motorStartLine = 0
        self.startStopEveryLine = False

    # The scannable that should be moved
    def setScannableToMove(self, scannableToMove):
        self.scannableToMove = scannableToMove
        self.setInputNames(scannableToMove.getInputNames())
        self.setOutputFormat(scannableToMove.getOutputFormat())
            
    def atScanStart(self) :
        self.lineStarts = 0
        if self.motorStartLine == 0 :
            self.logger.info("Starting motor move thread at start of scan", self.getName())
            self.startMotorMove()     

    def atScanLineStart(self):
        self.lineStarts += 1
        self.logger.info("atScanLineStart called on {}. Linestart calls = {}", self.getName(), self.lineStarts)
        if self.lineStarts == self.motorStartLine or self.startStopEveryLine == True :
            self.startMotorMove()

    def atScanLineEnd(self):
        if self.lineStarts == self.motorStartLine or self.startStopEveryLine == True :
            self.logger.info("Stopping {} motor move thread at end of scan part", self.getName())
            self.stopMotorMove()
    
    def atScanEnd(self):
        self.logger.info("Stopping {} motor move thread at end of scan", self.getName())
        self.stopMotorMove()

    # Move scannable to start position (block until move is complete), then start motor move thread
    def startMotorMove(self) :
        self.logger.info("Starting motor move for {}. Waiting for {} to finish", self.getName(), self.scannableToMove.getName())
        # Stop the previously running thread and the scannable
        self.stopFlag = 1
        self.scannableToMove.stop()
        self.scannableToMove.waitWhileBusy()
        self.originalMotorSpeed = self.scannableToMove.getSpeed()
        self.stopFlag = 0
        self.logger.info("Moving {} to initial position ({})", self.scannableToMove.getName(), self.initialPosition)
        self.scannableToMove.stop()
        self.scannableToMove.moveTo(self.initialPosition)
        self.logger.info("Setting {} speed to {}", self.scannableToMove.getName(), self.speed)
        self.scannableToMove.setSpeed(self.speed)
        # Create and start the motor move thread
        x = threading.Thread(target=self.motorMoveFunction, args=(self.scannableToMove, self.rangeStart, self.rangeEnd))
        x.start()
        
    # This function moves the scannable back and forth until stopFlag == 1  
    def motorMoveFunction(self, scn, start, end):
        self.logger.info("Starting motor move thread for {}. Start pos = {}, end pos = {}", self.getName(), start, end)
        while self.stopFlag != 1 :
            self.logger.info("{} position = {}, moving to {}", scn.getName(), scn.getPosition(), end)
            self.scannableToMove.moveTo(end)
            if self.stopFlag == 1 :
                break
            self.logger.info("{} position = {}, moving to {}", scn.getName(), scn.getPosition(), start)
            self.scannableToMove.moveTo(start)
        self.logger.info("Motor move thread for {} finished", self.getName())

    def stopMotorMove(self):
        self.stopFlag = 1
        self.scannableToMove.stop()
        self.scannableToMove.waitWhileBusy()
        #Restore original motor speed
        self.scannableToMove.setSpeed(self.originalMotorSpeed)
   
    def rawAsynchronousMoveTo(self,new_position):
        if self.scannableToMove.isBusy() == False:
            self.scannableToMove.rawAsynchronousMoveTo(new_position)
        else : 
            self.logger.warn("Not moving {} to {} - scannable is already busy", self.scannableToMove.getName(), new_position)
    
    def rawGetPosition(self):
        return None # self.scannableToMove.rawGetPosition()
    
    def isBusy(self):
        return False # self.scannableToMove.isBusy()

    def atCommandFailure(self) :
        self.atScanEnd()

    def stop(self) :
        self.atScanEnd();

    def setRangeStart(self, startRange):
        self.rangeStart = float(startRange)
    
    def setRangeEnd(self, endRange):
        self.rangeEnd = float(endRange)        

    def setInitialPosition(self, initialPosition):
        self.initialPosition = initialPosition
        
    def setSpeed(self, speed):
        self.speed = float(speed)  
    
    def getRangeStart(self):
        return self.rangeStart
    
    def getRangeEnd(self):
        return self.rangeEnd
    
    def getInitialPosition(self):
        return self.initialPosition
    
    def getSpeed(self):
        return self.speed

    def setMotorStartLine(self, motorStartLine):
        self.motorStartLine = motorStartLine
    
    def getMotorStartLine(self):
        return self.motorStartLine
    
    def setStartStopEveryLine(self, startStopEveryLine):
        self.startStopEveryLine = startStopEveryLine

    def getStartStopEveryLine(self):
        return self.startStopEveryLine
