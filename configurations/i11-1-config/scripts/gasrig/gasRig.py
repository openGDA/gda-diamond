'''
a scannable for controlling the gas injection rig system which are used to prepare the sample environment:
    1. Before starting the environment, you flush the system with gas using gasrig.flushSystem();
    2. then vacuum the sample using gasrig.vacSample();
    3. Then set the system pressure by selecting a mass flow controller, its flow, and target pressure using gdarig.gasin(mcf2,1.0,1.0);
    4. scan the sample pressure and collect data e.g. scan sampleP 0.5 0.9 0.1 w 100 cvscan 1800;
    5. on completion, vent the system by calling gasrig.complete(). 

Created on 6 Dec 2013
updated on 16 June 2014

@author: fy65
'''
#from gasrig.i11gasrig import mfc1, bpr, ventvalve, sampleP, dvpc, isolationvalve
from gasrig.gasRigValve import GasRigValveClass
from gasrig.alicatMassFlowController import AlicatMassFlowController
from gasrig.alicatPressureController import AlicatPressureController
from gasrig.samplePressure import SamplePressure
from gda.jython.commands.GeneralCommands import pause as interruptable

mfc1=AlicatMassFlowController("mfc1","BL11J-EA-GIR-01:MFC1:",0.01,"%.3f")
mfc2=AlicatMassFlowController("mfc2","BL11J-EA-GIR-01:MFC2:",0.01,"%.3f")
mfc3=AlicatMassFlowController("mfc3","BL11J-EA-GIR-01:MFC3:",0.01,"%.3f")
bpr=AlicatPressureController("bpr","BL11J-EA-GIR-01:SYSTEM:",0.01,"%.3f")
bpr.configure()
dvpc=AlicatPressureController("dvpc","BL11J-EA-GIR-01:SAMPLE:",0.01,"%.3f")
dvpc.configure()
ventvalve=GasRigValveClass("ventvalve", "BL11J-EA-GIR-01:VENT:")
isolationvalve=GasRigValveClass("isolationvalve", "BL11J-EA-GIR-01:ISO:")
backvalve=GasRigValveClass("backvalve", "BL11J-EA-GIR-01:BACK:")

sampleP=SamplePressure("sampleP", bpr)

from time import sleep
#ROOT_PV="BL11J-EA-GIR-01:"
SEQUENCE_CONTROL="SEQ:CON"
SEQUENCE_STATUS="SEQ:STA"
#AT_PRESSURE_PROC="ATPRESSURE.PROC"

sequence={0:"on",1:"off",2:"reset"}
sequencestat={0:"Fault",1:"on",2:"Turning On",3:"Off",4:"Turning Off"}

SystemTargetPressure = "BL11J-EA-GIR-01:SYSTEM:SETPOINT:WR"
SampleTargetPressure = "BL11J-EA-GIR-01:SAMPLE:SETPOINT:WR"


from gda.epics import CAClient 
from gda.device.scannable import ScannableMotionBase

class GasRigClass(ScannableMotionBase):
    '''Create a scannable for a gas injection rig'''
    def __init__(self, name, rootPV):
        self.setName(name);
        self.setInputNames([name])
        self.setLevel(5)
        self.setsequencecli=CAClient(rootPV+SEQUENCE_CONTROL)
        self.statecli=CAClient(rootPV+SEQUENCE_STATUS)
        self.systemincli=CAClient(SystemTargetPressure)
        self.sampleincli=CAClient(SampleTargetPressure)
        
    def vacSample(self, samplePressure=dvpc):
        print "Vacuum the sample ..."
        samplePressure.setMode(0)
        self.on()
        increment=0.005
        target=float(samplePressure.getPosition())-increment
        try:
            if not self.sampleincli.isConfigured():
                self.sampleincli.configure()
            while float(samplePressure.getPosition()) > target:  # final sample pressure in bar
#                 interruptable()
                self.sampleincli.caput(target)
                target = target-increment  # increments in bar
                sleep(5.0)  # wait time in seconds
                if target<=0.0:
                    break
            if self.sampleincli.isConfigured():
                self.sampleincli.clearup()
        except:
            print "error moving to position"
        samplePressure.moveTo(0.0)
        print "sample is under vacuum now."
        
    def vacSystem(self, systemPressure=bpr):
        print "Vacuum the system ..."
        systemPressure.setMode(0)
        self.on()
        increment=0.005
        target=float(systemPressure.getPosition())-increment
        try:
            if not self.systemincli.isConfigured():
                self.systemincli.configure()
            while target > 0:  
#                 interruptable()
                self.systemincli.caput(target)
                target = target-increment  # increments in bar
                sleep(5.0)  # wait time in seconds
            if self.systemincli.isConfigured():
                self.systemincli.clearup()
        except:
            print "error moving to position"
        systemPressure.moveTo(0.0)
        print "system is under vacuum now."

    def gasin(self, mfc=mfc1, flow=0.1, pressuretarget=1.0, systemPressure=bpr):
        '''select gas flow control and set system pressure'''
        print "inject gas %s into the system." % (mfc.getGasType())
        mfc.asynchronousMoveTo(flow)
        sleep(1)
        systemPressure.moveTo(pressuretarget)
        sleep(1)
        mfc.asynchronousMoveTo(0)
        print "The system reaches at target pressure %f" % (pressuretarget)
        
    def complete(self,valve=ventvalve,systemPressure=bpr, samplePressure=sampleP):
        print "complete this sample, vent the system"
        self.off()
        valve.on()
        systemPressure.asynchronousMoveTo(0)
        samplePressure.asynchronousMoveTo(0)
        mfc1.asynchronousMoveTo(0)
        mfc2.asynchronousMoveTo(0)
        mfc3.asynchronousMoveTo(0)
        
    def flushSystem(self,repeat, mfc=mfc1, flow=0.5, duration=60.0, isolation=isolationvalve, vent=ventvalve, systemPressure=bpr):
        print "flushing the system for "+str(duration)+" seconds for "+ str(repeat)+ " times ..."
        isolation.off()
        vent.on()
        for i in range(repeat):
            mfc.asynchronousMoveTo(flow)
            sleep(1)
            systemPressure.moveTo(4)
            sleep(1)
            mfc.asynchronousMoveTo(0)
            sleep(duration)
            systemPressure.asynchronousMoveTo(0)
            sleep(10.0)
        print "flush system completed."

    def getState(self):
        try:
            if not self.statecli.isConfigured():
                self.statecli.configure()
                output=int(self.statecli.caget())
                self.statecli.clearup()
            else:
                output=int(self.statecli.caget())
            return sequencestat[output]
        except:
            print "Error returning current state"
            return 0

    def setSequence(self,new_position):
        try:
            if not self.setsequencecli.isConfigured():
                self.setsequencecli.configure()
                self.setsequencecli.caput(new_position)
                self.setsequencecli.clearup()
            else:
                self.setsequencecli.caput(new_position)
        except:
            print "error setting sequence"
            
    def on(self):
        self.setSequence(0)
        
    def off(self):
        self.setSequence(1)
        
    def reset(self):
        self.setSequence(2)
        
#### methods for scannable 
    def getPosition(self):
        return self.getState()
    
    def asynchronousMoveTo(self, new_position):
        self.setSequence(float(new_position))

    def isBusy(self):
        return False

    def atScanStart(self):
        pass
    def atPointStart(self):
        pass
    def stop(self):
        pass
    def atPointEnd(self):
        pass
    def atScanEnd(self):
        pass
    
    def xgasin(self, mfc=mfc1, flow=0.1, pressuretarget=1.0, systemPressure=bpr, sleepdelta=1, sleepmove=0.5):
        '''select gas flow control and set system pressure'''
        print "xgasin: inject gas %s into the system." % (mfc.getGasType())
        mfc.asynchronousMoveTo(flow)
        #systemPressure.moveTo(pressuretarget)
        sleep(sleepdelta)
        systemPressure.moveTo(pressuretarget, sleepmove)
        #mfc.asynchronousMoveTo(flow)
        sleep(sleepdelta)
        mfc.asynchronousMoveTo(0)
        print "The system reaches at target pressure %f" % (pressuretarget)

# Usage example
#gasrig=GasRigClass("gasrig", "BL11J-EA-GIR-01:")
