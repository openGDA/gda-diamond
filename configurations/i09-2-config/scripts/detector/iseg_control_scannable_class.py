'''

Scannable class for iSeg Module Voltage Channel control

Created on Oct 31, 2022

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from time import sleep
import i09shared.installation as installation
from threading import Thread

#Device root PV
ISEG_DEVICE_PV = "BL09K-EA-PSU-01:0"
#Module PVs
VOLTAGE_RAMP_SPEED_PV = "VoltageRampSpeed"
CURRENT_RAMP_SPEED_PV = "CurrentRampSpeed"
#Channel PVs
CHANNEL_SET_ON_PV = "Control:setOn"
VOLTAGE_SET_PV = "VoltageSet"
VOLTAGE_MEASURE_PV = "VoltageMeasure"
CURRENT_SET_PV = "CurrentSet"
CURRENT_MEASURE_PV = "CurrentMeasure"

VOLTAGE_RAMP_SPEED = 1.0 #%/s*Vnom
CURRENT_RAMP_SPEED = 1.0 #%/s*Inom
#end points
SLEEP_TIME = 0.05

class ISegChannelControlScannable(ScannableMotionBase):
    '''
    A voltage controller - on, off, ramp speed, move to new position given
    '''


    def __init__(self, name, module_number, channel_number, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = VOLTAGE_RAMP_SPEED, current_ramp_speed = CURRENT_RAMP_SPEED, voltage_control = True):
        '''
        create a scannable for a give iSeg module channel control
        @param name: name of the scannable
        @param module_number: the number of module to use
        @param channel_number: the number of channel to use
        @param pv_root: root name of the Device Process Variable   
        '''
        self.setName(name)
        if voltage_control:
            self.setInputNames(["voltage"])
            self.setExtraNames(["current"])
        else:
            self.setInputNames(["current"])
            self.setExtraNames(["voltage"])
        self.moduleNum =  module_number
        self.channelNum = channel_number
        self.pvRoot = pv_root
        self.busywaittime = 0.0
        self.target = 0.0
        self.target_tolerance = tolerance
        self.saved_ramp_speed = None
        self.voltage_ramp_speed = voltage_ramp_speed
        self.current_ramp_speed = current_ramp_speed
        self._voltage_control = voltage_control
        self.voltage_position = 0.0
        self.current_position = 0.0
        
    @property
    def voltage_control(self):
        return self._voltage_control
    
    @voltage_control.setter
    def voltage_control(self, b):
        self._voltage_control = b
        if b:
            self.setInputNames(["voltage"])
            self.setExtraNames(["current"])
        else:
            self.setInputNames(["current"])
            self.setExtraNames(["voltage"])
        
    def configure(self):
        ''' create channel access clients, but not connect to PVs.
        '''
        if self.isConfigured():
            return
        if installation.isLive():
            self.voltage_ramp_speed_cli = CAClient(self.pvRoot + ":" + str(self.moduleNum) + ":" + VOLTAGE_RAMP_SPEED_PV)
            self.current_ramp_speed_cli = CAClient(self.pvRoot + ":" + str(self.moduleNum) + ":" + CURRENT_RAMP_SPEED_PV)
            self.channel_set_on_cli = CAClient(self.pvRoot + ":" + str(self.moduleNum) + ":" + str(self.channelNum) + ":" + CHANNEL_SET_ON_PV)
            self.voltage_set_cli = CAClient(self.pvRoot + ":" + str(self.moduleNum) + ":" + str(self.channelNum) + ":" + VOLTAGE_SET_PV)
            self.voltage_measure_cli = CAClient(self.pvRoot + ":" + str(self.moduleNum) + ":" + str(self.channelNum) + ":" + VOLTAGE_MEASURE_PV)
            self.current_set_cli = CAClient(self.pvRoot + ":" + str(self.moduleNum) + ":" + str(self.channelNum) + ":" + CURRENT_SET_PV)
            self.current_measure_cli = CAClient(self.pvRoot + ":" + str(self.moduleNum) + ":" + str(self.channelNum) + ":" + CURRENT_MEASURE_PV)

            self.voltage_ramp_speed_cli.configure();sleep(SLEEP_TIME)
            self.current_ramp_speed_cli.configure();sleep(SLEEP_TIME)
            self.channel_set_on_cli.configure();sleep(SLEEP_TIME)
            self.voltage_set_cli.configure();sleep(SLEEP_TIME)
            self.voltage_measure_cli.configure();sleep(SLEEP_TIME)
            self.current_set_cli.configure();sleep(SLEEP_TIME)
            self.current_measure_cli.configure();sleep(SLEEP_TIME)

        self.setConfigured(True)
    
    def deconfigure(self):
        if installation.isLive():
            if self.voltage_ramp_speed_cli.isConfigured():
                self.voltage_ramp_speed_cli.clearup()
            if self.current_ramp_speed_cli.isConfigured():
                self.current_ramp_speed_cli.clearup()
            if self.channel_set_on_cli.isConfigured():
                self.channel_set_on_cli.clearup()
            if self.voltage_set_cli.isConfigured():
                self.voltage_set_cli.clearup()
            if self.voltage_measure_cli.isConfigured():
                self.voltage_measure_cli.clearup()
            if self.current_set_cli.isConfigured():
                self.current_set_cli.clearup()
            if self.current_measure_cli.isConfigured():
                self.current_measure_cli.clearup()
        self.setConfigured(False)
                
    def atScanStart(self):
        if installation.isDummy():
            return
        if self._voltage_control:
            self.saved_ramp_speed = float(self.voltage_ramp_speed_cli.caget())
            self.voltage_ramp_speed_cli.caput(self.voltage_ramp_speed)
        else:
            self.saved_ramp_speed = float(self.current_ramp_speed_cli.caget())
            self.current_ramp_speed_cli.caput(self.current_ramp_speed)
        # self.on()
        
    def atScanEnd(self):
        if installation.isDummy():
            return
        # self.off()
        if self.saved_ramp_speed:
            if self._voltage_control:
                self.voltage_ramp_speed_cli.caput(self.saved_ramp_speed)
            else:
                self.current_ramp_speed_cli.caput(self.saved_ramp_speed)
    
    def rawGetPosition(self):
        if installation.isLive():
            if self._voltage_control:
                return [float(self.voltage_measure_cli.caget()), float(self.current_measure_cli.caget())]
            else:
                return [float(self.current_measure_cli.caget()), float(self.voltage_measure_cli.caget())]
        else:
            if self._voltage_control:
                return [self.voltage_position, self.current_position]
            else:
                return [self.current_position, self.voltage_position]
        
    def rawAsynchronousMoveTo(self,new_position):
        if installation.isLive():
            self.target = float(new_position)
            if self._voltage_control:
                self.voltage_set_cli.caput(self.target)
            else:
                self.current_set_cli.caput(self.target)
        else:
            self.target = float(new_position)            
            new_thread = Thread(target = self._task)
            new_thread.start()

    def isBusy(self):
        if installation.isLive():
            try:
                if self._voltage_control:
                    return abs(float(self.voltage_measure_cli.caget()) - self.target) > self.target_tolerance
                else:
                    return abs(float(self.current_measure_cli.caget()) - self.target) > self.target_tolerance
            except:
                print("problem read Voltage Measure from EPICS")
                return 0
        else:
            if self._voltage_control:
                return self.voltage_position != self.target
            else:
                return self.current_position != self.target
        
    
    def _task(self, time_increment = 1):
        '''increment or decrement current position toward target value
        '''
        if self._voltage_control:
            if self.target > self.voltage_position:
                increment = time_increment
            elif self.target < self.voltage_position:
                increment = -time_increment
    
            while abs(self.target - self.voltage_position) > self.voltage_ramp_speed * time_increment:
                sleep(time_increment)
                self.voltage_position += self.voltage_ramp_speed * increment
    
            self.voltage_position = self.target
        else: 
            if self.target > self.current_position:
                increment = time_increment
            elif self.target < self.current_position:
                increment = -time_increment
    
            while abs(self.target - self.current_position) > self.current_ramp_speed * time_increment:
                sleep(time_increment)
                self.current_position += self.current_ramp_speed * increment
    
            self.current_position = self.target

    def setVoltageRamp(self, speed = VOLTAGE_RAMP_SPEED):
        '''set voltage ramp speed for the module
        '''
        if installation.isLive():
            self.voltage_ramp_speed_cli.caput(float(speed))
        else:
            self.voltage_ramp_speed = speed
            
    def setCurrentRamp(self, speed = CURRENT_RAMP_SPEED):
        '''set voltage ramp speed for the module
        '''
        if installation.isLive():
            self.current_ramp_speed_cli.caput(float(speed))
        else:
            self.current_ramp_speed = speed  
                  
    def on(self):
        '''switch on the control
        '''
        if installation.isLive():
            self.channel_set_on_cli.caput(1)
        else:
            print("voltage control is on")
        
    def off(self):
        '''switch off the control
        '''
        if installation.isLive():
            self.channel_set_on_cli.caput(0)
        else:
            print("voltage control is off")

        