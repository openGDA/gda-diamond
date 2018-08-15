from gda.device.scannable import ScannableBase
from gda.device.scannable import PseudoDevice

class SimplestPD(PseudoDevice):
    """Device to allow control and readback of X value"""
    def __init__(self, name, position):
        self.setName(name)
        self.setInputNames([name])
        self.X = position
        
    def rawIsBusy(self):
        return 0

    def rawGetPosition(self):
        return self.X

    def rawAsynchronousMoveTo(self,new_position):
        self.X = new_position    

class Attenuation(ScannableBase):
    '''pseudo device to move stuff, multiple axis simultaneously'''

    def __init__(self, name):
        self.setName(name)
        self.energy=bkeV
        self.filter=d3filter
        self.calibration={  "Clear" : [ 0, 0, 0],
                            "0.05mm Al" : [3.11, 2.57, 0.25],
                            "0.1mm Al" : [3.33, 3.87, 0.27],
                            "0.25mm Al" : [5.22, 4.65, 0.36],
                            "0.5mm Al" : [9.65, 4.69, 0.61] }
        
    def logItOverI0(self, filterpos):
            if filterpos not in self.calibration.keys():
                raise DeviceException("attenutator "+self.filter.getName()+" at unknown position")
            ene = self.energy.getPosition()
            arr = self.calibration[filterpos]
            return arr[0]/(arr[1]-ene)+arr[2]

    def getPosition(self):
        filterpos = self.filter.getPosition()
        return self.logItOverI0(filterpos)

    def asynchronousMoveTo(self,p):
        disttopos={}
        for pos in self.calibration.keys():
            disttopos[abs(p-self.logItOverI0(pos))] = pos
        keys = disttopos.keys()
        keys.sort()
        target = disttopos[keys[0]]
        self.filter.asynchronousMoveTo(target)

    def isBusy(self):
        return self.filter.isBusy()
    

att=Attenuation("att")
