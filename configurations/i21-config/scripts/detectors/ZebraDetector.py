'''
Created on 28 Nov 2017

@author: fy65
'''
from gda.device.detector import NXDetector
from types import ListType

MAX_CAPTURE_SIZE=100000 # the maximum length of waveform in EPICS
ZEBRA_PC_CAPTURE=["PC_ENC1", "PC_ENC2", "PC_ENC3", "PC_ENC4", "PC_SYS1", "PC_SYS2", "PC_DIV1", "PC_DIV2", "PC_DIV3", "PC_DIV4", "PC_TIME"];
ZEBRA_PC_CAPTURE_UNIT={"PC_ENC1":'deg', "PC_ENC2":'deg', "PC_ENC3":'deg', "PC_ENC4":'deg', "PC_SYS1":'', "PC_SYS2":'', "PC_DIV1":'', "PC_DIV2":'', "PC_DIV3":'', "PC_DIV4":'', "PC_TIME":'ms'}
TRIGGER_SOURCE=["Position", "Time","External"]
ARM_SOURCE=["Soft","External"]
POSN_TRIG=["Enc1","Enc2","Enc3","Enc4","Enc1-4Av"]
POSN_DIR=["Positive","Negative"]
TIME_UNITS=["ms","s","10s"]


class ZebraDetector(NXDetector):
    '''
    control and run Zebra as detector and capture waveform data from active PC_BIT_CAP fields
    Usage:
     1. must call configureSetup(...) first as the readout and time units must be set before any other method call
     2. Please note Change time unit in EPICS does not update the time values accordingly, i.e. the value stay the same when unit is changed!
     3. call configureGate(...) - step must be greater than width
     4. call configurePulse(...) -  step must be greater than width, delay must be smaller than width, maximum pulse should be gate-width/pulse-step.
     5. Max Pluses greater than gate-width/pulse-step are ignored, less than means no data captured above the set maxPulses! 
    '''

    def __init__(self, name, zebra, collectionStrategy):
        '''
        Constructor
        '''
        self.setName(name)
        self.controller=zebra
        self.collectionStrategy=collectionStrategy
        
    def configure(self):
        super(NXDetector, self).configure()
        
    def configureSetup(self, capture, trig, direction, timeUnit):
        ''' configure the zebra setup fields - defines the  readout  channels and time units used
        @param capture: list of name to be captured - possible values: ["PC_ENC1", "PC_ENC2", "PC_ENC3", "PC_ENC4", "PC_SYS1", "PC_SYS2", "PC_DIV1", "PC_DIV2", "PC_DIV3", "PC_DIV4", "PC_TIME"]
        @param trig: the position trigger- possible values: 0 - Enc1, 1 - Enc2, 2 - Enc3, 3 - Enc4, 4 - Enc1-4Av
        @param direction: position direction - possible values: 0 - Positive:0, 1 - Negative
        @param timeUnit: time unit - possible values: 0 - ms, 1 - s, 2 - 10s
        '''
        self.setCaptureFields(capture)
        self.setPosnTrig(trig)
        self.setPosnDir(direction)
        self.setTimeUnit(timeUnit)
        
    def configureGate(self, source, start, width, numGates, step):
        '''configure the Zebra gate parameters:
        @param source: the trigger source -- 0 - Position, 1 - Time, 2 - External
        @param start: the Gate Start -- the time after arm starts in seconds 
        @param width: the Gate Width -- the time within which data are collected, in seconds
        @param numGates: the Number of gates to collection
        @param step: the Gate Step -- the time in seconds between the starts of 2 adjacent gates, must be greater than gate width!  
        '''
        if numGates > 1 and not (step > width+0.0001):
            #otherwise zebra with hanging during acquisition
            raise ValueError("Gate step must be greater than Gate Width plus 0.0001!")
        self.setGateSource(source)
        self.setGateStart(start)
        self.setGateWidth(width)
        self.setNumberOfGates(numGates)
        if numGates>1:
            self.setGateStep(step)

    def configurePulse(self, source, start, width, step, delay, maxPulses):
        '''configure the zebra Pulse parameters:
        @param source: the Trigger Source -- 0 - Position, 1 - Time, 2 - External
        @param start: the Pulse Start -- the time after gate start in seconds
        @param width: the Pulse Width -- in seconds
        @param step: the Pulse Step -- the time between the starts of 2 adjacent pulse, must be > pulse-width 
        @param delay: the Capture Delay -- the time after the start of pulse at which data are recorded
        @param maxPulses: the Maximum Number of Pulses to collect or sampling   
        '''
        if not (step > width+0.0001):
            raise ValueError("Pulse step must be greater than Pulse Width plus 0.0001!")
        if not (delay < width):
            raise ValueError("Capture delay must be smaller than Pulse Width!")
        self.setPulseSource(source)
        self.setPulseStart(start)
        self.setPulseWidth(width)
        self.setPulseStep(step)
        self.setPulseDelay(delay)
        if maxPulses>MAX_CAPTURE_SIZE:
            raise ValueError("Maximum size of captured waveform is %d. You asked for %d" % (MAX_CAPTURE_SIZE, maxPulses))
        self.setMaxPulses(maxPulses)
        
    def getCollectionTime(self):
        return self.getCollectionStrategy().getAcquireTime()
    
    def setCollectionTime(self, t):
        self.setGateWidth(float(t))
        
    def setNumberOfExposures(self, num):
        self.setNumberOfGates(num)
    
    def getNumberOfExposures(self):
        return self.getNumberOfGates()
    
    def getTotalCollectionTime(self):
        return self.getCollectionTime()*self.getNumberOfExposures()
    
    def getTotalAcquirePeriod(self):
        return self.getCollectionStrategy().getAcquirePeriod()*self.getNumberOfExposures()
    
    def getNumberOfGates(self):
        return int(self.controller.getPCGateNumberOfGates())
    
    def setNumberOfGates(self, num):
        self.controller.setPCGateNumberOfGates(num)
        
    def setCaptureFields(self, capture):
        capbitvalue=0
        if type(capture) is not ListType:
            raise ValueError("'capture' must be a list values from %s" % (ZEBRA_PC_CAPTURE))
        for each in capture:
            capbitvalue +=2**ZEBRA_PC_CAPTURE.index(each)
        self.controller.setPCCaptureBitField(capbitvalue)
        
    def getCaptureFields(self):
        pc_fields_on=[]
        pccapture_bit_field = self.controller.getPCCaptureBitField()
        for each in range(11):
            bitloc=1<<each
            if bitloc & pccapture_bit_field == 1:
                pc_fields_on.append(ZEBRA_PC_CAPTURE[each])
        return pc_fields_on
    
    def setPosnTrig(self,s):
        if s not in POSN_TRIG:
            raise ValueError("Position Trigger must be one of %s" % (POSN_TRIG))
        self.controller.setPCEnc(POSN_TRIG.index(s))
        
    def getPosnTrig(self):
        return POSN_TRIG[int(self.controller.getPCEnc())]
    
    def setPosnDir(self,s):
        if s not in POSN_DIR:
            raise ValueError("Position direction must be one of %s" % (POSN_DIR))
        self.controller.setPCDir(POSN_DIR.index(s))
        
    def getPosnDir(self):
        return POSN_DIR[int(self.controller.getPCDir())]
    
    def reset(self):
        self.controller.reset()
        
    def setTimeUnit(self, s):
        if s not in TIME_UNITS:
            raise ValueError("Time unit must be one of %s" % (TIME_UNITS))
        self.controller.setPCTimeUnit(TIME_UNITS.index(s))
        
    def getTimeUnit(self):
        return TIME_UNITS[int(self.controller.getPCTimeUnit())]
    
    def setArmSource(self, s):
        if s not in ARM_SOURCE:
            raise ValueError("ARm source mus be one of %s " % (ARM_SOURCE))
        self.controller.setPCArmSource(ARM_SOURCE.index(s))
    
    def getArmSource(self):
        return ARM_SOURCE[int(self.controller.getPCArmSource())]
    
    def arm(self):
        self.controller.pcArm()
    
    def disarm(self):
        self.controller.pcDisarm()
        
    def isArmd(self):
        return self.controller.isPCArmed()
        
    def setGateWidth(self, t):
        pctime_unit = self.controller.getPCTimeUnit()
#         if int(self.controller.getPCGateNumberOfGates())>1 and t>=self.getGateStep():
#             raise ValueError("Gate width must be less than Gate Step!")
        if pctime_unit == 0: #ms
            self.controller.setPCGateWidth(t*1000.0)
        elif pctime_unit == 1: #s
            self.controller.setPCGateWidth(t)
        elif pctime_unit == 2: #10s
            self.controller.setPCGateWidth(t/10.0)
            
    def getGateWidth(self):
        return self.getCollectionStrategy().getGateWidth()
            
    def setGateStep(self, t):
        pctime_unit = self.controller.getPCTimeUnit()
#         if t<=self.getGatewidth():
#             raise ValueError("Gate Step must be greater than Gate Width %f!" % (self.getGateWidth()))
        if pctime_unit == 0: #ms
            self.controller.setPCGateStep(t*1000.0)
        elif pctime_unit == 1: #s
            self.controller.setPCGateStep(t)
        elif pctime_unit == 2: #10s
            self.controller.setPCGateStep(t/10.0)

    def getGateStep(self):
        '''return gate step in seconds
        '''
        pcgate_step = float(self.controller.getPCGateStep())
        pctime_unit = self.controller.getPCTimeUnit()
        if pctime_unit == 0: #ms
            return pcgate_step/1000.0
        elif pctime_unit == 1: #s
            return pcgate_step
        elif pctime_unit == 2: #10s
            return pcgate_step*10.0

    def setGateStart(self, t):
        pctime_unit = self.controller.getPCTimeUnit()
        if pctime_unit == 0: #ms
            self.controller.setPCGateStart(t*1000.0)
        elif pctime_unit == 1: #s
            self.controller.setPCGateStart(t)
        elif pctime_unit == 2: #10s
            self.controller.setPCGateStart(t/10.0)

    def getGateStart(self):
        '''return gate start in seconds
        '''
        pcgate_start = float(self.controller.getPCGateStartRBV())
        pctime_unit = self.controller.getPCTimeUnit()
        if pctime_unit == 0: #ms
            return pcgate_start/1000.0
        elif pctime_unit == 1: #s
            return pcgate_start
        elif pctime_unit == 2: #10s
            return pcgate_start*10.0

    def setGateSource(self, s):
        if s not in TRIGGER_SOURCE:
            raise ValueError("Gate source must be one of %s" % TRIGGER_SOURCE)
        self.controller.setPCGateSource(TRIGGER_SOURCE.index(s))
    
    def getGateSource(self):
        return TRIGGER_SOURCE[int(self.controller.getPCGateSource())]
    
    def isGateBusy(self):
        return self.controller.isGateBusy()
    
    def isPulseBusy(self):
        return self.controller.isPulseBusy()
            
    def setPulseSource(self, s):
        if s not in TRIGGER_SOURCE:
            raise ValueError("Pulse source must be one of %s" % TRIGGER_SOURCE)
        self.controller.setPCPulseSource(TRIGGER_SOURCE.index(s))
    
    def getPulseSource(self):
        return TRIGGER_SOURCE[int(self.controller.getPCPulseSource())]
        
    def setPulseWidth(self, t):
        pctime_unit = self.controller.getPCTimeUnit()
#         if t>=self.getPulseStep():
#             raise ValueError("Pulse width must be less than Pulse Step %f!" % (self.getPulseStep()))
        if pctime_unit == 0: #ms
            self.controller.setPCPulseWidth(t*1000.0)
        elif pctime_unit == 1: #s
            self.controller.setPCPulseWidth(t)
        elif pctime_unit == 2: #10s
            self.controller.setPCPulseWidth(t/10.0)

    def getPulseWidth(self):
        pulse_width = float(self.controller.getPCPulseWidthRBV())
        pctime_unit = self.controller.getPCTimeUnit()
        if pctime_unit == 0: #ms
            return pulse_width/1000.0
        elif pctime_unit == 1: #s
            return pulse_width
        elif pctime_unit == 2: #10s
            return pulse_width*10.0
            
    def setPulseStep(self, t):
        pctime_unit = self.controller.getPCTimeUnit()
#         if t<=self.getPulseWidth():
#             raise ValueError("Pulse Step must be greater than Pulse Width %f!" % (self.getPulseWidth()))
        if pctime_unit == 0: #ms
            self.controller.setPCPulseStep(t*1000.0)
        elif pctime_unit == 1: #s
            self.controller.setPCPulseStep(t)
        elif pctime_unit == 2: #10s
            self.controller.setPCPulseStep(t/10.0)

    def getPulseStep(self):
        pulse_step = float(self.controller.getPCPulseStepRBV())
        pctime_unit = self.controller.getPCTimeUnit()
        if pctime_unit == 0: #ms
            return pulse_step/1000.0
        elif pctime_unit == 1: #s
            return pulse_step
        elif pctime_unit == 2: #10s
            return pulse_step*10.0
        
    def setPulseStart(self, t):
        pctime_unit = self.controller.getPCTimeUnit()
#         if t+self.getPulseWidth()>self.getGateWidth():
#             raise ValueError("Pulse Start must be smaller than Gate Width %f minus Pulse Width %f!" % (self.getGateWidth(), self.getPulseWidth()))
        if pctime_unit == 0: #ms
            self.controller.setPCPulseStart(t*1000.0)
        elif pctime_unit == 1: #s
            self.controller.setPCPulseStart(t)
        elif pctime_unit == 2: #10s
            self.controller.setPCPulseStart(t/10.0)

    def getPulseStart(self):
        pulse_start = float(self.controller.getPCPulseStartRBV())
        pctime_unit = self.controller.getPCTimeUnit()
        if pctime_unit == 0: #ms
            return pulse_start/1000.0
        elif pctime_unit == 1: #s
            return pulse_start
        elif pctime_unit == 2: #10s
            return pulse_start*10.0

    def setPulseDelay(self, t):
        pctime_unit = self.controller.getPCTimeUnit()
#         if t>=self.getPulseWidth():
#             raise ValueError("Capture Delay must be less than Pulse Width %f!" % (self.getPulseWidth()))
        if pctime_unit == 0: #ms
            self.controller.setPCPulseDelay(t*1000.0)
        elif pctime_unit == 1: #s
            self.controller.setPCPulseDelay(t)
        elif pctime_unit == 2: #10s
            self.controller.setPCPulseDelay(t/10.0)

    def getPulseDelay(self):
        pulse_delay = float(self.controller.getPCPulseDelayRBV())
        pctime_unit = self.controller.getPCTimeUnit()
        if pctime_unit == 0: #ms
            return pulse_delay/1000.0
        elif pctime_unit == 1: #s
            return pulse_delay
        elif pctime_unit == 2: #10s
            return pulse_delay*10.0

    def setMaxPulses(self, num):
        maxpulses=int(self.getGateWidth()/self.getPulseStep()*self.getNumberOfGates())
        if num>MAX_CAPTURE_SIZE:
            raise ValueError("Maximum size of captured waveform is %d. You asked for %d" % (MAX_CAPTURE_SIZE, num))
        elif num>maxpulses:
            print "Warning: Requested number %d is greater than number of pulses generated %d!" % (num, maxpulses)
        self.controller.setPCPulseMax(num)

    def getMaxPulses(self):
        return int(self.controller.getPCPulseMax())
        
    def setSamplingFrequency(self, freq):
        timestep=1/float(freq)
        pulse_width = self.getPulseWidth()
#         if timestep<pulse_width+0.0001:
#             raise ValueError("Sampling frequency too high, limit is %f" % (1/pulse_width))
        pctime_unit = self.controller.getPCTimeUnit()
        if pctime_unit == 0: #ms
            self.controller.setPCPulseStep(timestep*1000.0)
        elif pctime_unit == 1: #s
            self.controller.setPCPulseStep(timestep)
        elif pctime_unit == 2: #10s
            self.controller.setPCPulseStep(timestep/10.0)
    
    def getSamplingFrequence(self):
        pcpulse_step = float(self.controller.getPCPulseStepRBV())
        pctime_unit = self.controller.getPCTimeUnit()
        if pctime_unit == 0: #ms
            return 1/(pcpulse_step/1000.0)
        elif pctime_unit == 1: #s
            return 1/pcpulse_step
        elif pctime_unit == 2: #10s
            return 1/(pcpulse_step*10.0)
    
    def getCapturedData(self, capture):
        '''get captured data from channel specified         
        @param capture: list of name to be captured - possible values: ["PC_ENC1", "PC_ENC2", "PC_ENC3", "PC_ENC4", "PC_SYS1", "PC_SYS2", "PC_DIV1", "PC_DIV2", "PC_DIV3", "PC_DIV4", "PC_TIME"]
        '''
        return self.collectionStrategy.getCapturedData()
        
#     def setCollectionStrategy(self,collectionStrategy):
#         self.collectionStrategy=collectionStrategy
#         super(NXDetector, self).setCollectionStrategy(collectionStrategy)
        

