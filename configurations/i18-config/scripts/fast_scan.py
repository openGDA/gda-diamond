from gda.device.scannable import ScannableBase, ScannableUtils
from gda.scan import ScanPositionProvider, ScanBase
import gda.jython.commands.ScannableCommands.scan
import time
import math
'''
tsl =TrajectoryScanLine([continuousSampleX,ScanPositionsTwoWay(sc_MicroFocusSampleX, 0, 1.99, 0.01), HTXmapMca, 0.1] )
scan sc_MicroFocusSampleY 0 2 1 tsl
'''
class   ScanPositionsTwoWay(ScanPositionProvider):
    def __init__(self, firstScannable, start, stop, step):
        self.firstScannable = firstScannable
        self.start = start
        self.stop = stop
        self.step = ScanBase.sortArguments(start, stop, step);
        numberSteps = ScannableUtils.getNumberSteps(firstScannable, self.start, self.stop, self.step)
        self.points = []
        self.points.append(start)
        previousPoint = start
        for i in range(numberSteps):
            nextPoint = ScannableUtils.calculateNextPoint(previousPoint, self.step);
            self.points.append(nextPoint)
            previousPoint = nextPoint
        self.forward=False
        print "Points list is ", self.points

    def get(self, index):
        max_index = self.size()-1
        if index > max_index:
            raise Exception("Position %d is outside possible range : %d" % (index, max_index))
        #self.forward = True
        if self.forward:
            val = self.points[index]
            if index == max_index:
                self.forward = False
        else:
            val = self.points[max_index-index]
            if index == max_index:
                self.forward = True
        #print "direction is forward ", self.forward
        return val;
    
    def size(self):
        return len(self.points)
    
    def __str__(self):
        return "Scan %s from %s to %s in steps of %s. No of points = %d" % (self.firstScannable.getName(), `self.start`,`self.stop`,`self.step`, self.size() ) 
    def toString(self):
        return self.__str__()