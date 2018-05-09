def make_positions(start, end, step):
    positions=[]
    position=start
    while position < end:
        positions.append(position)
        position += step
        
    return positions

def make_reverse_positions(_positions):
    positions=list(_positions)
    reverse = positions[:]
    reverse.reverse()
    return tuple(positions + reverse[1:])

import gda.scan.ScanPositionProvider
import gda.scan.ScanBase
from gda.device.scannable import ScannableUtils

class ForwardAndBack(gda.scan.ScanPositionProvider):
    """
    Class that provides points to scan from start to end and then back to start
    """
    def __init__(self, scannable, start, end, _step):
        self.scannable = scannable
        self.start = start
        self.end= end
        self._step = _step
        step = gda.scan.ScanBase.sortArguments(start, end, _step);
        numberSteps = ScannableUtils.getNumberSteps(scannable, start, end, step);
        numberOfPoints = numberSteps+1
        self.points=[]
        self.points.append(start)
        previousPoint=start
        for i in range(numberSteps):
            nextPoint = ScannableUtils.calculateNextPoint(previousPoint, step)
            self.points.append(nextPoint)
            previousPoint = nextPoint
            
        cpy = self.points[:]
        cpy.reverse()
        #remove first point
        cpy = cpy[1:]
        self.points = self.points + cpy
        
    def get(self,index):
        return self.points[index]

    def size(self): 
        return len(self.points)
    def __str__(self):
        return "ForwardAndBack for %s, start:%s, end:%s, step:%s" %(self.scannable.name, self.start, self.end, self._step)
    def __repr__(self):
        return self.__str__() 

class MyPositions(ForwardAndBack):
    def __init__(self, scannable, start, end, step):
        ForwardAndBack.__init__(self,scannable, start, end, step)
    def __str__(self):
        return "MyPositions for %s, start:%s, end:%s, step:%s" %(self.scannable.name, self.start, self.end, self._step)


