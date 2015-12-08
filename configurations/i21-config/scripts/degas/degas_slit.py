#------------------------------------------------------------------------------------------------------------------
# Script to degas a single slit
#
# Move a single slit blade gradually into the beam, by an amount
# calculated using a PID formula (see https://en.wikipedia.org/wiki/PID_controller)
#
# If the pressure exceeds <maxPressure>, return the blade to its starting position
# and terminate the script. Ideally, we should set the parameters so that this never happens.
#
# The script assumes that the blade has been positioned manually at a suitable starting position
# and it will return the slit to this position when it terminates. 
#
# Constructor arguments:
#    blade:          the blade to move
#    bladeMax:       end position for the blade i.e. when it is fully in the beam
#    gauge:          the pressure gauge to monitor
#    frontend:       the front end shutter
#
#    targetPressure: the gas pressure we are aiming for
#    maxPressure:    the maxmum gas pressure we allow before terminating the script
#
#    P, I, D:    coefficients for the proportional, integral and derivative terms respectively
#    Integrator: initial value for the integral of error values
#    Integrator_max, Integrator_min: maximum & minimum values we allow for Integrator 
#------------------------------------------------------------------------------------------------------------------

from exceptions import KeyboardInterrupt
from time import sleep, gmtime, strftime
from gda.jython import ScriptBase

class DegasSlit:
    def __init__(self, blade, bladeMax, gauge, frontend, targetPressure = 2e-8, maxPressure = 5e-8, P = 2.0, I = 0.1, D = 0.3, Integrator = 0.0, Integrator_max = 500, Integrator_min = -500):
        self.blade = blade
        self.bladeMax = float(bladeMax)
        self.gauge = gauge
        self.frontend = frontend

        self.targetPressure = targetPressure
        self.maxPressure = maxPressure
        
        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.Derivator = 0
        self.Integrator = Integrator
        self.Integrator_max = Integrator_max
        self.Integrator_min = Integrator_min
        
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

        self.P_value = self.Kp * error

        self.D_value = self.Kd * ( error - self.Derivator)
        self.Derivator = error

        self.Integrator = self.Integrator + error
        if self.Integrator > self.Integrator_max:
            self.Integrator = self.Integrator_max
        elif self.Integrator < self.Integrator_min:
            self.Integrator = self.Integrator_min
        self.I_value = self.Integrator * self.Ki

        PID = self.P_value + self.I_value + self.D_value

        currentPosition = self.blade.getPosition()
        newPosition = round(currentPosition + (PID * self.direction), 2)
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

        finally:
            self.blade.asynchronousMoveTo(self.initialPosition)
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
