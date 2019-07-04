'''
functions for controlling Keithley 2461 source meter.

It defines some, but not all, of control methods for a given Keithley instance.

Created on 9 Nov 2018

@author: fy65
'''

from userDevices.ASCIIComunicator import ASCIIComunicator

# support for Keithley model 2461
with ASCIIComunicator("kei2461", "10.106.8.8", 5025, '\n') as kei2461:
    kei2461.configure()

def keithleyReset(keithley):
    '''resets the instrument settings to their default values and clears the reading buffers.
    '''
    keithley.sendCmdNoReply('*RST')

def keithleySourceCurrentMode(keithley):
    '''Set the source function to current.
    '''
    keithley.sendCmdNoReply("SOUR:FUNC CURR")

def keithleySenseVoltageMode(keithley):
    '''Set the measure function to voltage.
    '''
    keithley.sendCmdNoReply("SENS:FUNC 'VOLT'")

def keithleyAutoRange(keithley):
    '''switch on voltage auto range for measurement
    '''
    keithley.sendCmdNoReply("SENS:VOLT:RANG:AUTO ON")
    
def keithleyConfigurePulse(keithley, Current, pulseWidth, timeDelay, NumberOfPulses):
    '''sets up a linear pulse sweep for a fixed number of pulse points.
        keithley.sendCmdNoReply('SOUR:PULS:SWE:CURR:LIN bias, start, Current, points, pulseWidth, measEnable, defbuffer1, delay, offtime, NumberOfPulses, VlimBias, VLimPulse, failAbort, dual') 
        bias = 0 (bias level amplitude between, before and after)
        start = 0 (amplitude of the beginning of the sweep)
        Current = amplitude of the current pulse. units: [Ampere]
        points = 2 (number of measurement points in the pulse)
        measEnable = "off"  (if you want to measure during the pulse)
        defbuffer1 = "defbuffer1"
        delay = 0 (time at bias level before each pulse)
        offtime= time at bias level after each pulse. units:[sec]
        NumberOfPulses = (equal to the number of pulses requsted)
        VlimBias = 70 (compliance voltage while at bias level. units: [Volt])
        VlimPulse = 70 (compliance voltage during pulse)
        failAbort = "off" (decides, if everything is aborted when one of the levels is exceeded)
        dual = "off" (decides if the sweep goes back and forth or not, doesn't make sense for a single pulse amplitude)    
    '''
    #cmd='SOUR:PULS:SWE:CURR:LIN 0, 0, '+str(Current)+', 2, '+str(pulseWidth) + ', off, "defbuffer1", '+str(timeDelay)+', '+ str(timeDelay)+', '+ str(NumberOfPulses) +', 30, 30, off, off'
    cmd='SOUR:PULS:TR:CURR 0, '+str(Current)+', '+str(pulseWidth) + ', '+ str(NumberOfPulses) + ', off, "defbuffer1", '+str(timeDelay)+', '+ str(timeDelay)+', 100, 100, off'
    print cmd
    keithley.sendCmdNoReply(cmd) 
    
def keithleyStartSweep(keithley):
    #send the pulses
    keithley.sendCmdNoReply("INIT")

def keithleyWait(keithley):
    '''postpones the execution of subsequent commands until all previous overlapped commands are
        finished.
    '''
    return keithley.sendCmdNoReply("*WAI")

def keithleyConfigureReadback(keithley, state):
    '''
    '''
    if not (state in ['ON', 'OFF']):
        raise Exception("Input must be in ['ON', 'OFF']")
    keithley.sendCmdNoReply("SOUR:VOLT:READ:BACK "+ str(state))