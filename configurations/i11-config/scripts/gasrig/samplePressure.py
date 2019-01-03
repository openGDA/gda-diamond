'''
a specific scannable for sample pressure control to support gradual gas pressure increments in sample.

Created on 13 Jun 2014

@author: fy65
'''
from gov.aps.jca.event import MonitorListener
from gda.device.scannable import ScannableBase
from time import sleep
import sys
from gda.epics import CAClient
import thread
from gda.jython.commands.GeneralCommands import pause as interruptable

CurrentPressure = "BL11I-EA-GIR-01:SAMPLE:P:RD"
TargetPressure = "BL11I-EA-GIR-01:SAMPLE:SETPOINT:WR"
PressureControl = "BL11I-EA-GIR-01:SAMPLE:MODE:WR"

class SamplePressure(ScannableBase, MonitorListener):
    '''
    create a sannable to provide control of gas pressure in the sample. 
    It will reports to users when the system pressure is less than the sample pressure requested. 
    '''

    def __init__(self, name, systempressure):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.increment = 0.01
        self.target = 0.0
        self.lastTarget=0.0
        self.sampleP = 0.0
        self.currentpressure = 0.0
        self.pressureTolerance = 0.002
        self.outcli=CAClient(CurrentPressure)
        self.incli=CAClient(TargetPressure)
        self.sysp=systempressure
        self.initialiseTarget()
        
    def atScanStart(self):
        '''intialise parameters before scan'''
        #TODOS check requested sample pressure can be reached 
        if not self.outcli.isConfigured():
            self.outcli.configure()
        if not self.incli.isConfigured():
            self.incli.configure()
        self.target = self.getPosition()
    
    def atScanEnd(self):
        '''clean up resources'''
        if self.outcli.isConfigured():
            self.outcli.clearup()
        if self.incli.isConfigured():
            self.incli.clearup()
        
    def atPointStart(self):
        pass
    
    def atPointEnd(self):
        pass
        
    def getPosition(self):
        '''
        return the current gas pressure in sample
        '''
        try:
            if not self.outcli.isConfigured():
                self.outcli.configure()
                output=float(self.outcli.caget())
                self.outcli.clearup()
            else:
                output=float(self.outcli.caget())
            return output
        except:
            print "Error returning current position"
            return 0

    def asynchronousMoveTo(self, new_position):
        '''
        move the sample pressure to the specified value asynchronously.
        '''
        try:
            self.lastTarget=round(self.getLastTarget(),3)
            self.sampleP = round(self.getPosition(),3)
            self.target = round(float(new_position),3)
            thread.start_new_thread(self.setSamplePressure, (self.sampleP, self.target, self.increment))
        except:
            print "error moving sample pressure to (%s): %f" % (sys.exc_info()[0], float(new_position))
            raise

    def isBusy(self):
        return (abs(self.getPosition() - self.getTarget())>self.getTolerance())
    
    def stop(self):
        '''
        stop or abort pressure move in the sample.
        '''
        self.asynchronousMoveTo(self.getPosition())
        if self.outcli.isConfigured():
            self.outcli.clearup()
        if self.incli.isConfigured():
            self.incli.clearup()
        
    def setSamplePressure(self, SampleP, target, increment):
        # SET FINAL SAMPLE PRESSURE AND INCREMENTS
        if SampleP<target:
            SampleP =round(self.lastTarget+increment,3)  # increments in bar
            if SampleP>target:
                return
            try:
                if not self.incli.isConfigured():
                    self.incli.configure()
                while SampleP <= target:  # final sample pressure in bar
#                   interruptable()
                    self.incli.caput(SampleP)
                    #print "set sample pressure to "+str(SampleP)+", target is "+str(target)
                    sleep(5)  # wait time in seconds
                    SampleP =round(SampleP+increment,3)
                    #check if smaple pressure required greater the system pressure then exit
                    if self.sysp.getPosition()<target:
                        #TODOs recharge the system pressure here???
                        print "System pressure %f is less than the demanding sample pressure %f. Please abort this scan or re-charge the system pressure." % (self.sysp.getPosition(),target)
#                 if self.incli.isConfigured():
#                     self.incli.clearup()
            except:
                print "error moving to position"

        elif SampleP>target:
            SampleP =round(self.lastTarget-increment,3)  # increments in bar
            if SampleP<target:
                return
            if SampleP<0:
                SampleP=0
            if target<0:
                raise Exception("Pressure cannot be negative.")
            try:
                if not self.incli.isConfigured():
                    self.incli.configure()
                while SampleP >= target:  # final sample pressure in bar
#                   interruptable()
                    self.incli.caput(SampleP)
                   # print "set sample pressure to "+str(SampleP)+", target is "+str(target)
                    sleep(5)  # wait time in seconds
                    SampleP =round(SampleP-increment, 3)
                    if SampleP<0:
                        self.incli.caput(0)
                        break
#                 if self.incli.isConfigured():
#                     self.incli.clearup()
            except:
                print "error moving to position"
        else:
            print "already at the sample pressure."
            return
            

    def setIncrement(self, value):
        self.increment = value
        
    def getIncrement(self):
        return self.increment 

    def getTarget(self):
        return self.target
    
    def getLastTarget(self):
        try:
            if not self.incli.isConfigured():
                self.incli.configure()
                output=float(self.incli.caget())
                self.incli.clearup()
            else:
                output=float(self.incli.caget())
            return output
        except:
            print "Error returning target value"
            return 0
    
    def initialiseTarget(self):
        self.lastTarget=self.getLastTarget()
        
    def getTolerance(self):
        return self.pressureTolerance
    def setTolerance(self, value):
        self.pressureTolerance = value


