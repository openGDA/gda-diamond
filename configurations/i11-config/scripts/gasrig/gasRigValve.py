'''
Created on 6 Dec 2013

@author: fy65
'''

ROOT_PV="BL11I-EA-GIR-01:VENT:"
VALVE_CONTROL="CON"
VALVE_STATUS="STA"
VALVE_MODE="MODE"
VALVE_INTERLOCKS="ILKSTA"
VALVE_OPERATIONS="OPS"
VALVE_DEBOUNCE_SET="SETADB"
VALVE_DEBOUNCE_GET="ADB"

CONTROL_SEQUENCE={0:"on",1:"off",2:"reset"}
STATUS_SEQUENCE={0:"Fault",1:"On & AtSpeed",2:"On & NotAtSpeed",3:"Off",4:"Off & AtSpeed"}
MODE_SEQUENCE={0:"Remote",1:"Local"}
INTERLOCKS_SEQUENCE={0:"Failed",1:"Run Ilks OK",2:"OK"}


from gda.epics import CAClient 
from gda.device.scannable import ScannableMotionBase

class GasRigValveClass(ScannableMotionBase):
    '''Create a scannable for a gas injection rig'''
    def __init__(self, name, rootPV):
        self.setName(name);
        self.setInputNames([name])
        self.setLevel(5)
        self.controlcli=CAClient(rootPV+VALVE_CONTROL)
        self.statecli=CAClient(rootPV+VALVE_STATUS)
        self.modecli=CAClient(rootPV+VALVE_MODE)
        self.interlockscli=CAClient(rootPV+VALVE_INTERLOCKS)
        self.operationscli=CAClient(rootPV+VALVE_OPERATIONS)
        
    def getStatus(self):
        try:
            if not self.statecli.isConfigured():
                self.statecli.configure()
                output=int(self.statecli.caget())
                self.statecli.clearup()
            else:
                output=int(self.statecli.caget())
            return STATUS_SEQUENCE[output]
        except:
            print "Error returning current state"
            return 0
        
    def getMode(self):
        try:
            if not self.modecli.isConfigured():
                self.modecli.configure()
                output=int(self.modecli.caget())
                self.modecli.clearup()
            else:
                output=int(self.modecli.caget())
            return MODE_SEQUENCE[output]
        except:
            print "Error returning current state"
            return 0
        
    def getInterlocks(self):
        try:
            if not self.interlockscli.isConfigured():
                self.interlockscli.configure()
                output=int(self.interlockscli.caget())
                self.interlockscli.clearup()
            else:
                output=int(self.interlockscli.caget())
            return INTERLOCKS_SEQUENCE[output]
        except:
            print "Error returning current state"
            return 0

    def getOperations(self):
        try:
            if not self.operationscli.isConfigured():
                self.operationscli.configure()
                output=int(self.operationscli.caget())
                self.operationscli.clearup()
            else:
                output=int(self.operationscli.caget())
            return output
        except:
            print "Error returning current state"
            return 0

    def setControl(self,new_position):
        try:
            if not self.controlcli.isConfigured():
                self.controlcli.configure()
                self.controlcli.caput(new_position)
                self.controlcli.clearup()
            else:
                self.controlcli.caput(new_position)
        except:
            print "error setting sequence"
            
    def on(self):
        self.setControl(0)
        
    def off(self):
        self.setControl(1)
        
    def reset(self):
        self.setControl(2)
        
#### methods for scannable 
    def getPosition(self):
        return self.getStatus()
    
    def asynchronousMoveTo(self, new_position):
        self.setControl(float(new_position))

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
    