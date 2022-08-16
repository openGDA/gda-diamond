'''
define scannables that interact with Keithley 2461 source meter using SCPI (Standard Commands for Programmable Instrument) commands

SCPI Command execution rules are as follows:

1. Commands execute in the order that they are presented in the command message. 
2. An invalid command generates an event message and is not executed.
3. Valid commands that precede an invalid command in a command message are executed.
4. Valid commands that follow an invalid command in a command message are ignored.

Source and measure order
When you are using a remote interface, you should set the measure function first, then set the source
function, because setting the measure function may change the source function. 
Once you have set the source and measure functions, you can change other measure and source
settings as needed.
When setting range, you should first set the limit (compliance) to a value higher than the measure
range you intend to set.

'''
from gda.device.scannable import ScannableMotionBase
from time import sleep
from gda.device import DeviceException

class Keitlhey2461Resistance(ScannableMotionBase):
    '''Create a scannable to read resistance measurement from keithley 2461 source meter'''
    
    def __init__(self, name,keithley):
        self.setName(name)
        self.keithley = keithley
        self.setInputNames([name])
        self.setOutputFormat(['%3.3f'])
        self.setLevel(5)
        self.timeout = 0.2
        self.NPLC = 0.5
        
    def atScanStart(self):
        self.keithley.outputOn()
        
    def atScanEnd(self):
        self.keithley.outputOff()
           
    def getPosition(self):
        self.keithley.send_command_no_reply(":SENS:RES:NPLC " + str(self.NPLC), self.timeout)
        self.keithley.send_command(":MEASure:RESistance?", self.timeout)
        resistance_value = self.keithley.get_response(self.timeout)
        print("Resistance value is %s", resistance_value)   
        return float(resistance_value)

    def asynchronousMoveTo(self,time):
        raise DeviceException("resistance scannable is read only")
        
    def isBusy(self):
        return False;

 
class Keitlhey2461Current(ScannableMotionBase):
    '''Create a scannable to control and read current measurement from keithley 2461 source meter'''
    def __init__(self, name, keithley, tolerance = 0.1):
        self.setName(name)
        self.keithley = keithley
        self.setInputNames([name])
        self.setOutputFormat(['%3.3f'])
        self.setLevel(5)
        self.timeout = 0.2 # EPICS Asyn communication timeout
        self.NPLC = 0.5 #the number of power line cycles range from 0.01 to 10 with 0.01 resulting in the fastest reading rates and 10 resulting in the lowest reading noise.
        self.target = None
        self.current_tolerance = tolerance
        
    def atScanStart(self):
        self.keithley.outputOn()
        
    def atScanEnd(self):
        self.keithley.outputOff()
           
    def getPosition(self):
        self.keithley.send_command_no_reply(":SENS:CURR:NPLC " + str(self.NPLC), self.timeout)
        self.keithley.send_command(":MEASure:CURRent?", self.timeout)
        current_value = self.keithley.get_response(self.timeout)
        print("Current value is %s", current_value)   
        return float(current_value)

    def asynchronousMoveTo(self, value):
        self.target = float(value)
        self.keithley.send_command_no_reply(":SOUR:FUNC CURR; :SOUR:CURR:RANG:AUTO ON", self.timeout)
        self.keithley.send_command_no_reply(":SOUR:CURR:READ:BACK ON; :SOUR:CURR " + str(value), self.timeout)
        
    def isBusy(self):
        if self.target is not None:
            return abs(self.target - self.getPosition()) > self.current_tolerance
        return False;

class Keitlhey2461Voltage(ScannableMotionBase):
    '''Create a scannable to control and read voltage measurement from keithley 2461 source meter'''
    def __init__(self, name, keithley, tolerance = 0.1):
        self.setName(name)
        self.keithley = keithley
        self.setInputNames([name])
        self.setOutputFormat(['%3.3f'])
        self.setLevel(5)
        self.timeout = 0.2 # EPICS Asyn communication timeout
        self.NPLC = 0.5 #the number of power line cycles range from 0.01 to 10 with 0.01 resulting in the fastest reading rates and 10 resulting in the lowest reading noise.
        self.target = None
        self.voltage_tolerance = tolerance
        
    def atScanStart(self):
        self.keithley.outputOn()
        
    def atScanEnd(self):
        self.keithley.outputOff()
           
    def getPosition(self):
        self.keithley.send_command_no_reply(":SENS:VOLT:NPLC " + str(self.NPLC), self.timeout)
        self.keithley.send_command(":MEASure:VOLTage?", self.timeout)
        voltage_value = self.keithley.get_response(self.timeout)
        print("Voltage value is %s", voltage_value)   
        return float(voltage_value)

    def asynchronousMoveTo(self, value):
        self.target = float(value)
        self.keithley.send_command_no_reply(":SOUR:FUNC VOLT; :SOUR:VOLT:RANG:AUTO ON", self.timeout)
        self.keithley.send_command_no_reply(":SOUR:VOLT:READ:BACK ON; :SOUR:VOLT " + str(value), self.timeout)
        
    def isBusy(self):
        if self.target is not None:
            return abs(self.target - self.getPosition()) > self.voltage_tolerance
        return False;


