from gda.epics import CAClient 
from gda.configuration.properties import LocalProperties
def fixEpicsTrajectoryStatus():
    trajReadStatus = CAClient("BL18I-MO-TABLE-01:TRAJ1:Readback")
    trajReadStatus.configure()
    trajReadStatus.caput(0)
    xmapCaptureStop = CAClient("BL18I-EA-DET-04:HDF:Capture")
    xmapCaptureStop.configure()
    xmapCaptureStop.caput(0)
    xmapCollectMode = CAClient("BL18I-EA-DET-04:CollectMode")
    xmapCollectMode.configure()
    xmapCollectMode.caput(0)
    
def fixMapScan():
    LocalProperties.set("gda.scan.useScanPlotSettings" , "true")