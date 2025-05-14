from uk.ac.diamond.daq.scanning import ScanHookParticipant
from org.slf4j import LoggerFactory

"""
This scan participant makes sure that the VMA camera is stopped before starting a mapping scan.
(the detector is restarted after the scan finishes if it was running before the scan).

(PrepareForScan is called *before* the AreaDetectorRunnableDevice 'configure' method is run, and
before any collection strategy methods are run by ADDetector.atScanStart)).

"""
class VMAHooks(ScanHookParticipant) :
    
    def __init__(self, name, vma_detector, vma_detector_name="VMA"):
        self.setName(name)
        self.initial_acquire_state = 0
        self.scan_uses_vma = False
        self.logger = LoggerFactory.getLogger(name)
        self.vma_detector = vma_detector
        self.vma_detector_name = vma_detector_name # name of the VMA detector RunnableDevice object
        
    # Stop the VMA detector before detector configuration starts
    def atPrepareForScan(self, scan_model) :
        # Chack to see if scan uses VMA detector
        detectors = scan_model.getDetectors()
        det_names = [det.getName() for det in detectors]
        self.scan_uses_vma = self.vma_detector_name in det_names

        self.logger.debug("Detector names : {}, Scan uses VMA detector {}", det_names, self.scan_uses_vma)

        if self.scan_uses_vma :
            self.stop_detector()

    def atScanFinally(self):
        # Start the detector if it was running before the scan
        if self.scan_uses_vma and self.initial_acquire_state == 1 :
            self.start_detector()

    # Stop the VMA detector (using functions on the VMA 'ADDetector' object)
    def stop_detector(self):
        self.logger.debug("Stopping VMA detector")
        base=self.vma_detector.getAdBase()
        # Store the current 'acquire' state, so we can restart the detector after the scan finishes
        self.initial_acquire_state = base.getAcquireState()
        
        base.stopAcquiring()
        ndfile=self.vma_detector.getNdFile()
        ndfile.stopCapture()

    def start_detector(self):
        self.logger.debug("Starting VMA detector")
        base = self.vma_detector.getAdBase()
        base.startAcquiring()


vma_stop_start = VMAHooks("vma_stop_start", VMA)
vma_stop_start.addScanParticipant()
add_reset_hook(vma_stop_start.removeScanParticipant)
