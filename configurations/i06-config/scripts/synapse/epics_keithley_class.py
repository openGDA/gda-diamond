'''
control Keithley 2461 source meter using EPICS Asyn record

Created on 22 Feb 2022

@author: fy65
'''
from gda.epics import CAClient
# the root name of keithley PV
pv_root = "BL06I-EA-SRCM-01:"
# selected Asyn PVs
command = "ASYN.BOUT"  # DBF_CHAR (array)
bytes_sent = "ASYN.NAWT"  # DBF_LONG
max_send_size = "ASYN.OMAX"  # DBF_LONG
response = "ASYN.BINP"  # DBF_CHAR (array)
error = "ASYN.ERRS"  # DBF_STRING
bytes_received = "ASYN.NORD"  # DBF_LONG
max_receive_size = "ASYN.IMAX"  # DBF_LONG
connect = "ASYN.CNCT"   #DBF_RECCHOICE
reading = "READING"

ENCODING = 'utf-8'


class EpicsKeithley2461(object):
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
        self.response = CAClient (pv_root + response)
        self.error = CAClient(pv_root + error)
        self.reading = CAClient(pv_root + reading)
        self.connect = CAClient(pv_root + connect)
        self.configured = False
        
    def configure(self):
        if self.configured:
            return
        self.command.configure()
        self.response.configure()
        self.error.configure()
        self.reading.configure()
        self.connect.configure() 
        self.configured = True
        
    def send_command(self, command):
        self.configure()
        self.command.caputWait(command.encode(ENCODING))
        
    def get_response(self):
        self.configure()
        return self.response.cagetArrayByte().decode(ENCODING)
    
    def get_errors(self):
        self.configure()
        return self.error.caget()
    
    def read(self):
        self.configure()
        #TODO need to check the DBF data type here
        return self.reading.cagetArrayByte().decode(ENCODING)
         
    def reset(self):
        '''resets the instrument settings to their default values and clears the reading buffers.
        '''
        self.send_command('*RST')
        
    def sourceFunction(self, function):
        '''Set the source function
        '''
        self.send_command("SOUR:FUNC " + str(function))
        
    def sourceValue(self, function, val):
        '''set the value for a given function
        '''
        self.send_command("SOUR:" + str(function) + " " + str(val))
         
    def sourceVoltageLimit(self, limit):
        '''set voltage limit in source current mode
        '''
        self.send_command("SOUR:CURR:VLIM " + str(limit))
       
    def senseFunction(self, function):
        '''Set the measure function
        '''
        self.send_command("SENS:FUNC " + str(function))
    
    def senseFunctionNPLC(self, function, nplc):
        '''Set NPLC to the measure function
        '''
        self.send_command("SENS:" + str(function) + ":NPLC " + str(nplc))
              
    def senseAutoRange(self, function, val):
        '''switch auto range ON/OFF for measurement in the given mode
        '''
        if not (val in ['ON', 'OFF']):
            raise ValueError("input 'val' must be in ['ON', 'OFF']")
        self.send_command("SENS:" + str(function) + ":RANG:AUTO " + str(val))
    
    def senseFunctionRange(self, function, val):
        '''set measurement range for the specified function
        '''
        self.send_command("SENS:" + str(function) + ":RANG " + str(val))
           
    def senseVoltRsen(self, state):
        ''' set 4-wire remote sense
        '''
        if not (state in ['ON', 'OFF']):
            raise ValueError("state must be in ['ON', 'OFF']")
        self.send_command("SENS:VOLT:RSEN " + str(state))
        
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
        self.send_command(cmd) 
        
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
        self.send_command(cmd) 
        
    def startPulse(self):
        '''start pulses
        '''
        self.send_command("INIT")
    
    def wait(self):
        '''wait for previous commands to execute
        '''
        self.send_command("*WAI")
    
    def senseResistanceCompensated(self, val):
        '''enables or disables offset compensation.
        '''
        self.send_command("SENS:RES:OCOM " + str(val))
    

    def print_response_and_errors(self):
        response = self.get_response()
        errors = self.get_errors()
        if not response:
            print("response: %s" % response)
        if not errors:
            print("Errors: %s" % errors)

    def readVoltage(self, nplc):
        ''' read voltage after the number of power line cycles (NPLC)
        '''
        self.send_command("SENS:VOLT:NPLC " + str(nplc))
        self.send_command("OUTP ON")
        self.send_command(":READ? 'defbuffer1', sour, read")
        self.print_response_and_errors() 
        self.send_command("OUTP OFF")
        voltage = self.read()
        return voltage
        
    def readResistance(self, count):
        '''read resistance for the given number of count
        '''
        self.send_command("SENS:COUN " + str(count))
        self.send_command("OUTP ON")
        self.send_command("TRAC:TRIG 'defbuffer1'")
        self.send_command("TRAC:DATA? 1, " + str(count) + ", 'defbuffer1', SOUR, READ")
        self.print_response_and_errors()
        self.send_commandy("OUTP OFF")
        resistance = self.read()
        return resistance
    
    def readTraceData(self, count):
        '''get data from source, measured reading and relative time of the measurements for a given number of pulses after pulse train.
        ''' 
        self.send_command("OUTP ON")
        self.send_command("TRAC:DATA? 1, " + str(count) + ", 'defbuffer1', SOUR, READ, REL")
        self.print_response_and_errors()
        self.send_commandy("OUTP OFF")
        data = self.read() 
        return data
        
    def sourceReadback(self, function, state):
        '''records the measured source value (ON) or the configured source value (OFF) when making a measurement
        '''
        if not (function in ['VOLT', 'CURR']):
            raise ValueError("function must be in ['VOLT', 'CURR']")
        if not (state in ['ON', 'OFF']):
            raise ValueError("state must be in ['ON', 'OFF']")
        self.send_command("SOUR:" + str(function) + ":READ:BACK " + str(state))
    
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
        
