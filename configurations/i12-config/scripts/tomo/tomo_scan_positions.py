class   tomoScan_positions(ScanPositionProvider):
    def __init__(self, step, darkFieldInterval, flatFieldInterval,
             inBeamPosition, outOfBeamPosition, points):
        self.step = step
        self.darkFieldInterval = darkFieldInterval
        self.flatFieldInterval = flatFieldInterval
        self.inBeamPosition = inBeamPosition
        self.outOfBeamPosition = outOfBeamPosition
        self.points = points

    def get(self, index):
        return self.points[index]
    
    def size(self):
        return len(self.points)
    
    def __str__(self):
        return "Step: %f Darks every:%d Flats every:%d InBeamPosition:%f OutOfBeamPosition:%f Optimize every:%d numImages %d " % \
            ( self.step,self.darkFieldInterval,self.flatFieldInterval, self.inBeamPosition, self.outOfBeamPosition, self.size() ) 
    def toString(self):
        return self.__str__()