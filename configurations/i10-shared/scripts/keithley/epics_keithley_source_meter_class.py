'''
Support Keithley source meter via EPICS Asyn connection - model 2461 supported first. model 2400 added later

SCPI Command execution rules are as follows:

    - Commands execute in the order that they are presented in the command message. 
    - An invalid command generates an event message and is not executed.
    - Valid commands that precede an invalid command in a command message are executed.
    - Valid commands that follow an invalid command in a command message are ignored.

From Model 2461
    Source and measure order
        - When you are using a remote interface, you should set the measure function first, then set the source
        function, because setting the measure function may change the source function. 
        - Once you have set the source and measure functions, you can change other measure and source
        settings as needed.
        - When setting range, you should first set the limit (compliance) to a value higher than the measure
        range you intend to set.
    
From Model 2400
    Using :TRACe commands to store data
        Use :TRAC:POIN <n> and :TRAG:COUN <n> followed by :TRAC:FEED:CONT NEXT to store data.
        (n = number of readings; 2500 maximum.) Turn on the output with :OUTP ON and
        then send :INIT to take the unit out of idle and store readings. After data is stored,
        send :TRAC:DATA? to access it.
    Using :READ? to store data
        USE :TRAG:COUN <n> to set the number of readings to be stored.
        (n = number of readings, 2500 maximum.) Turn on the output with :OUTP ON and
        then send the :READ? command to trigger and access readings.
        (Once you access these readings, you will still be able to access previously 
        stored :TRACe buffer readings using :TRAC:DATA?.) 
        
Created on 22 Feb 2022
16 Aug 2023 - added support for model 2400

@author: fy65
'''
from gda.epics import CAClient
from gda.device import DeviceException
from time import sleep

# the root name of keithley PV
pv_root = "BL10I-EA-K2400-01:"
# selected Asyn PVs
command = "ASYN.BOUT"  # DBF_CHAR (array of ASCII code)
response = "ASYN.BINP"  # DBF_CHAR (array of ASCII code)
asyn_error = "ASYN.ERRS" # DBF_CHAR (array of ASCII code)
error = "ERR:STRING"  # DBF_CHAR (array of ASCII code)
error_count = "ERR:COUNT" #DBF_DOUBLE
error_clear = "SYST:CLEAR" #DBF_ENUM [0, 1]
connect = "ASYN.CNCT"   #DBF_ENUM [0,1] or ["Disconnect", "Connect"]
transfer_mode = "ASYN.TMOD" #DBF_ENUM [ 0] Write/Read [ 1] Write [ 2] Read [ 3] Flush [ 4] NoI/O
asyn_timeout = "ASYN.TMOT" #DBF_DOUBLE

class EpicsKeithleySourceMeter(object):
    '''
    support Keithley source meter 2461 model and 2400 model.
    Only limited SCPL commands are implemented here!
    '''

    def __init__(self, name, pv_root, model=2461):
        '''
        Constructor
        '''
        self.name = name
        self.command = CAClient(pv_root + command)
        self.response = CAClient(pv_root + response)
        self.transfer_mode = CAClient(pv_root + transfer_mode)
        self.asyn_error = CAClient(pv_root + asyn_error)
        self.error = CAClient(pv_root + error)
        self.error_count = CAClient(pv_root + error_count)
        self.error_clear = CAClient(pv_root + error_clear)
        self.connect = CAClient(pv_root + connect)
        self.asyn_timeout = CAClient(pv_root + asyn_timeout)
        self.model = model
        self.configured = False
        self.last_transfer_mode = 1 #WRITE
        self.use_trace_buffer = True
        self.communication_wait = 0.1
        self.read_wait = 0.1
        self.enable_output_control_per_point = True
        
    def configure(self):
        '''
        configure EPICS connections
        '''
        if self.configured:
            return
        self.command.configure()
        self.response.configure()
        self.transfer_mode.configure()
        self.asyn_error.configure()
        self.error.configure()
        self.error_count.configure()
        self.error_clear.configure()
        self.connect.configure()
        self.asyn_timeout.configure()
        self.communication_wait = 0.1
        self.configured = True
        
    def send_command_no_reply(self, command, timeout = 1.0):
        '''
        send command to device in Write mode - no reply
        '''
        self.configure()
        self.asyn_timeout.caput(timeout)
        if self.last_transfer_mode != 1:
            self.transfer_mode.caput(1)
            self.last_transfer_mode = 1
        sleep(self.communication_wait)
        self.command.caput([ord(c) for c in command + str('\0')])
        sleep(self.communication_wait)
        
    def send_command(self, command, timeout = 1.0):
        '''
        send command in Write/Read mode, expect reply in response
        '''
        self.configure()
        self.asyn_timeout.caput(timeout)
        if self.last_transfer_mode != 0:
            self.transfer_mode.caput(0)
            self.last_transfer_mode = 0
        sleep(self.communication_wait)
        self.command.caput([ord(c) for c in command + str('\0')])
        sleep(self.communication_wait)
        
    def get_response(self, timeout = 1.0):
        '''
        retrieve data from device and convert byte array to String
        '''
        self.configure()
        import time
        timeout_time = time.time() + timeout
        byte_array_char_code = self.response.cagetArrayByte()
        while all( v == 0 for v in byte_array_char_code):
            byte_array_char_code = self.response.cagetArrayByte()
            if time.time() > timeout_time :
                print("timeout after wait data for %f seconds" % timeout)
                break
        response = ''.join(chr(i) for i in byte_array_char_code if i != 0) # convert list of ASCII values to String
        if response == '':
            print(self.get_asyn_error()) #if return is zero, check asyn communication error message
        return response
    
    def get_asyn_error(self):
        self.configure()
        asynerror = self.asyn_error.cagetArrayByte()
        return ''.join(chr(i) for i in asynerror if i != 0)
    
    def get_errors(self):
        '''
        get error text from device
        '''
        self.configure()
        error_in_char_code = self.error.caget()
        return ''.join(chr(i) for i in error_in_char_code if i != 0)
    
    def get_error_count(self):
        '''
        get the number of errors in the device
        '''
        self.configure()
        return float(self.error_count.caget())
    
    def clear_error(self):
        '''
        clear errors from the device
        '''
        self.configure()
        self.error_clear.caput(1)
        
    def reset(self):
        '''resets the instrument settings to their default values and clears the reading buffers.
        '''
        if self.enable_output_control_per_point:
            self.send_command_no_reply("*RST")
        
    def outputOn(self):
        '''
        switch on output before acquiring data or do measurements
        '''
        self.send_command_no_reply("OUTP ON")
        
    def outputOff(self):
        '''
        switch off output after acquiring data or do measurements
        '''
        self.send_command_no_reply("OUTP OFF")
    
    def clearBuffer(self, buffer_name=None):
        '''
        clear the named buffer 
        - model 2461 supports buffer named as  "defbuffer1", 
        - model 2400 doesn't not supported named buffer, so should be None
        '''
        if self.model == 2461:
            self.send_command_no_reply('TRACe:CLEar "' + str(buffer_name) + '"')
        if self.model == 2400:
            self.send_command_no_reply('TRACe:CLEar')
        
    def isBufferClear(self, buffer_name=None):
        '''check if buffer is cleared, i.e. the number of readings in buffer is 0
        - model 2461 supports buffer named as  "defbuffer1", 
        - model 2400 doesn't not supported named buffer, so should be None
        '''
        if self.model == 2461:
            self.send_command('TRACe:ACTual? "' + str(buffer_name) + '"')
        if self.model == 2400:
            self.send_command('TRACe:POINts:ACTual?')
        # sleep required otherwise get_response() returns '?'
        while self.get_response() == '?' or self.get_response() == '@':
            sleep(self.read_wait) 
        return int(self.get_response()) == 0
    
    def numberOfReadingInBuffer(self, buffer_name):
        if self.model == 2641:
            self.send_command('TRACe:ACTual:END? "' + str(buffer_name) + '"')
        if self.model == 2400:
            raise AttributeError("Command  'TRACe:ACTual:END? 'is not supported in model 2400")
        return int(self.get_response())
    
    def set_compliance(self, func, level):
        if self.model == 2400:
            self.send_command_no_reply(":SENSe:" + str(func) + ":PROT " + str(level))
            
    def specify_data_elements(self, *args):
        '''
        specify the elements to be included in the data string. You can specify one to five elements. Valid elements are VOLT, CURR, RES,TIME, STAT 
        '''
        if self.model == 2400:
            valid_inputs = ["VOLT", "CURR", "RES", "TIME", "STAT"]
            separator = ","
            if set(args).issubset(valid_inputs):
                arg = separator.join(args)
            else:
                raise ValueError("input value '%s' not valid. Valid value must be in %s" % (args, valid_inputs))
            command = ":FORMat:ELEMents " + arg   
            self.send_command_no_reply(command)
        if self.model == 2461:
            raise AttributeError("Command '%s' is not supported in model 2461" % command)
    
    def acquire_data(self, count):
        '''
        trigger measurement and read data
        '''
        if self.enable_output_control_per_point:
            self.outputOn()
        if self.model == 2461:
            self.send_command_no_reply('TRACe:TRIGger "defbuffer1"')
            while self.isBufferClear("defbuffer1"):
                sleep(self.read_wait)
            self.send_command('TRACe:DATA? 1, ' + str(count) + ', "defbuffer1", SOUR, READ')
            # sleep required otherwise get_response() returns '@'
            while  self.get_response() == '@':
                sleep(self.read_wait)
        if self.model == 2400:
            if not self.use_trace_buffer:
                self.send_command("READ?")
            if self.use_trace_buffer:
                self.send_command_no_reply(":INIT")
                self.send_command(":TRACE:DATA?")
                # sleep required otherwise get_response() returns '+'
                while self.get_response() == '+':
                    sleep(self.read_wait)
        if self.enable_output_control_per_point:
            self.outputOff()
                
    def prepare_trace_buffer(self, count):
        '''
        configure trace buffer
        '''
        if self.model == 2400:
            self.clearBuffer()
            while not self.isBufferClear():
                sleep(self.read_wait)
            if self.use_trace_buffer:
                self.send_command_no_reply(":TRAC:FEED SENS") #Store raw readings in buffer.
                self.send_command_no_reply(":TRAC:POIN " + str(count)) #Store count readings in buffer.
                self.send_command_no_reply(":TRAC:FEED:CONT NEXT") #Enable buffer.
            self.send_command_no_reply(":TRIG:COUN " + str(count)) #Trigger count number.
        if self.model == 2461:
            self.clearBuffer("defbuffer1")
            while not self.isBufferClear("defbuffer1"):
                sleep(0.1)
        
    def sourceFunction(self, function):
        '''Set the source function
        '''
        self.send_command_no_reply("SOUR:FUNC " + str(function))
        
    def sourceValue(self, function, val):
        '''set the value for a given function
        '''
        self.send_command_no_reply("SOUR:" + str(function) + " " + str(val))
         
    def sourceLimit(self, func, limit):
        '''set voltage limit in source current mode
        '''
        if str(func) in ['VOLT', 'VOLTage']:
            command = "SOUR:"+ str(func) + ":ILIM " + str(limit)
        if str(func) in ['CURR', 'CURRent']:
            command = "SOUR:"+ str(func) + ":VLIM " + str(limit)
        if self.model == 2461:
            self.send_command_no_reply(command)
        if self.model == 2400:
            raise AttributeError("Command '%s' is not supported in model %d" % (command,self.model))
    
    def source_mode(self, func, mode):
        command = "SOUR:"+ str(func) + ":MODE " + str(mode)
        if self.model == 2400:
            self.send_command_no_reply(command)
        if self.model == 2461:
            raise AttributeError("Command '%s' is not supported in model 2461" % command)
       
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
    
    def senseCount(self, count):
        command = 'SENSe:COUNT ' +  str(count)
        if self.model == 2461:
            self.send_command_no_reply(command)
        if self.model == 2400:
            raise AttributeError("Command '%s' is not supported in model %d" % (command, self.model))
           
    def senseRsense(self, func, state):
        ''' set 4-wire remote sense
        '''
        if not (state in ['ON', 'OFF']):
            raise ValueError("state must be in ['ON', 'OFF']")
        self.send_command_no_reply("SENS:" + str(func) + ":RSEN " + str(state))
        
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
        if self.model == 2461:
            self.send_command_no_reply(cmd)
        if self.model == 2400:
            raise AttributeError("Method is not yet implemented for model 2400!") 
        
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
        if self.model == 2461:
            self.send_command_no_reply(cmd) 
        if self.model == 2400:
            raise AttributeError("Method is not yet implemented for model 2400!") 
        
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
        if self.model == 2461:
            self.send_command_no_reply("SENS:VOLT:NPLC " + str(nplc))
            self.send_command_no_reply("OUTP ON")
            self.send_command(":READ? 'defbuffer1', sour, read", timeout)
            if self.get_error_count() > 0:
                print("Error count is not zero, please clear the error count in EPICS before use the last command again!")
            respose = self.get_response(timeout)            
            self.send_command_no_reply("OUTP OFF")
        if self.model == 2400:
            raise AttributeError("This method is not yet implemented in model 2400")
        return respose
        
    def readResistance(self, count, timeout = 1.0):
        '''read resistance for the given number of count
        '''
        if self.model == 2461:
            self.send_command_no_reply("SENS:COUN " + str(count))
            self.send_command_no_reply("OUTP ON")
            self.send_command_no_reply("TRAC:TRIG 'defbuffer1'")
            self.send_command("TRAC:DATA? 1, " + str(count) + ", 'defbuffer1', SOUR, READ", timeout)
            if self.get_error_count() > 0:
                print("Error count is not zero, please clear the error count in EPICS before use the last command again!")
            respose = self.get_response(timeout)            
            self.send_command_no_reply("OUTP OFF")
        if self.model == 2400:
            raise AttributeError("This method is not yet implemented in model 2400")
        return respose
    
    def readTraceData(self, count, timeout = 1.0):
        '''get data from source, measured reading and relative time of the measurements for a given number of pulses after pulse train.
        '''
        if self.model == 2461:
            self.send_command_no_reply("OUTP ON")
            self.send_command("TRAC:DATA? 1, " + str(count) + ", 'defbuffer1', SOUR, READ, REL", timeout)
            if self.get_error_count() > 0:
                print("Error count is not zero, please clear the error count in EPICS before use the last command again!")
            respose = self.get_response(timeout)            
            self.send_command_no_reply("OUTP OFF")
        if self.model == 2400:
            raise AttributeError("This method is not yet implemented in model 2400")
        return respose
        
    def sourceReadback(self, function, state):
        '''records the measured source value (ON) or the configured source value (OFF) when making a measurement
        '''
        if function not in ['VOLT', 'CURR']:
            raise ValueError("function must be in ['VOLT', 'CURR']")
        if state not in ['ON', 'OFF']:
            raise ValueError("state must be in ['ON', 'OFF']")
        command = "SOUR:" + str(function) + ":READ:BACK " + str(state)
        if self.model == 2461:
            self.send_command_no_reply(command)
        if self.model == 2400:
            raise AttributeError("Command '%s' is not supported in model 2400" % command)
    
    def connect(self):
        '''connect to Keithley device
        '''
        self.configure()
        self.connect.caputWait("Connect")
    
    def disconnect(self):
        '''disconnect to the Keithley device
        '''
        self.configure()
        self.connect.caputWait("Disconnect")
        
