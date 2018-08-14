'''
Created on 23 May 2014

@author: fy65
'''
from time import sleep

from epics_scripts.pv_scannable_utils import caput
from gda.epics import CAClient
from gov.aps.jca.event import MonitorListener


class VacControl(MonitorListener):
    def __init__(self, name):
        self.name=name
        self.currentpressure=0.0
        self.outcli=None
        self.monitor=None
        
    def waitForGreaterThan(self, target):
        if not self.outcli.isConfigured():
            self.outcli.configure()
            self.monitor=self.outcli.camonitor(self)        
        while (self.getCurrentPressure() <= target):
            sleep(0.1)
        if self.outcli.isConfigured():
            self.outcli.removeMonitor(self.monitor)
            self.monitor=None
        
    def getCurrentPressure(self):
        return self.currentpressure
    
    
    def setSamplePressure(self, SampleP, target, decrement):
        # SET FINAL SAMPLE PRESSURE AND INCREMENTS - DVPC
        while SampleP > target:                                  #final sample pressure in bar
            SampleP -= decrement                                #increments in bar
            caput("BL11J-EA-GIR-01:DVPC:SETPOINT:WR", SampleP)
            sleep(2)                      #sleep time in seconds
    
    def setSystemPressure(self, sysP, target, decrement):
        # SET SYSTEM PRESSURE - BPR
        caput("BL11J-EA-GIR-01:BPR:SETPOINT:WR", target)
        
        while sysP > target:                                #final system pressure in bar
            target -= decrement                                #increments in bar
            caput("BL11J-EA-GIR-01:BPR:SETPOINT:WR", target)
            sleep(7)                      #sleep time in seconds
        
    def monitorChanged(self, mevent):
        self.currentpressure = float(mevent.getDBR().getDoubleValue()[0])

