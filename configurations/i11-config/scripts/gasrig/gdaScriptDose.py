'''
Created on 23 May 2014

@author: fy65
'''
from epics_scripts.pv_scannable_utils import caput
from gda.epics import CAClient
from gov.aps.jca.event import MonitorListener
from time import sleep


class DoseControl(MonitorListener):
    
    def __init__(self, name,pv):
        self.name=name
        self.currentpressure=0.0
        self.outcli=CAClient(pv)
        self.outcli.configure()
        sleep(1)
        self.monitor=self.outcli.camonitor(self)
        
    def waitForGreaterThan(self, target):
        while (self.getCurrentPressure() <= target):
            sleep(0.1)
        
    def getCurrentPressure(self):
        return self.currentpressure
    
    def setSystemPressure(self, sysP,target,flow):
        #SET STARTING SAMPLE PRESSURE
        caput("BL11I-EA-GIR-01:DVPC:SETPOINT:WR", sysP)
        caput("BL11I-EA-GIR-01:MFC1:SETPOINT:WR", flow)
        caput("BL11I-EA-GIR-01:BPR:SETPOINT:WR", target)
        self.waitForGreaterThan(target)
        caput("BL11I-EA-GIR-01:MFC1:SETPOINT:WR", 0)
    
    def setSamplePressure(self,SampleP, target, increment):
        # SET FINAL SAMPLE PRESSURE AND INCREMENTS
        while SampleP <= target:                                #final sample pressure in bar
            SampleP += increment                      #increments in bar
            caput("BL11I-EA-GIR-01:DVPC:SETPOINT:WR", SampleP)
            sleep(5)                      #wait time in seconds

    def monitorChanged(self, mevent):
        try:
            self.currentpressure = float(mevent.getDBR().getDoubleValue()[0])
        except:
            #do nothing
            print
            