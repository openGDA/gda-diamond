'''
Created on 29 Aug 2017

@author: fy65
'''
from gda.device.scannable import ScannableBase
from gda.epics import CAClient

class PositionerValue(ScannableBase):
    '''
    an object which set or get the value of motor position for a positioner
    '''
    PV_END_POINT={"Screws":":VALA","Transfer":":VALB","RIXS":":VALC"}

    def __init__(self, name, positioner, pvroot):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.positioner=positioner
        self.screws=CAClient(pvroot+PositionerValue.PV_END_POINT["Screws"])
        self.screws.configure()
        self.transfer=CAClient(pvroot+PositionerValue.PV_END_POINT["Transfer"])
        self.transfer.configure()
        self.rixs=CAClient(pvroot+PositionerValue.PV_END_POINT["RIXS"])
        self.rixs.configure()
        
    def getPosition(self):
        position = str(self.positioner.getPosition())
        if position==PositionerValue.PV_END_POINT.keys[0]:
            return self.screws.caget()
        elif position==PositionerValue.PV_END_POINT.keys[1]:
            return self.transfer.caget()
        elif position==PositionerValue.PV_END_POINT.keys[2]:
            return self.rixs.caget()
        else:
            msg="Positioner: '%s' is in unknown position '%s'" % (self.positioner.getName(), position)
            raise Exception(msg)
        
    def asynchronousMoveTo(self, value):
        value=float(value)
        position = str(self.positioner.getPosition())
        if position==PositionerValue.PV_END_POINT.keys[0]:
            return self.screws.caput(value)
        elif position==PositionerValue.PV_END_POINT.keys[1]:
            return self.transfer.caput(value)
        elif position==PositionerValue.PV_END_POINT.keys[2]:
            return self.rixs.caput(value)
        else:
            msg="Positioner: '%s' is in unknown position '%s'" % (self.positioner.getName(), position)
            raise Exception(msg)
        
    def isBusy(self):
        return False
    
class DummyPositionerValue(ScannableBase):
    '''
    an object which set or get the value of motor position for a positioner
    '''

    def __init__(self, name, positioner, motor, positions={"Screws":1.0,"Transfer":2.0,"RIXS":3.0}):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.positioner=positioner
        self.positions=positions
        self.motor=motor
        
    def getPosition(self):
        position = str(self.positioner.getPosition())
        self.motor.moveTo(self.positions[position]) #move underlying motor to position for comparing value later
        return self.positions[position]

        
    def asynchronousMoveTo(self, value):
        value=float(value)
        position = str(self.positioner.getPosition())
        self.positions[position]=value
        
    def isBusy(self):
        return False