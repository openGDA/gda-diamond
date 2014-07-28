'''
Created on 6 Dec 2013

@author: fy65
'''
ROOT_PV="I11GasRig:"
SEQUENCE_CONTROL="SEQ:CON"
SEQUENCE_STATUS="SEQ:STA"
AT_PRESSURE_PROC="ATPRESSURE.PROC"

sequence={0:"on",1:"off",2:"reset"}

from gda.epics import CAClient 
from gda.device.scannable import ScannableMotionBase

class GasRigClass(ScannableMotionBase):
    '''Create a scannable for a gas injection rig'''
    def __init__(self, name, rootPV):
        self.setName(name);
        self.setInputNames([name])
        self.setLevel(3)
        self.setsequencecli=CAClient(rootPV+SEQUENCE_CONTROL)
        self.statecli=CAClient(rootPV+SEQUENCE_STATUS)
        self.atpressurecli=CAClient(rootPV+AT_PRESSURE_PROC)
        
    def getState(self):
        try:
            if not self.statecli.isConfigured():
                self.statecli.configure()
                output=int(self.statecli.caget())
                self.statecli.clearup()
            else:
                output=int(self.statecli.caget())
            return sequence[output]
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

    def atPressure(self):
        try:
            if not self.atpressurecli.isConfigured():
                self.atpressurecli.configure()
                self.atpressurecli.caput(1)
                self.atpressurecli.clearup()
            else:
                self.atpressurecli.caput(1)
        except:
            print "error setting at_pressure"

