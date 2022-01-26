from gda.device.detector.areadetector import NDStatsGroupFactory
from gda.device.scannable import ScannableBase



class NDStatsMonitor(ScannableBase):
    '''
    Scannable to act as a monitor to read stats pvs live from the plugin.
    Doesn't make any guarantees that the plugin is enabled so data may be old
    Construct by providing a name and an ADDetector that has a ndStats set
    '''

    def __init__(self, name, detector):
        self.statsGroup = NDStatsGroupFactory.getStatsInstance(detector.getNdStats())
        self.centroidGroup = NDStatsGroupFactory.getCentroidInstance(detector.getNdStats())
        self.setName(name)
        self.setInputNames([])
        self.setExtraNames(self.statsGroup.getFieldNames() + self.centroidGroup.getFieldNames())
        self.setOutputFormat(self.statsGroup.getFieldFormats() + self.centroidGroup.getFieldFormats())

    def moveTo(self, position):
        pass

    def getPosition(self):
        return self.statsGroup.getCurrentDoubleVals() + self.centroidGroup.getCurrentDoubleVals()

    def isBusy(self):
        return False