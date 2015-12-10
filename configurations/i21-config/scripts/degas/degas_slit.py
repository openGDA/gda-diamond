#------------------------------------------------------------------------------------------------------------------
# Script to degas a single slit
#
# Move a single slit blade gradually into the beam, by an amount
# calculated using a PID formula (see en.wikipedia.org/wiki/PID_controller)
#
# If the pressure exceeds <maxPressure>, return the blade to its starting position, close
# the front end and terminate the script.
# Ideally, we should set the parameters so that this never happens.
#
# The script assumes that the blade has been positioned manually at a suitable starting position
# and it will return the slit to this position when it terminates. 
#
# Constructor arguments:
#    blade:          the blade to move
#    bladeMax:       end position for the blade i.e. when it is fully in the beam
#    gauge:          the pressure gauge to monitor
#    frontend:       the front end shutter
#------------------------------------------------------------------------------------------------------------------

import sys
from exceptions import KeyboardInterrupt
from time import sleep, gmtime, strftime
from gda.jython import ScriptBase

class DegasSlit:
    def __init__(self, blade, bladeMax, gauge, frontend):
        self.blade = blade
        self.bladeMax = float(bladeMax)
        self.gauge = gauge
        self.frontend = frontend

        # The following values have been set by experimentation on i21
        # Please be careful if you intend to change them
        
        # Gas pressure we are aiming for
        self.targetPressure = 3e-8
        
        # Pressure deadband: if the pressure is only slightly above or below the
        # target pressure, don't move the blade
        self.pressureDeadband = 0.2e-8
        
        # Maximum gas pressure we allow before terminating the script and closing the front end
        self.maxPressure = 5e-8
        
        # PID factors
        self.Kp = 5e7
        self.Ki = 10000
        self.Kd = 0.3
        self.Derivator = 0
        self.Integrator = 0
        self.Integrator_max = 500
        self.Integrator_min = -500
        
        # Limit the distance that the blade can move into the slit in one movement.
        # This is designed to prevent sudden pressure as the beam reaches an unconditioned part of the blade.
        # There is no limit on movement out of the beam.
        self.maxForwardMovement = 0.05  # mm 
        
        # Deduce direction of slit travel from current and end positions
        self.initialPosition = self.blade.getPosition()
        if (self.bladeMax > self.initialPosition):
            self.direction = 1
        else:
            self.direction = -1
        
        # Frequency of monitoring pressure (seconds)
        self.monitorFreq = 0.1
        
        # Minimum number of monitoring cycles before moving blade
        self.minCycles = 100
        
        # Pressure below which we assume no significant outgassing is taking place 
        self.minPressure = 1e-8


    # Check whether the blade is at its maximum position, taking account
    # of its direction of travel.
    def atBladeMax(self):
        position = self.blade.getPosition()
        if (self.direction > 0):
            if (position >= self.bladeMax):
                return True
        else:
            if (position <= self.bladeMax):
                return True
        return False
    
    
    # Update slit position, based on current & target pressures
    def updatePosition(self, pressure):
        error = self.targetPressure - pressure

        self.Derivator = error
        self.Integrator = self.Integrator + error
        self.Integrator = min(self.Integrator, self.Integrator_max)
        self.Integrator = max(self.Integrator, self.Integrator_min)
        
        # Don't move if pressure is within the deadband
        if (abs(error) < self.pressureDeadband):
            self.printMessage("pressure " + str(pressure) + ", not moving blade")
            return

        # Calculate PID
        self.P_value = self.Kp * error
        self.D_value = self.Kd * (error - self.Derivator)
        self.I_value = self.Integrator * self.Ki
        PID = self.P_value + self.I_value + self.D_value
        
        # Limit the forward (into beam) movement
        if (PID > 0):
            PID = min(PID, self.maxForwardMovement) 

        currentPosition = self.blade.getPosition()
        newPosition = round(currentPosition + (PID * self.direction), 3)
    
        # Don't try to move the blade beyond its maximum (fully closed) position 
        if (self.direction > 0):
            newPosition = min(newPosition, self.bladeMax)
        else:
            newPosition = max(newPosition, self.bladeMax)
            
        self.printMessage("pressure " + str(pressure) + ", moving blade to " + str(newPosition))
        self.blade.moveTo(newPosition)
        

    def run(self):
        self.report()
        cyclesBeforeMove = 0
        finished = False
        
        try:
            while (finished == False):
                pressure = self.gauge.getPosition()
                
                if (pressure > self.maxPressure):
                    self.printMessage("pressure too high: terminating script")
                    finished = True
                        
                elif (pressure < self.minPressure and self.atBladeMax()):
                    self.printMessage("outgassing finished: terminating script")
                    finished = True
                    
                elif (cyclesBeforeMove > 0):
                    cyclesBeforeMove = cyclesBeforeMove - 1
                    
                else:
                    self.updatePosition(pressure)
                    cyclesBeforeMove = self.minCycles - 1
                    
                sleep(self.monitorFreq)
            
        except KeyboardInterrupt:
            self.printMessage("script terminated by user")
            
        except:
            self.printMessage("script terminated by exception: " + str(sys.exc_info()[0]))

        finally:
            try:
                self.printMessage("moving blade back to initial position")
                self.blade.asynchronousMoveTo(self.initialPosition)
            except:
                self.printMessage("exception moving blade: " + str(sys.exc_info()[0]))
            finally:
                self.printMessage("closing front end")
                self.frontend.moveTo('Close')
                self.report()


    def printMessage(self, message):
        print strftime("%Y-%m-%d %H:%M:%S", gmtime()), message


    def report(self):
        print ""
        print "--------------- DegasSlit ------------------------"
        print "blade = ", self.blade
        print "initialPosition = ", self.initialPosition
        print "bladeMax = ", self.bladeMax
        print "direction = ", self.direction
        print "gauge = ", self.gauge
        print "frontend = ", self.frontend
        print "targetPressure = ", self.targetPressure
        print "maxPressure = ", self.maxPressure
        print "Kp = ", self.Kp
        print "Ki = ", self.Ki
        print "Kd = ", self.Kd
        print "--------------------------------------------------"
        print ""
