#------------------------------------------------------------------------------------------------------------------
# Script to prevent pressure in the sample chamber reach too high level during warning up
#
# Adjust ramp rate during warming up so to prevent vacuum pressure exceed the set maximum.
# The amount to adjust is calculated using a PID formula (see en.wikipedia.org/wiki/PID_controller).
# However, to avoid pressure spikes, the speed of ramp is limited to <maxRampRate>.
#
# If the pressure exceeds <maxPressure>, return the ramp rate to its starting position, and terminate the script.
# Ideally, we should set the parameters so that this never happens.
#
# The script assumes that the ramp rate of the cryostat has been
# positioned manually at a suitable starting position. When it terminates, it will
# return the device to the starting position.
#
# Pressures are in millibars, ramp rate in K/min
#
# Constructor arguments:
#  mandatory:
#    cryostat:           the cryostat that control the temperature
#    maxRampRate:        Maximum ramp rate of the cryostat set by users
#    gauge:              the pressure gauge to monitor
#
#  optional:
#    minPressure:        the pressure below which we assume no significant outgassing is taking place
#    targetPressure:     optimum vacuum pressure for cryostat warning up
#    pressureDeadband:   if the pressure is only slightly above or below the target pressure, don't move the device
#    maxPressure:        maximum vacuum pressure we allow 
#    minRampRate:        minimum ramp rate set by users

#    PID factor
#        The default values have been set by experimentation on i21 for degas.py
#        Please be careful if you intend to change them
#------------------------------------------------------------------------------------------------------------------

import sys
from exceptions import KeyboardInterrupt
from time import sleep, gmtime, strftime
import threading

class cryostatPID(threading.Thread):
    def __init__(self, cryostat, gauge, maxRampRate = 10.0, minRampRate=0.05,
                 minPressure = 5e-9, targetPressure = 3e-8, pressureDeadband = 2e-9, maxPressure = 5e-8,
                 Kp = 5e7, Ki = 10000, Kd = 0.3, Derivator=0.0, Integrator=0.0, Integrator_max=500, Integrator_min=-500):

        threading.Thread.__init__(self)
        self.cryostat = cryostat
        self.rampMax = float(maxRampRate)
        self.gauge = gauge
        self.minRampRate = minRampRate
        self.maxRampRate = maxRampRate 

        self.minPressure = minPressure
        self.targetPressure = targetPressure
        self.pressureDeadband = pressureDeadband
        self.maxPressure = maxPressure

        # PID factors
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.Derivator = Derivator
        self.Integrator = Integrator
        self.Integrator_max = Integrator_max
        self.Integrator_min = Integrator_min
        
        # Deduce direction of travel from current and end positions
        self.initialPosition = self.cryostat.getRampRate()
        if (self.rampMax > self.initialPosition):
            self.direction = 1
        else:
            self.direction = -1
        
        # Frequency of monitoring pressure (seconds)
        self.monitorFreq = 0.1
        
        # Minimum number of monitoring cycles before moving
        self.minRampRateChangeCycles = 100
        self.finished=False
        


    # Check whether the device is at its maximum position, taking account
    # of its direction of travel.
    def atRampMax(self):
        position = self.cryostat.getRampRate()
        if (self.direction > 0):
            if (position >= self.rampMax):
                return True
        else:
            if (position <= self.rampMax):
                return True
        return False
    
    
    # Update position, based on current & target pressures
    def updatePosition(self, pressure):
        difference = self.targetPressure - pressure

        # Don't move if pressure is within the deadband
        if (abs(difference) < self.pressureDeadband):
            self.printMessage("pressure is at " + str(pressure) + ", don't need to change ramp rate")
            return

        self.P_value = self.Kp * difference
        self.D_value = self.Kd * (difference - self.Derivator)
        
        self.Derivator = difference
        self.Integrator = self.Integrator + difference
        if self.Integrator > self.Integrator_max:
            self.Integrator = self.Integrator_max
        elif self.Integrator < self.Integrator_min:
            self.Integrator = self.Integrator_min
        self.I_value = self.Integrator * self.Ki

        # Calculate PID
        PID = self.P_value + self.I_value + self.D_value
        
        # Limit the forward (into beam) movement
        if (PID > 0):
            PID = min(PID, self.maxRampRate) 

        currentPosition = self.cryostat.getRampRate()
        newPosition = round(currentPosition + (PID * self.direction), 3)
    
        # Don't try to move the device beyond its maximum ramp rate 
        if (self.direction > 0):
            newPosition = min(newPosition, self.rampMax)
        else:
            newPosition = max(newPosition, self.rampMax)
        
        if (newPosition == currentPosition):
            self.printMessage("pressure is at " + str(pressure) + ", not changing ramp rate (at max ramp rate)")
        else:
            if newPosition<0.0:
                newPosition=self.minRampRate
            self.printMessage("pressure is at " + str(pressure) + ", change ramp rate to " + str(newPosition))
            self.cryostat.setRampRate(newPosition)
        
    def stop(self):
        self.finished=True
        
    def run(self):
        self.report()
        cyclesBeforeMove = 0
        self.finished = False
        
        try:
            while (self.finished == False):
                pressure = self.gauge.getPosition()

                if (pressure > self.maxPressure):
                    self.printMessage("pressure too high: terminating script")
                    self.finished = True
                        
                elif (pressure < self.minPressure and self.atRampMax()):
                    self.printMessage("pressure below minimum at max ramp rate: terminating script")
                    self.finished = True
                    
                elif (cyclesBeforeMove > 0):
                    cyclesBeforeMove = cyclesBeforeMove - 1
                    
                else:
                    self.updatePosition(pressure)
                    cyclesBeforeMove = self.minRampRateChangeCycles - 1
                    
                sleep(self.monitorFreq)
            
        except KeyboardInterrupt:
            self.printMessage("script terminated by user")
        except:
            self.printMessage("script terminated by exception: " + str(sys.exc_info()[0]))
        finally:
            try:
                self.printMessage("moving ramp rate back to initial position")
                self.cryostat.setRampRate(self.initialPosition)
            except:
                self.printMessage("exception changing ramp rate: " + str(sys.exc_info()[0]))
            finally:
                self.report()


    def printMessage(self, message):
        print strftime("%Y-%m-%d %H:%M:%S", gmtime()), message


    def report(self):
        print ""
        print "--------------- Cryostat PID ------------------------"
        print self.cryostat.getRampRate()
        print "initialPosition : ", self.initialPosition
        print "rampMax : ", self.rampMax
        print "maxRampRate : ", self.maxRampRate
        print "direction : ", self.direction
        print ""
        print self.gauge
        print ""
        print "minPressure : ", self.minPressure
        print "targetPressure : ", self.targetPressure
        print "pressureDeadband : ", self.pressureDeadband
        print "maxPressure : ", self.maxPressure
        print ""
        print "Kp : ", self.Kp
        print "Ki : ", self.Ki
        print "Kd : ", self.Kd
        print "--------------------------------------------------"
        print ""
