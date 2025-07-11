'''
Script to warm up a cryostat
    
warm up a cryostat (e.g. increase demand temperature) gradually by adjusting ramp rate 
to LIMIT the time period, or prevent if possible, that vacuum pressure exceeds the set maximum <maxPressure>.
 
Algorithm implemented:
 1. ON - control of the cryostat's ramp rate based on the pressure reading only when temperature is increased;
 2. OFF - the loop control should be switched off when the temperature reaches its demand target temperature; 
 3. Initialisation - When the loop starts, the ramp rate should always start at the minimum ramp rate;
 4. Increment - After every loop in which vacuum pressure does not exceed 1/pressureFactor of <maxPressure>, ramp rate should be doubled for the next loop;
 5. Decrement - When pressure exceeds 1/pressureFactor of the maximum pressure, change ramp rate to minimum ramp rate, and then repeat step 4;
 6. Delay - Since pressure reacts on the time scale of seconds below 120 K, a sleep time is required in the loop so that the speed of adjustments of ramp rate are matched with the speed of the changes in pressure.
 7. Cooldown - when requested temperature less than current, set ramp rate to 100.0K/min
 8. If the temperature of tsample, tshield, or tcryostat is between 130 and 160 K, A different maximum ramp rate is required.
 
Pressures are in millibars, ramp rate in K/min

Constructor arguments:
 mandatory:
    name:               name of the scannable
    cryostat:           the cryostat that controls the temperature
    gauge:              the pressure gauge to monitor

 optional:
    minRampRate:        minimum ramp rate (default is 0.05K/min)
    maxRampRate:        Maximum ramp rate of the cryostat (default is 10.0K/min)
    maxPressure:        maximum vacuum pressure permitted (defult is 5e-8)
    pressureFactor:     The divisor of maximum pressure used to adjust the pressure limit in loop (default is 2)
    sleepTime:          the sleep time in loop ( Default is 10.0 seconds)
    tolerance:          the accuracy used to determine temperature is in position (Default is 0.001K)
    lowThreashold:      the low threshold of a temperature range that requires different maximum ramp rate (Default is 130.0K)
    highThreashold:     the high threshold of a temperature range that requires different maximum ramp rate (Default is 160.0K)
    maxRampRate130_160: maximum ramp rate for temperature between 130.0K and 160.0K (Default is 1.0)
    
'''

import sys
from exceptions import KeyboardInterrupt
from time import sleep, strftime, localtime, time
from gda.device.scannable import ScannableBase
import math
from java.lang import Runnable, Thread  # @UnresolvedImport

class CryostatWarmUp(ScannableBase, Runnable):
    def __init__(self, name, cryostat, gauge, maxRampRate = 10.0, minRampRate=0.05, 
                 maxPressure = 5e-8, pressureFactor=2.0, sleepTime=10.0, tolerance=0.001, lowThreshold=130.0, highThreshold=160.0, maxRampRate130_160=1.0):

        self.setName(name)
        self.setInputNames([name])
        self.cryostat = cryostat
        self.gauge = gauge
        self.minRampRate = minRampRate
        self.maxRampRate = maxRampRate 
        self.pressureFactor=pressureFactor
        self.maxPressure = maxPressure
        self.tolerance_demand=tolerance
        self.tolerance_sample=tolerance
        self.lowThreshold=lowThreshold
        self.highThreshold=highThreshold
        self.MAX_RAMP_RATE=maxRampRate
        self.MAX_RAMP_RATE_130_160=maxRampRate130_160

        # Frequency of monitoring pressure (seconds)
        self.sleepTime = sleepTime
        self.finished=False
        self.firstTime=False
        self.temperatutePrintIntervalInSeconds=10.0
        self.warmup=True
        self.CRYO_SAMPLE_DIFFERENCE=0.0
        
    def setSleepTime(self, t):
        self.sleepTime=t
    
    def getSleepTime(self):
        return self.sleepTime

    def asynchronousMoveTo(self, new_temp):
        heater_range =self.cryostat.getHeaterRange()
        if new_temp > 100 and heater_range != 3:
            self.cryostat.setHeaterRange(3)
        elif new_temp <= 100 and heater_range != 2:
            self.cryostat.setHeaterRange(2)
        existingTemperature=self.cryostat.getCurrentDemandTemperature()
        if new_temp > existingTemperature:
            #1. ON - only when temperature is increased;
            self.thread=Thread(self,"Thread: "+self.getName())
            self.thread.start()
            self.cryostat.asynchronousMoveTo(new_temp)
            self.firstTime=True
            self.warmup=True
        elif new_temp < existingTemperature:
            self.cryostat.setRampRate(100.0)
            self.cryostat.asynchronousMoveTo(new_temp - self.CRYO_SAMPLE_DIFFERENCE)
            self.firstTime=True
            self.warmup=False
        else:
            self.printMessage("Already at the requested temperature")
        
    def getPosition(self):
            return self.cryostat.getPosition()[1] #sample temperature
    
    def isBusy(self):
        if self.firstTime:
            sleep(0.5) #sleep required to give time for lakeshore to react to asynchronousMoveTo
            self.firstTime=False
        if self.warmup:
            return math.fabs(self.cryostat.getTargetDemandTemperature() - self.cryostat.getCurrentDemandTemperature()) > self.tolerance_demand or math.fabs(float(self.cryostat.getPosition()[1]) - self.cryostat.getTargetDemandTemperature()) > self.tolerance_sample
        else:
            return math.fabs(float(self.cryostat.getPosition()[1]) - (self.cryostat.getTargetDemandTemperature()+self.CRYO_SAMPLE_DIFFERENCE)) > self.tolerance_sample
         
    def stop(self):
        currentdDemand=self.cryostat.getCurrentDemandTemperature()
        self.cryostat.moveTo(currentdDemand)
        self.finished=True
        self.firstTime=False
        
    def run(self):
        self.report()
        self.finished = False
        lastprinttime=0.0
        # 3. Initialisation - When the loop starts, the ramp rate should always start at the minimum ramp rate;
        self.cryostat.setRampRate(self.minRampRate)
        sleep(0.5) #sleep required to give time for lakeshore to react
        try:
            while (self.finished == False):
                #I21-640
                tsample=self.cryostat.getTemperature(0)  # @UndefinedVariable
                tshield=self.cryostat.getTemperature(1)
                tcryostat=self.cryostat.getTemperature(2)

                if time() - lastprinttime >= self.temperatutePrintIntervalInSeconds:
                    self.printMessage("Current sample temperature is %.1f" % (tsample))
                    lastprinttime=time()
                
                if (tsample>self.lowThreshold and tsample<self.highThreshold) or (tshield>self.lowThreshold and tshield<self.highThreshold) or (tcryostat>self.lowThreshold and tcryostat<self.highThreshold):
                    self.maxRampRate=self.MAX_RAMP_RATE_130_160
                else:
                    self.maxRampRate=self.MAX_RAMP_RATE
                
                #I21-420   
                pressure = self.gauge.getPosition()

                if (pressure > self.maxPressure/self.pressureFactor):
                    #5. Decrement - pressure exceeds half of <maxPressure>, set ramp rate to <minRampRate>
                    self.cryostat.setRampRate(self.minRampRate)
                    self.printMessage("pressure %.3E is greater than 1/%.0f of maximum pressure %.3E, reduce ramp rate to minimum %.1f" % (pressure, self.pressureFactor, self.maxPressure, self.minRampRate))
                       
                elif (pressure < self.maxPressure/self.pressureFactor):
                    #4. Increment - pressure does not exceed half of <maxPressure>, ramp rate should be doubled
                    ramp_rate = self.cryostat.getRampRate()
                    if ramp_rate*2 <= self.maxRampRate:
                        self.cryostat.setRampRate(ramp_rate*2)
                        self.printMessage("pressure %.3E is below 1/%.0f of maximum pressure %.3E, double the ramp rate to %.1f" % (pressure, self.pressureFactor, self.maxPressure, ramp_rate*2))
                    else:
                        self.cryostat.setRampRate(self.maxRampRate)
                        self.printMessage("pressure %.3E is below 1/%.0f of maximum pressure %.3E, set the ramp rate to maximum %.1f" % (pressure, self.pressureFactor, self.maxPressure, self.maxRampRate))
                #6. Delay - Since pressure reacts on the time scale of seconds below 120 K, a sleep time is required in the loop so that the speed of adjustments of ramp rate are matched to the speed of the changes in pressure    
                sleep(self.sleepTime)
                if math.fabs(self.cryostat.getTargetDemandTemperature() - self.cryostat.getCurrentDemandTemperature()) <= self.tolerance_demand:
                    #2. Off - stop looping when the temperature reaches its demand target temperature
                    break;
            
        except KeyboardInterrupt:
            self.printMessage("script terminated by user")
        except:
            self.printMessage("script terminated by exception: " + str(sys.exc_info()))
        finally:
            try:
                self.printMessage("Set ramp rate to minimum after temperature reached to target.")
                self.cryostat.setRampRate(self.minRampRate)
                sleep(0.5) #sleep required to give time for lakeshore to react
            except:
                self.printMessage("exception changing ramp rate: " + str(sys.exc_info()))
            finally:
                self.report()


    def printMessage(self, message):
        print strftime("%Y-%m-%d %H:%M:%S", localtime()), message


    def report(self):
        print ""
        print "--------------- Cryostat Warm Up ------------------------"
        print "currentRampRate : %f" % self.cryostat.getRampRate()
        print "minRampRate     : %f" % self.minRampRate
        print "maxRampRate     : %f" % self.maxRampRate
        print ""
        print "currentPressure : %E" % self.gauge.getPosition()
        print "maxPressure     : %E" % self.maxPressure
        print "--------------------------------------------------"
        print ""
