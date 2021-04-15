'''
Created on 31 Jul 2013

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
class EpicsShutterClass(ScannableMotionBase):
    '''Create PD for single EPICS positioner
    The PVs to control the two EH2 photon shutters on I09 are:
    
    BL09I-PS-SHTR-02:CON
    BL09J-PS-SHTR-02:CON
    
    With states,
    
    0 = Open
    1 = Close
    2 = Reset
    
    The status can be read back on.
    
    BL09I-PS-SHTR-02:STA
    BL09J-PS-SHTR-02:STA
    
    With states,
    
    0 = Fault
    1 = Open
    2 = Opening
    3 = Closed
    4 = Closing
    '''
    def __init__(self, name, pvcontrolstring, pvstatestring, unitstring, formatstring):
        self.setName(name);
        self.setInputNames([name])
        self.Units=[unitstring]
        self.setOutputFormat([formatstring])
        self.setLevel(3)
        self.incli=CAClient(pvcontrolstring)
        self.statecli=CAClient(pvstatestring)
 
    def rawGetPosition(self):
        output=1
        try:
            if not self.incli.isConfigured():
                self.incli.configure()
            output=float(self.incli.caget())
            #self.incli.clearup()
            return int(output)
        except:
            print "Error returning position"
            return 1

    def rawAsynchronousMoveTo(self,new_position):
        try:
            if self.incli.isConfigured():
                self.incli.caput(new_position)
            else:
                self.incli.configure()
                self.incli.caput(new_position)
                #self.incli.clearup()
        except:
            print "error moving to position"

    def isBusy(self):
        try:
            if self.statecli.isConfigured():
                self.status = self.statecli.caget()
            else:
                self.statecli.configure()
                self.status=self.statecli.caget()
                #self.statecli.clearup()
            return int(self.status) == 2 or int(self.status) == 4
        except:    
            print "problem with isMoving string: "+self.status+": Returning busy status"
            return 0
    
psj2=EpicsShutterClass("psj2", "BL09J-PS-SHTR-02:CON","BL09J-PS-SHTR-02:STA","","%d")
psi2=EpicsShutterClass("psi2", "BL09I-PS-SHTR-02:CON","BL09I-PS-SHTR-02:STA","","%d")
