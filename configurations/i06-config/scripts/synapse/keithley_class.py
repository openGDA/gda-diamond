'''
Created on 14 Nov 2018

@author: fy65
'''
from userDevices.ASCIIComunicator import ASCIIComunicator

class Keithley2461(object):
    '''
    support source meter Keithley 2461 model.
    Only limited SCPL commands are implemented here!
    '''

    def __init__(self, name, ipaddress, port, terminator):
        '''
        Constructor
        '''
        self.communicator=ASCIIComunicator(name,ipaddress,port,terminator,self)
        
    def reset(self):
        '''resets the instrument settings to their default values and clears the reading buffers.
        '''
        self.communicator.sendCmdNoReply('*RST')
        
    def sourceFunction(self, function):
        '''Set the source function
        '''
        self.communicator.sendCmdNoReply("SOUR:FUNC " + str(function))
        
    def sourceValue(self, function, val):
        '''set the value for a given function
        '''
        self.communicator.sendCmdNoReply("SOUR:" + str(function)+ " "+ str(val))
        
    def sourceVoltageLimit(self, limit):
        '''set voltage limit in source current mode
        '''
        self.communicator.sendCmdNoReply("SOUR:CURR:VLIM " + str(limit))
       
    def senseFunction(self, function):
        '''Set the measure function
        '''
        self.communicator.sendCmdNoReply("SENS:FUNC '" +str(function)+"'")
    
    def senseFunctionNPLC(self, function, nplc):
        '''Set NPLC to the measure function
        '''
        self.communicator.sendCmdNoReply("SENS:" +str(function)+":NPLC " + str(nplc))
              
    def senseAutoRange(self, function, val):
        '''switch auto range ON/OFF for measurement in the given mode
        '''
        if not (val in ['ON', 'OFF']):
            raise Exception("input 'val' must be in ['ON', 'OFF']")
        self.communicator.sendCmdNoReply("SENS:"+str(function)+":RANG:AUTO "+str(val))
    
    def senseFunctionRange(self, function, val):
        '''set measurement range for the specified function
        '''
        self.communicator.sendCmdNoReply("SENS:"+str(function)+":RANG "+str(val))
           
    def senseVoltRsen(self, state):
        ''' set 4-wire remote sense
        '''
        if not (state in ['ON', 'OFF']):
            raise Exception("state must be in ['ON', 'OFF']")
        self.communicator.sendCmdNoReply("SENS:VOLT:RSEN "+str(state))
        
    def sourcePulseTrain(self, function, pulseLevel, pulseWidth, numberOfPulses, measEnable, timeDelay):
        '''sets up a pulse train for a fixed number of pulse points.
            cmd='SOUR:PULS:TR:CURR bias,pulseLevel,pulseWidth,count,measEnable,bufferName,delay,offtime,xBiasLimit,xPulseLimit,failAbort' 
            bias = 0 (bias level amplitude between, before and after)
            pulseLevel = The amplitude current or voltage from zero (not from the bias level)
            count = The number of pulses in the pulse train; default is 1
            measEnable = "off"  (Enable (ON) or disable (OFF) measurements at the top of each pulse)
            bufferName = "defbuffer1" (A string that indicates the reading buffer; the default buffers (defbuffer1))
            delay = 0 (time at bias level before each pulse)
            offtime= time at bias level after each pulse. units:[sec]
            xBiasLimit = 30 (The current or voltage limit for the defined bias level)
            xPulseLimit = 70 (The current or voltage limit for the defined pulse level)
            failAbort = "off" (Determines if the pulse train is stopped immediately if a limit is exceeded)
        '''
        cmd='SOUR:PULS:TR:'+str(function)+' 0, '+str(pulseLevel)+', '+str(pulseWidth) + ', '+ str(numberOfPulses) + ', '+str(measEnable)+', "defbuffer1", '+str(timeDelay)+', '+ str(timeDelay)+', 100, 100, off'
        print cmd
        self.communicator.sendCmdNoReply(cmd) 
        
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
        cmd='SOUR:PULS:SWE:'+str(function)+':LIN 0, 0, '+str(stop)+', 2, '+str(pulseWidth) + ', off, "defbuffer1", '+str(timeDelay)+', '+ str(timeDelay)+', '+ str(numberOfPulses) +', 100, 100, off, off'
        print cmd
        self.communicator.sendCmdNoReply(cmd) 
        
    def startPulse(self):
        '''start pulses
        '''
        self.communicator.sendCmdNoReply("INIT")
    
    def wait(self):
        '''wait for previous commands to execute
        '''
        self.communicator.sendCmdNoReply("*WAI")
    
    def senseResistanceCompensated(self, val):
        self.communicator.sendCmdNoReply("SENS:RES:OCOM "+str(val))
    
    def readVoltage(self, nplc):
        self.communicator.sendCmdNoReply("SENS:VOLT:NPLC "+str(nplc))
        self.communicator.sendCmdNoReply("OUTP ON")
        voltage=self.communicator.send(":READ? 'defbuffer1', sour, read")
        self.communicator.sendCmdNoReply("OUTP OFF")
        return voltage
        
    def readResistance(self, count):
        self.communicator.sendCmdNoReply("SENS:COUN " + str(count))
        self.communicator.sendCmdNoReply("OUTP ON")
        self.communicator.sendCmdNoReply("TRAC:TRIG 'defbuffer1'")
        resistance=self.communicator.send("TRAC:DATA? 1, " + str(count)+ ", 'defbuffer1', SOUR, READ")
        self.communicator.sendCmdNoReply("OUTP OFF")
        return resistance
    
    def readTraceData(self, count):
        '''get data from source, measured reading and relative time of the measurements for a given number of pulses after pulse train.
        '''
        data=self.communicator.send("TRAC:DATA? 1, " + str(count)+ ", 'defbuffer1', SOUR, READ, REL")
        return data
        
        
    def sourceReadback(self, function, state):
        '''records the measured source value (ON) or the configured source value (OFF) when making a measurement
        '''
        if not (function in ['VOLT','CURR']):
            raise Exception("function must be in ['VOLT', 'CURR']")
        if not (state in ['ON', 'OFF']):
            raise Exception("state must be in ['ON', 'OFF']")
        self.communicator.sendCmdNoReply("SOUR:"+str(function)+":READ:BACK "+str(state))
    
    def closeConnection(self):
        '''close the socket connect to Keithley device
        '''
        self.communicator.close()
    
    def isConnectionClosed(self):
        '''check if connection is closed or not
        '''
        return self.communicator.isClosed()
        