'''

Scannable class for iSeg Module Voltage Channel control

Created on Oct 31, 2022

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from time import sleep
import installation
from threading import Thread

ISEG_DEVICE = "BL09K-EA-PSU-01:0"

#end points
VOLTAGE_RAMP_SPEED = "VoltageRampSpeed"
VOLTAGE_SET = "VoltageSet"
CONTROL_SET_ON = "Control:setOn"
IS_VOLTAGE_RAMP = "isVoltageRamp"
VOLTAGE_MEASURE = "VoltageMeasure"

class ISegVoltageControl(ScannableMotionBase):
    '''
    A voltage controller - on, off, ramp speed, move to new position given
    '''


    def __init__(self, name, module_number, channel_number, pv_root = "BL09K-EA-PSU-01:0"):
        '''
        create a scannable for a give iSeg module channel
        @param name: name of the scannable
        @param module_number: the number of module to use
        @param channel_number: the number of channel to use
        @param pv_root: root name of the Processing Variable   
        '''
        self.setName(name)
        self.setInputNames([name])
        self.moduleNum =  module_number
        self.channelNum = channel_number
        self.pvRoot = pv_root
        
    def configure(self):
        ''' create channel access clients, but not connect to PVs.
        '''
        if self.isConfigured():
            return
        if installation.isLive():
            self.rampspeedCli = CAClient(self.pvRoot + ":" + str(self.moduleNum) + ":" + str(self.channelNum) + ":" + VOLTAGE_RAMP_SPEED)
            self.setCli = CAClient(self.pvRoot + ":" + str(self.moduleNum) + ":" + str(self.channelNum) + ":" + VOLTAGE_SET)
            self.controlCli = CAClient(self.pvRoot + ":" + str(self.moduleNum) + ":" + str(self.channelNum) + ":" + CONTROL_SET_ON)
            self.isRampCli = CAClient(self.pvRoot + ":" + str(self.moduleNum) + ":" + str(self.channelNum) + ":" + IS_VOLTAGE_RAMP)        
            self.readCli = CAClient(self.pvRoot + ":" + str(self.moduleNum) + ":" + str(self.channelNum) + ":" + VOLTAGE_MEASURE)
        self.setConfigured(True)
                
    def atScanStart(self):
        if installation.isLive():
            if not self.rampspeedCli.isConfigured():
                self.rampspeedCli.configured()
            if not self.setCli.isConfigured():
                self.setCli.configured()
            if not self.controlCli.isConfigured():
                self.controlCli.configured()
            if not self.isRampCli.isConfigured():
                self.isRampCli.configured()
            if not self.readCli.isConfigured():
                self.readCli.configured()

    def atScanEnd(self):
        if installation.isLive():
            if self.rampspeedCli.isConfigured():
                self.rampspeedCli.clearup()
            if self.setCli.isConfigured():
                self.setCli.clearup()
            if self.controlCli.isConfigured():
                self.controlCli.clearup()
            if self.isRampCli.isConfigured():
                self.isRampCli.clearup()()
            if self.readCli.isConfigured():
                self.readCli.clearup()

    def rawGetPosition(self):
        if installation.isLive():
            if not self.readCli.isConfigured():
                self.readCli.configure()
            output=float(self.readCli.caget())
            return output
        else:
            return self.current_position
        
    def rawAsynchronousMoveTo(self,new_position):
        if installation.isLive():
            if not self.setCli.isConfigured():
                self.setCli.configure()
            self.setCli.caput(float(new_position))
            sleep(0.1)
        else:
            self.target = float(new_position)            
            new_thread = Thread(target = self._task)
            new_thread.start()

    def isBusy(self):
        if installation.isLive():
            try:
                if not self.isRampCli.isConfigured():
                    self.isRampCli.configure()
                self.status=self.isRampCli.caget()
                return int(self.status) == 1
            except:
                print("problem get ramping status")
                return 0
        else:
            return self.current_position != self.target
        
    
    def _task(self, time_increment = 1):
        '''increment or decrement current position toward target value
        '''
        if self.target > self.current_position:
            increment = time_increment
        elif self.target < self.current_position:
            increment = -time_increment

        while abs(self.target - self.current_position) > self.rampspeed * time_increment:
            sleep(time_increment)
            self.current_position += self.rampspeed * increment

        self.current_position = self.target
           

    def setRampSpeed(self, speed = 1):
        '''set voltage ramp speed for the module
        '''
        if installation.isLive():
            if not self.rampspeedCli.isConfigured():
                self.rampspeedCli.configure()
            self.rampspeedCli.caput(float(speed))
        else:
            self.rampspeed = speed
        
    def on(self):
        '''switch on the control
        '''
        if installation.isLive():
            if not self.controlCli.isConfigured():
                self.controlCli.configure()
            self.controlCli.caput(1)
        else:
            print("voltage control is on")
        
    def off(self):
        '''switch off the control
        '''
        if installation.isLive():
            if not self.controlCli.isConfigured():
                self.controlCli.configure()
            self.controlCli.caput(0)
        else:
            print("voltage control is off")

        