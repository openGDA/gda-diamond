'''
filename: positionCompare.py

This class uses position compare to determine if work requested is done or not. It does not require the actual device status for this.
The scannable's positional tolerance must be set, which is used to determine if the move requested is done or not.

Created on 4 Jan 2021

@author: fy65
'''

from gda.epics import CAClient 
from gda.device.scannable import ScannableMotionBase

class PositionCompareClass(ScannableMotionBase):
    '''Create a position compare scannable with separate PV names for demand, target and readback positions.'''
    def __init__(self, name, pvdemand, pvreadback, tolerance, unitstring, formatstring):
        ''' constructor
        @param name: name of this scannable
        @param pvdemand: the PV name for the demand position
        @param pvreadback: the PV name for the current position or readback
        @param tolerance: the tolerance value within which the readback position is regarded as reached to the demand position
        @param unitstring: the String value of the unit
        @param formatstring: the format string for the returned value.        
        '''
        self.setName(name);
        self.setInputNames([name])
        self.unit=unitstring
        self.setOutputFormat([formatstring])
        self.setLevel(3)
        self.demand=CAClient(pvdemand)
        self.readback=CAClient(pvreadback)
        self._tolerance=tolerance
        
    def setTolerance(self, tolerance):
        self._tolerance=tolerance
        
    def getTolerance(self):
        return self._tolerance
        
    def atScanStart(self):
        if not self.demand.isConfigured():
            self.demand.configure()
        if not self.readback.isConfigured():
            self.readback.configure()
         
    def rawGetPosition(self):
        '''read the magnet value
        '''
        try:
            if not self.readback.isConfigured():
                self.readback.configure()
                output=float(self.readback.caget())
                self.readback.clearup()
            else:
                output=float(self.readback.caget())
            return output
        except Exception, e:
            print("Error returning Magnet value")
            raise e
        

    def getTargetPosition(self):
        '''read the demand position of the magnet 
        '''
        try:
            if not self.demand.isConfigured():
                self.demand.configure()
                target=float(self.demand.caget())
                self.demand.clearup()
            else:
                target=float(self.demand.caget())
            return target
        except Exception,e:
            print("Error returning demand position")
            raise e
       
    def rawAsynchronousMoveTo(self,new_position):
        try:
            if not self.demand.isConfigured():
                self.demand.configure()
                self.demand.caput(new_position)
                self.demand.clearup()
            else:
                self.demand.caput(new_position)
        except Exception,e:
            print("error moving to demand position %r %s" % (new_position, self.unit))
            raise e

    def rawIsBusy(self):
        return ( not abs(self.rawGetPosition() - self.getTargetPosition()) < self._tolerance)

    def atScanEnd(self):
        if self.demand.isConfigured():
            self.demand.clearup()
        if self.readback.isConfigured():
            self.readback.clearup()
            
    def stop(self):
        '''stop magnet by setting current position into demand position
        '''
        curpos = self.rawGetPosition()
        self.rawAsynchronousMoveTo(curpos)

    def toString(self):
        return self.name + " : " + str(self.getPosition())
              
