from uk.ac.gda.exafs.ui.data import TimingGroup
from uk.ac.gda.exafs.ui.data import EdeScanParameters
from BeamlineParameters import JythonNameSpaceMapping

def doMultipleCollections(number_of_scans = 1, time_per_scan = 1):
    jythonmapper = JythonNameSpaceMapping()
#    time_per_frame = float(number_of_scans) * float(time_per_scan)
    
    myscan = EdeScanParameters()
    group1 = TimingGroup()
    group1.setLabel("group1");
    group1.setNumberOfFrames(1);
    group1.setTimePerScan(time_per_scan);
    group1.setNumberOfScansPerFrame(number_of_scans);
    myscan.addGroup(group1)
    jythonmapper.xh.loadParameters(myscan)
    
    jythonmapper.xh.collectData()
    jythonmapper.xh.waitWhileBusy()
    return jythonmapper.xh.readFrameToArray(0)
    
def doSingleCollection(time = 1):
    return doMultipleCollections(1,time)


