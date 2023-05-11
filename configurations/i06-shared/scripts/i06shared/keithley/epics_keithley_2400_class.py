'''
control Keithley 2461 source meter using EPICS Asyn record

Created on 22 Feb 2022

@author: fy65
'''
from gda.epics import CAClient
from gda.device import DeviceException
from time import sleep

# the root name of keithley PV
pv_root = "BL06J-EA-SRCM-01:"
# selected Asyn PVs
command = "COMMAND"  # DBF_STRING
response = "RESPONSE"  # DBF_STRING


class EpicsKeithley2400(object):
    '''
    support source meter Keithley 2461 model.
    Only limited SCPL commands are implemented here!
    '''

    def __init__(self, name, pv_root):
        '''
        Constructor
        '''
        self.name = name
        self.command = CAClient(pv_root + command)
        self.response = CAClient(pv_root + response)

        self.configured = False
        self.last_transfer_mode = 1 #WRITE
        
    def configure(self):
        if self.configured:
            return
        self.command.configure()
        self.response.configure()

        self.configured = True
        
    def send_command_no_reply(self, command):
        self.configure()
        self.command.caput(str(command))
        
     
    def get_response(self):
        self.configure()
        response_string = self.response.caget()
        return response_string.trim()

    def reset(self):
        '''resets the instrument settings to their default values and clears the reading buffers.
        '''
        self.send_command_no_reply('*RST')
        
    def outputOn(self):
        self.send_command_no_reply("OUTP ON")
        
    def outputOff(self):
        self.send_command_no_reply("OUTP OFF")
        
    def isBufferClear(self, buffer_name):
        '''check if buffer is cleared, i.e. the number of readings in buffer is 0
        '''
        self.send_command_no_reply('TRACe:ACTual? "' + str(buffer_name) + '"')
        sleep(1)
        return int(self.get_response()) == 0
    
    def numberOfReadingInBuffer(self, buffer_name):
        self.send_command_no_reply('TRACe:ACTual:END? "' + str(buffer_name) + '"')
        sleep(1)
        return int(self.get_response())
        
    def sourceFunction(self, function):
        '''Set the source function
        '''
        self.send_command_no_reply("SOUR:FUNC " + str(function))
        
    def sourceValue(self, function, val):
        '''set the value for a given function
        '''
        self.send_command_no_reply("SOUR:" + str(function) + " " + str(val))
         
    def sourceVoltageLimit(self, limit):
        '''set voltage limit in source current mode
        '''
        self.send_command_no_reply("SOUR:CURR:VLIM " + str(limit))
       
    def senseFunction(self, function):
        '''Set the measure function
        '''
        self.send_command_no_reply("SENS:FUNC '" + str(function) + "'")
    
    def senseFunctionNPLC(self, function, nplc):
        '''Set NPLC to the measure function
        '''
        self.send_command_no_reply("SENS:" + str(function) + ":NPLC " + str(nplc))
              
    def senseAutoRange(self, function, val):
        '''switch auto range ON/OFF for measurement in the given mode
        '''
        if not (val in ['ON', 'OFF']):
            raise ValueError("input 'val' must be in ['ON', 'OFF']")
        self.send_command_no_reply("SENS:" + str(function) + ":RANG:AUTO " + str(val))
    
    def senseFunctionRange(self, function, val):
        '''set measurement range for the specified function
        '''
        self.send_command_no_reply("SENS:" + str(function) + ":RANG " + str(val))
           
    def senseVoltRsen(self, state):
        ''' set 4-wire remote sense
        '''
        if state not in ['ON', 'OFF']:
            raise ValueError("state must be in ['ON', 'OFF']")
        self.send_command_no_reply("SENS:VOLT:RSEN " + str(state))
        
    def sourcePulseTrain(self, function, pulseLevel, pulseWidth, numberOfPulses, measEnable, timeDelay):
        '''sets up a pulse train for a fixed number of pulse points.
            cmd='SOUR:PULS:TR:CURR bias,pulseLevel,pulseWidth,count,measEnable,bufferName,delay,offtime,xBiasLimit,xPulseLimit,failAbort' 
            bias = 0 (bias level amplitude between, before and after)
            pulseLevel = The amplitude current or voltage from zero (not from the bias level)
            pulseWidth = The time at the amplitude level for each pulse
            count = The number of pulses in the pulse train; default is 1
            measEnable = "off"  (Enable (ON) or disable (OFF) measurements at the top of each pulse)
            bufferName = "defbuffer1" (A string that indicates the reading buffer; the default buffers (defbuffer1))
            delay = 0 (time at bias level before each pulse)
            offtime= time at bias level after each pulse. units:[sec]
            xBiasLimit = 30 (The current or voltage limit for the defined bias level)
            xPulseLimit = 70 (The current or voltage limit for the defined pulse level)
            failAbort = "off" (Determines if the pulse train is stopped immediately if a limit is exceeded)
        '''
        cmd = 'SOUR:PULS:TR:' + str(function) + ' 0, ' + str(pulseLevel) + ', ' + str(pulseWidth) + ', ' + str(numberOfPulses) + ', ' + str(measEnable) + ', "defbuffer1", ' + str(timeDelay) + ', ' + str(timeDelay) + ', 100, 100, off'
        print(cmd)
        self.send_command_no_reply(cmd) 
        
    def sourcePulseLinearSweep(self, function, stop, pulseWidth, timeDelay, numberOfPulses):
        '''sets up a linear pulse sweep for a fixed number of pulse points.
            keithley.sendCmdNoReply('SOUR:PULS:SWE:CURR:LIN bias, start, Current, points, pulseWidth, measEnable, defbuffer1, delay, offtime, count, VlimBias, VLimPulse, failAbort, dual') 
            bias = 0 (bias level amplitude between, before and after)
            start = 0 (The voltage or current source level at which the pulse sweep starts)
            stop = The voltage or current source level at which the pulse sweep stops
            points = 2 (The number of pulse-measure points between the start and stop values of the pulse sweep (2 to 1e6))
            pulseWidth = The time at the amplitude level for each pulse
            measEnable = "off"  (Enable or disable measurements at the top of each pulse)
            bufferName = "defbuffer1" (A string that indicates the reading buffer; the default buffers (defbuffer1))
            delay = 0 (time at bias level before each pulse)
            offtime= time at bias level after each pulse. units:[sec]
            count = (The number of pulse sweeps; default is 1)
            xBiasLimit = 30 (The current or voltage limit for the defined bias level)
            xPulseLimit = 70 (The current or voltage limit for the defined pulse level)
            failAbort = "off" (Determines if the sweep is stopped immediately if a limit is exceeded)
            dual = "off" (Determines if the sweep runs from start to stop and then from stop to start)    
        '''
        cmd = 'SOUR:PULS:SWE:' + str(function) + ':LIN 0, 0, ' + str(stop) + ', 2, ' + str(pulseWidth) + ', off, "defbuffer1", ' + str(timeDelay) + ', ' + str(timeDelay) + ', ' + str(numberOfPulses) + ', 100, 100, off, off'
        print(cmd)
        self.send_command_no_reply(cmd) 
        
    def startPulse(self):
        '''start pulses
        '''
        self.send_command_no_reply("INIT")
    
    def wait(self):
        '''wait for previous commands to execute
        '''
        self.send_command_no_reply("*WAI")
    
    def senseResistanceCompensated(self, val):
        '''enables or disables offset compensation.
        '''
        self.send_command_no_reply("SENS:RES:OCOM " + str(val))
    

    def print_errors_if_any(self):
        errors = self.get_errors()
        if not errors:
            print("%s returns errors: %s" % (self.name, errors))
            raise DeviceException("%s returns errors: %s" % (self.name, errors))

    def readVoltage(self, nplc, timeout = 1.0):
        ''' read voltage after the number of power line cycles (NPLC)
        '''
        self.send_command_no_reply("SENS:VOLT:NPLC " + str(nplc))
        self.send_command_no_reply("OUTP ON")
        self.send_command_no_reply(":READ? 'defbuffer1', sour, read")
        sleep(timeout)
        respose = self.get_response()            
        self.send_command_no_reply("OUTP OFF")
        return respose
        
    def readResistance(self, count, timeout = 1.0):
        '''read resistance for the given number of count
        '''
        self.send_command_no_reply("SENS:COUN " + str(count))
        self.send_command_no_reply("OUTP ON")
        self.send_command_no_reply("TRAC:TRIG 'defbuffer1'")
        self.send_command_no_reply("TRAC:DATA? 1, " + str(count) + ", 'defbuffer1', SOUR, READ")
        sleep(timeout)
        respose = self.get_response()            
        self.send_command_no_reply("OUTP OFF")
        return respose
    
    def readTraceData(self, count, timeout = 1.0):
        '''get data from source, measured reading and relative time of the measurements for a given number of pulses after pulse train.
        '''
        self.send_command_no_reply("OUTP ON")
        self.send_command_no_reply("TRAC:DATA? 1, " + str(count) + ", 'defbuffer1', SOUR, READ, REL")
        sleep(timeout)
        respose = self.get_response()            
        self.send_command_no_reply("OUTP OFF")
        return respose
        
    def sourceReadback(self, function, state):
        '''records the measured source value (ON) or the configured source value (OFF) when making a measurement
        '''
        if function not in ['VOLT', 'CURR']:
            raise ValueError("function must be in ['VOLT', 'CURR']")
        if state not in ['ON', 'OFF']:
            raise ValueError("state must be in ['ON', 'OFF']")
        self.send_command_no_reply("SOUR:" + str(function) + ":READ:BACK " + str(state))
    
        
