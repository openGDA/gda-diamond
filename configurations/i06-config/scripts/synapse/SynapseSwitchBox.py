'''
create scannables 'synapse_s1','synapse_s2','synapse_s3','synapse_s4','synapse_cg','synapse_setall' to control 
Synapse Switch Box in EPICS

Created on 9 Nov 2018

@author: fy65
'''
from gda.epics import CAClient
from gda.device.scannable import ScannableMotionBase
from time import sleep
# CONSTANTS HERE
PV_ROOT="BL06I-EA-PLC-01:SW:"
SET_ALL="SET:ALL"
RBV="_RBV"

S_POSITIONS={0:'Open circuit',
             1:'Source high',
             2:'Source low',
             3:'Sense high',
             4:'Sense low',
             5:'STV',
             6:'DVM'       
             }
 
CG_POSITIONS={0:'Open circuit',
              1:'Source high',
              2:'Source low',
              3:'STV',
              4:'DVM'       
              }
 
SET_ALL_POSITIONS={0:'Open circuit',
                   1:'STV'
                   }

class EpicsReadWriteEnum(ScannableMotionBase):
    '''
    class that creates an instance for a EPICS PV of Enum type.
    '''
    def __init__(self, name, inpvstring, rbvpvstring, formatstring, positions={}):
        '''
        Constructor
        '''
        self.setName(name);
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat([formatstring])
        self.setLevel(5)
        self.incli=CAClient(inpvstring)
        self.rbvcli=CAClient(rbvpvstring)
        self.positions=positions
        
    def atScanStart(self):
        if not self.incli.isConfigured():
            self.incli.configure()
        if not self.rbvcli.isConfigured():
            self.rbvcli.configure()
    
    def atPointStart(self):
        pass
    
    def rawGetPosition(self):
        try:
            if not self.rbvcli.isConfigured():
                self.rbvcli.configure()
            sleep(0.5) # there is no caput callback yet in EPIC
            output=int(self.rbvcli.caget())
            return self.positions[output]
        except:
            raise Exception("%s: Error get current position" % self.getName()) 
    
    def rawAsynchronousMoveTo(self,new_position):
        lKey=None
        try:
            if not self.incli.isConfigured():
                self.incli.configure()
            if isinstance(new_position, str):
                lKey = [key for key, value in self.positions.iteritems() if value == new_position][0]
            elif isinstance(new_position, int):
                lKey=int(new_position)
            else:
                raise Exception("Input must be String or Integer.")
            if lKey is None or (lKey<0 or lKey>=len(self.positions)):
                raise Exception("Request position is not supported.")
            self.incli.caput(lKey)
        except:
            raise Exception("%s: Error set position to '%s'" % (self.getName(), self.positions[lKey]))
       
    
    def isBusy(self):
        return False
    
    def atPointEnd(self):
        pass
    
    def atScanEnd(self):
        if self.incli.isConfigured():
            self.incli.clearup()
        if self.rbvcli.isConfigured():
            self.rbvcli.clearup()
            
    def stop(self):
        pass

    def toFormattedString(self):
        return self.name + " : " + self.getInputNames()[0] +" : " + str(self.getPosition())
    
#create instances
synapse_s1=EpicsReadWriteEnum("synapse_s1", PV_ROOT+"S1", PV_ROOT+"S1"+RBV, "%s", positions=S_POSITIONS)
synapse_s2=EpicsReadWriteEnum("synapse_s2", PV_ROOT+"S2", PV_ROOT+"S2"+RBV, "%s", positions=S_POSITIONS)
synapse_s3=EpicsReadWriteEnum("synapse_s3", PV_ROOT+"S3", PV_ROOT+"S3"+RBV, "%s", positions=S_POSITIONS)
synapse_s4=EpicsReadWriteEnum("synapse_s4", PV_ROOT+"S4", PV_ROOT+"S4"+RBV, "%s", positions=S_POSITIONS)
synapse_cg=EpicsReadWriteEnum("synapse_cg", PV_ROOT+"CG", PV_ROOT+"CG"+RBV, "%s", positions=CG_POSITIONS)
synapse_setall=EpicsReadWriteEnum("synapse_setall", PV_ROOT+SET_ALL, PV_ROOT+SET_ALL, "%s", positions=SET_ALL_POSITIONS)

