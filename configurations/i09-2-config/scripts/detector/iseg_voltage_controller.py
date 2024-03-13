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

ISEG_DEVICE = "BL09K-EA-PSU-01:0"
VOLTAGE_RAMP_SPEED = 1.0 #%/s*Vnom
#end points
VOLTAGE_RAMP_SPEED_PV = "VoltageRampSpeed"
VOLTAGE_SET_PV = "VoltageSet"
CONTROL_SET_ON_PV = "Control:setOn"
VOLTAGE_MEASURE_PV = "VoltageMeasure"

class ISegVoltageControl(ScannableMotionBase):
    '''
    A voltage controller - on, off, ramp speed, move to new position given
    '''


    def __init__(self, name, module_number, channel_number, pv_root = ISEG_DEVICE, tolerance = 0.1, ramp_speed = VOLTAGE_RAMP_SPEED):
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
        self.busywaittime = 0.0
        self.target = 0.0
        self.target_tolerance = tolerance
        self.saved_ramp_speed = None
        self.ramp_speed = ramp_speed

        
    def configure(self):
        ''' create channel access clients, but not connect to PVs.
        '''
        if self.isConfigured():
            return
        if installation.isLive():
            self.rampspeedCli = CAClient(self.pvRoot + ":" + str(self.moduleNum) + ":" + VOLTAGE_RAMP_SPEED_PV)
            self.setCli = CAClient(self.pvRoot + ":" + str(self.moduleNum) + ":" + str(self.channelNum) + ":" + VOLTAGE_SET_PV)
            self.controlCli = CAClient(self.pvRoot + ":" + str(self.moduleNum) + ":" + str(self.channelNum) + ":" + CONTROL_SET_ON_PV)
            self.readCli = CAClient(self.pvRoot + ":" + str(self.moduleNum) + ":" + str(self.channelNum) + ":" + VOLTAGE_MEASURE_PV)

            self.rampspeedCli.configure();sleep(0.1)
            self.setCli.configure();sleep(0.1)
            self.controlCli.configure();sleep(0.1)
            self.readCli.configure();sleep(0.1)
        self.setConfigured(True)
    
    def deconfigure(self):
        if installation.isLive():
            if self.rampspeedCli.isConfigured():
                self.rampspeedCli.clearup()
            if self.setCli.isConfigured():
                self.setCli.clearup()
            if self.controlCli.isConfigured():
                self.controlCli.clearup()
            if self.readCli.isConfigured():
                self.readCli.clearup()
                
    def atScanStart(self):
        self.saved_ramp_speed = float(self.rampspeedCli.caget())
        self.rampspeedCli.caput(self.ramp_speed)

    def atScanEnd(self):
        if self.saved_ramp_speed:
            self.rampspeedCli.caput(self.saved_ramp_speed)
    
    def rawGetPosition(self):
        if installation.isLive():
            return float(self.readCli.caget())
        else:
            return self.current_position
        
    def rawAsynchronousMoveTo(self,new_position):
        if installation.isLive():
            self.target = float(new_position)
            self.setCli.caput(self.target)
        else:
            self.target = float(new_position)            
            new_thread = Thread(target = self._task)
            new_thread.start()

    def isBusy(self):
        if installation.isLive():
            try:
                if abs(float(self.readCli.caget()) - self.target) > self.target_tolerance:
                    return True
                else:
                    return False
            except:
                print("problem read Voltage Measure from EPICS")
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
           

    def setRampSpeed(self, speed = VOLTAGE_RAMP_SPEED):
        '''set voltage ramp speed for the module
        '''
        if installation.isLive():
            self.rampspeedCli.caput(float(speed))
        else:
            self.rampspeed = speed
        
    def on(self):
        '''switch on the control
        '''
        if installation.isLive():
            self.controlCli.caput(1)
        else:
            print("voltage control is on")
        
    def off(self):
        '''switch off the control
        '''
        if installation.isLive():
            self.controlCli.caput(0)
        else:
            print("voltage control is off")

        