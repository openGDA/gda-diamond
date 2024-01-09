'''
define scannables that interact with Keithley 2461 source meter using SCPI (Standard Commands for Programmable Instrument) commands

SCPI Command execution rules are as follows:

Commands execute in the order that they are presented in the command message. 
An invalid command generates an event message and is not executed.
Valid commands that precede an invalid command in a command message are executed.
Valid commands that follow an invalid command in a command message are ignored.

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
import logging

logger = logging.getLogger(__name__)

class Keithley2461Current(ScannableMotionBase):
    '''Create a scannable to control source current and measure voltage from keithley 2461 source meter. Resistance is then calculated from measured voltage and current.
        The recorded current value is measured value, not the set value requested!
        The implementation is largely based on manual reference page 2-107 with modifications to make scannable works with scan and pos command.
    '''
    def __init__(self, name, keithley, tolerance = 0.1):
        self.setName(name)
        self.keithley = keithley
        self.setInputNames(["Current"])
        self.setExtraNames(["Voltage", "Resistance"])
        self.setOutputFormat(['%10.6f','%10.6f','%10.6f'])
        self.setLevel(5)
        self.timeout = 1.0 # EPICS Asyn communication timeout
        self.NPLC = 0.5 #the number of power line cycles range from 0.01 to 10 with 0.01 resulting in the fastest reading rates and 10 resulting in the lowest reading noise.
        self._busy = False
        self.inScan = False
        self._count = 1
        self.use4wire = True
        self._read_wait = 0.2
        self.config_wait = 2.0
        self._epics_wait = 0.1
        self.voltage_limit = 10
        self.logger = logger.getChild(self.__class__.__name__)
        
    def configure(self):
        self.keithley.reset()
        self.keithley.senseFunction("VOLT")
        self.keithley.senseAutoRange("VOLT", "ON")
        if self.use4wire:
            self.set4Wire()
        else:
            self.set2Wire()
        self.keithley.sourceFunction('CURR')
        self.keithley.sourceLimit("CURR", self.voltage_limit)
        self.keithley.sourceReadback("CURR", "ON")
        self.keithley.senseCount(self.count)
        self.keithley.senseFunctionNPLC("VOLT",self.NPLC)
        sleep(self.config_wait)
        
    def set4Wire(self):
        self.keithley.senseRsense("VOLT", "ON")
        
    def set2Wire(self):
        self.keithley.senseRsense("VOLT", "OFF")
        
    def enable_output_control_per_point(self):
        self.keithley.enable_output_control_per_point = True
    
    def disable_output_control_per_point(self):
        self.keithley.enable_output_control_per_point = False
        
    def atScanStart(self):
        self.configure()
        self.inScan = True

    def atScanEnd(self):
        self.inScan = False
    
    @property
    def epics_wait(self):
        return self._epics_wait 
    
    @epics_wait.setter
    def epics_wait(self, value):
        self._epics_wait = float(value)
        self.keithley.communication_wait = self._epics_wait
    
    @property
    def read_wait(self):
        return self._read_wait
    
    @read_wait.setter
    def read_wait(self, value):
        self._read_wait = float(value)
        self.keithley.read_wait =  self._read_wait
        
    @property
    def count(self):
        return self._count
    
    @count.setter        
    def count(self, value):
        self._count = int(value)
        if self.count < 1:
            raise ValueError("Number of measurement count must be positive integer greater than and equals to 1.")
        if self.count == 1:
            self.setInputNames(["Current"])
            self.setExtraNames(["Voltage", "Resistance"])
            self.setOutputFormat(['%10.6f','%10.6f','%10.6f'])
        if self.count > 1:
            input_names = []
            extra_names = []
            output_formats = []
            for i in range(self.count):
                if i == 0:
                    input_names.append("Current_" + str(i))
                else:
                    extra_names.append("Current_" + str(i))
                extra_names.append("Voltage_" + str(i))
                extra_names.append("Resistance_" + str(i))
                output_formats.append("%10.6f")
                output_formats.append("%10.6f")
                output_formats.append("%10.6f")
            self.setOutputFormat(output_formats)
            self.setInputNames(input_names)
            self.setExtraNames(extra_names)
           
    def getPosition(self):
        returned_value = self.keithley.get_response(self.timeout)
        self.logger.debug("Keithley returns are %s" % returned_value)
        try:
            data = [float(x) for x in str(returned_value).split(",")]
    
            if self.count == 1:
                current = data[0]
                voltage = data[1]
                resistance = voltage/current
                self.logger.debug("Current value is %f, Voltage value is %f, Resistance is %f" % (current, voltage, resistance))
                data = [current, voltage, resistance]
            if self.count > 1:
                input_data = []
                extra_data = []
                resistance_data = []
                for i in range(len(data)):
                    if i % 2 == 0: #even index
                        input_data.append(data[i])
                    if i % 2 == 1: #odd index
                        extra_data.append(data[i])
                for vol, cur in zip(extra_data,input_data):
                    resistance_data.append(vol/cur)
                self.logger.debug("Current value is %s, Voltage value is %s, Resistance is %s" % (str(input_data), str(extra_data), str(resistance_data)))
                data = []
                #reorder data to match GDA input names and extra names order
                for each in zip(input_data, extra_data, resistance_data):
                    [data.append(x) for x in each]
            return data
        except:
            print("response from %s is %s" % (self.getName(), returned_value))            
            raise

    def asynchronousMoveTo(self, value):
        if not self.inScan:
            self.configure()
        try:
            self._busy = True
            self.keithley.sourceValue("CURR", value)
            self.keithley.prepare_trace_buffer(self.count)
            self.keithley.acquire_data(self.count)
        finally:
            self._busy = False
        
    def isBusy(self):
        return self._busy

class Keithley2461Voltage(ScannableMotionBase):
    '''Create a scannable to control source voltage and measure current from keithley 2461 source meter. Resistance is then calculated from the measured voltage and current.
        The voltage recored is measured value, not the set value requested!
        This implementation is based on manual reference page 2-106.
    '''
    def __init__(self, name, keithley, tolerance = 0.1):
        self.setName(name)
        self.keithley = keithley
        self.setInputNames(["Voltage"])
        self.setExtraNames(["Current", "Resistance"])
        self.setOutputFormat(['%10.6f','%10.6f','%10.6f'])
        self.setLevel(5)
        self.timeout = 1.0 # EPICS Asyn communication timeout
        self.NPLC = 0.5 #the number of power line cycles range from 0.01 to 10 with 0.01 resulting in the fastest reading rates and 10 resulting in the lowest reading noise.
        self._busy = False
        self.inScan = False
        self._count = 1
        self.use4wire = True
        self._read_wait = 0.2
        self.config_wait = 2.0
        self._epics_wait = 0.1
        self.current_limit = 1.0
        self.logger = logger.getChild(self.__class__.__name__)
        
    def configure(self):
        self.keithley.reset()
        self.keithley.senseFunction("CURR")
        self.keithley.senseAutoRange("CURR", "ON")
        if self.use4wire:
            self.set4Wire()
        else:
            self.set2Wire()
        self.keithley.sourceFunction('VOLT')
        self.keithley.sourceLimit("VOLT", self.current_limit)
        self.keithley.sourceReadback("VOLT", "ON")
        self.keithley.senseCount(self.count)
        self.keithley.senseFunctionNPLC("CURR", self.NPLC)
        sleep(self.config_wait)
        
    def set4Wire(self):
        self.keithley.senseRsense("CURR", "ON")
        
    def set2Wire(self):
        self.keithley.senseRsense("CURR", "OFF")
            
    def enable_output_control_per_point(self):
        self.keithley.enable_output_control_per_point = True
    
    def disable_output_control_per_point(self):
        self.keithley.enable_output_control_per_point = False

    def atScanStart(self):
        self.configure()
        self.inScan = True
        
    def atScanEnd(self):
        self.inScan = False
    
    @property
    def epics_wait(self):
        return self._epics_wait 
    
    @epics_wait.setter
    def epics_wait(self, value):
        self._epics_wait = float(value)
        self.keithley.communication_wait = self._epics_wait
    
    @property
    def read_wait(self):
        return self._read_wait
    
    @read_wait.setter
    def read_wait(self, value):
        self._read_wait = float(value)
        self.keithley.read_wait =  self._read_wait
        
    @property      
    def count(self):
        return self._count
    
    @count.setter
    def count(self, value):
        self._count = int(value)
        if self.count < 1:
            raise ValueError("Number of measurement count must be positive integer greater than and equals to 1.")
        if self.count == 1:
            self.setInputNames(["Voltage"])
            self.setExtraNames(["Current", "Resistance"])
            self.setOutputFormat(['%10.6f','%10.6f','%10.6f'])
        if self.count > 1:
            input_names = []
            extra_names = []
            output_formats = []
            for i in range(self.count):
                if i == 0:
                    input_names.append("Voltage_" + str(i))
                else:
                    extra_names.append("Voltage_" + str(i))
                extra_names.append("Current_" + str(i))
                extra_names.append("Resistance_" + str(i))
                output_formats.append("%10.6f")
                output_formats.append("%10.6f")
                output_formats.append("%10.6f")
            self.setOutputFormat(output_formats)
            self.setInputNames(input_names)
            self.setExtraNames(extra_names)
                      
    def getPosition(self):
        returned_value = self.keithley.get_response(self.timeout)
        self.logger.debug("Keithley returns are %s" % returned_value)
        data = [float(x) for x in str(returned_value).split(",")]
        
        if self.count == 1:
            voltage = data[0]
            current = data[1]
            resistance = voltage/current
            self.logger.debug("Voltage value is %f, Current value is %f, Resistance is %f" % (voltage, current, resistance))
            data = [voltage, current, resistance]
        if self.count > 1:
            #parse the returned data
            input_data = []
            extra_data = []
            resistance_data = []
            for i in range(len(data)):
                if i % 2 == 0: #even index
                    input_data.append(data[i])
                if i % 2 == 1: #odd index
                    extra_data.append(data[i])
            for vol, cur in zip(input_data,extra_data):
                resistance_data.append(vol/cur)
            self.logger.debug("Voltage value is %s, Current value is %s, Resistance is %s" % (str(input_data), str(extra_data), str(resistance_data)))
            data = []
            #reorder data to match GDA input names and extra names order
            for each in zip(input_data, extra_data, resistance_data):
                [data.append(x) for x in each]          
        return data

    def asynchronousMoveTo(self, value):
        if not self.inScan:
            self.configure()
        try:
            self._busy = True
            self.keithley.sourceValue("VOLT", value)
            self.keithley.prepare_trace_buffer(self.count)
            self.keithley.acquire_data(self.count)
        finally:
            self._busy = False
        
    def isBusy(self):
        return self._busy
