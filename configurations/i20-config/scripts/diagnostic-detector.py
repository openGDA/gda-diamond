from gda.device.detector import DetectorBase
import time

class DiagnosticDetector(DetectorBase):
    """
        Wrapper class for reading out d9_current as a detector in a scan
        to allow a sleep to be added before reading out the PV value (PV update in response
        to change in beam can be slow).
        
        * collectionTime of the detector (as set by scan command) is used as the sleep time in collectData,
        * there an extra sleep before the very first point, so avoid reading too early.
        
        
        1 sec 'collection time' seems good; 0.5 sec might be acceptable (very slight shift in profile when doing
        bragg offset scan due to PV update speed)
        
        imh 15/11/2023
    """
    def __init__(self, name, diagnostic_current):
        self.setName(name)
        self.inputNames = []
        self.diagnostic_current = diagnostic_current
        self.outputFormat = diagnostic_current.getOutputFormat()
        self.collectionTime = 1.0
        self.firstPointSleepTime = 1.0
        self.firstPoint = False
        
    def collectData(self):
        if self.firstPoint :
            # Extra sleep needed before first point, to avoid reading value too early
            time.sleep(self.firstPointSleepTime)
            self.firstPoint = False
        
        time.sleep(self.collectionTime)

    def atScanLineStart(self):
        self.firstPoint = True
        
    def getStatus(self):        
        return 0

    def readout(self):
        return self.diagnostic_current.getPosition()

    def getDescription(self):
        return " "

    def getDetectorID(self):
        return " "

    def getDetectorType(self):
        return " "
    
    def createsOwnFiles(self):
        return False
    
# NB make sure scan rate of d9 current PV is set to 0.1 seconds, so it updates quickly in response to beam change.
# e.g. caput BL20I-DI-PHDGN-09:DIODE:I.SCAN 9, 

d9_current_detector = DiagnosticDetector("d9_current_detector", d9_current)
d9_current_detector.setOutputFormat(["%.4f"])
d9_current_detector.configure()
detectorPreparer.setDiagnosticDetector(d9_current_detector)
detectorPreparer.setDiagnosticValve(d9_diode)
