from gda.device.detector import PseudoDetector

class PCOext(PseudoDetector) :

    def __init__(self, detector):
        self.setName("pcoext")
        self.setInputNames(["pcoext"])
        self.setExtraNames([])
        self.setOutputFormat(["%s"])
        self.pco = detector;

    def collectData(self):
        return

    def readout(self) :
        return "CreatesOwnFiles"

    def createsOwnFiles(self):
        return 1 

    def getStatus(self):
        return 0

    def atScanStart(self):
        self.pco.areaDetector.setImageMode(0)
        self.pco.setCollectionTime(self.getCollectionTime())
        self.pco.atScanStart()
        return

    def stop(self):
        #self.pco.areaDetector.stop()
        return;      

    def atScanEnd(self):
        #self.pco.areaDetector.stop()
        return;


