'''
Created on 15 Feb 2011

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
import sys
from eventreceiver import EventReceiver
from adc import ADC
from functiongenerator import FunctionGenerator
from localStation import mythen
from pvmonitor import PVMonitor

fg=FunctionGenerator("fg")
evr=EventReceiver("evr")
adc=ADC("adc")

class PELoop(ScannableMotionBase):
    
    def __init__(self, name="peloop", functiongenerator=fg, eventreceiver=evr, adc1=adc, psd=mythen):
        self.setName(name)
        self.setInputNames(["time"])
        self.setExtraNames(["PData","EData","MythenData"])
        self.fg=FunctionGenerator()
        self.evr=EventReceiver()
        self.adc=ADC()
        self.psd=mythen
        self.voltagesmonitor=PVMonitor()
        self.electrometersmonitor=PVMonitor()
        self.counter=0
        self.numberofgates=0
        
    # function generator controls
    def getElectrometer(self):
        try:
            self.adc.getElectrometer()
        except:
            print "Fail to get electrometer readings: ", sys.exc_info()[0]
            raise

    def getVoltage(self):
        try:
            self.adc.getVoltage()
        except:
            print "Fail to get voltage readings: ", sys.exc_info()[0]
            raise

    def atScanStart(self):
        #add voltage and electrometer monitor to get data, 
        #this may trigger an monitor event that increment the counter, so it must be reset
        self.voltagesmonitor.setNumberOfGates(self.numberofgates)
        self.electrometersmonitor.setNumberOfGates(self.numberofgates)
        self.adc.addVoltageMonitor(self.voltagesmonitor)
        self.adc.addElectrometerMonitor(self.electrometersmonitor)
        #start ramp output
        self.fg.setOutput(1)

   
    def atScanEnd(self):
        #add voltage and electrometer monitor to get datas
        self.adc.removeVoltageMonitor(self.voltagesmonitor)
        self.adc.removeElectrometerMonitor(self.electrometersmonitor)
        #stop ramp output
        self.fg.setOutput(0)

    def atPointStart(self):
        self.voltagesmonitor.resetCounter()
        self.voltagesmonitor.resetRepetition()
        self.electrometersmonitor.resetCounter()
        self.electrometersmonitor.resetRepetition()
    def atPointEnd(self):
        pass

    def rawGetPosition(self):
        return self.volatgesmonitor.rawGetPosition(), self.electrometersmonitor.rawGetPosition(),mythen.getPosition()

    def rawAsynchronousMoveTo(self,new_position):
        self.evr.rawAsynchronousMoveTo(new_position)
    
    def rawIsBusy(self):
        return self.evr.rawIsBusy()
    
            
#    def toString(self):
#        return self.name + " : " + str(self.getPosition())
