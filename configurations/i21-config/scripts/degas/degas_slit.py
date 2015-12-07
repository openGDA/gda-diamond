#------------------------------------------------------------------------------------------------------------------
# Script to degas a single slit
#
# Move a single slit blade into the beam stepwise, waiting for the pressure
# to drop below <lowerBound> before advancing it by the next step.
#
# If the pressure exceeds <upperBound>, retract the blade completely,
# wait for the pressure to drop, halve the step size, then advance it as before.
# Ideally, we should set the initial step size so that this never happens.
#
# Constructor arguments:
#    blade:     the blade to move
#    startPos:  starting position for the blade.
#               This should be such that the edge is (just) outside the beam.
#    endPos:    end position for the blade i.e. when it is fully in the beam
#    direction: the direction which takes the blade towards the centre of the beam.
#               Any positive number will be treated as meaning that the position should be incremented,
#               any negative number that it should be decremented.
#    gauge:     the pressure gauge to monitor
#------------------------------------------------------------------------------------------------------------------

from exceptions import KeyboardInterrupt
from time import sleep
from gda.jython import ScriptBase

class DegasSlit:
    def __init__(self, blade, startPos, endPos, direction, gauge, frontend):
        self.blade = blade
        self.startPos = float(startPos)
        self.endPos = float(endPos)
        self.setDirection(direction)
        self.gauge = gauge
        self.frontend = frontend
        
        # Pressure bounds: see above
        self.lowerBound = 1e-8
        self.upperBound = 5e-8
        
        # Frequency of monitoring pressure (seconds)
        self.monitorFreq = 0.1
        
        # Minimum number of monitoring cycles between steps
        self.minCycles = 100
        
        # Step size (mm)
        self.stepSize = 0.1


    def setDirection(self, direction):
        if (direction == 0):
            raise RuntimeError("direction must not be zero")
        elif (direction > 0):
            self.direction = 1
        else:
            self.direction = -1


    def run(self):
        self.report()

        print "moving to start position"
        self.blade.moveTo(self.startPos)
        cyclesBeforeMove = 0
        finished = False

        
        try:
            while (finished == False):
                pressure = self.gauge.getPosition()
#                 print self.blade, self.gauge
                
                if (pressure > self.upperBound):
                    # Pressure is too high: move blade out and wait for pressure to drop
                    print "pressure too high: resetting blade"
                    self.blade.moveTo(self.startPos)
                    self.stepSize = self.stepSize / 2.0
                    while (self.gauge.getPosition() > self.lowerBound):
#                         print "waiting for pressure to drop"
                        print self.blade, self.gauge
                        sleep(self.monitorFreq)
                    cyclesBeforeMove = 0
                        
                elif (pressure < self.lowerBound):
                    # Pressure is low: advance the blade, unless we have recently done this,
                    # or the blade is at its maximum position
                    if (self.blade.getPosition() >= self.endPos):
                        print "process finished"
                        finished = True 
                    elif (cyclesBeforeMove > 0):
#                         print "pressure low but we cannot move yet: cyclesBeforeMove ", cyclesBeforeMove
                        cyclesBeforeMove = cyclesBeforeMove - 1
                    else:
                        newPos = self.blade.getPosition() + (self.stepSize * self.direction)
                        print "moving blade to ", newPos
                        self.blade.moveTo(newPos)
                        cyclesBeforeMove = self.minCycles

                else:
#                     print "stay steady"
                    cyclesBeforeMove = cyclesBeforeMove - 1

                    
                # Wait before checking again
                sleep(self.monitorFreq)
            
        except KeyboardInterrupt:
            print "Process terminated by user"

        finally:
            self.blade.asynchronousMoveTo(self.startPos)
            self.frontend.moveTo('Close')
            self.report()

        
    def report(self):
        print "--------------- DegasSlit ------------------------"
        print "blade = ", self.blade
        print "startPos = ", self.startPos
        print "endPos = ", self.endPos
        print "direction = ", self.direction
        print "gauge = ", self.gauge
        print "lowerBound = ", self.lowerBound
        print "upperBound = ", self.upperBound
        print "stepSize = ", self.stepSize
        print "--------------------------------------------------"
        print ""
