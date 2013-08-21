#
# Drives the single_scan.py script using serializable arguments so can easily be called from the UI.
#
#
#
#
from data_collection.single_scan import SingleScanExperiment

from gda.factory import Finder
from gda.device.scannable import AlignmentStageScannable
from gda.scan import AlignmentStageScanPosition,ExplicitScanPositions,EdePositionType

class SingleScanDriver():
    
    def __init__(self,detectorName,i0_scantime,i0_numberscans,it_scantime = -1,it_numberscans = -1):
        self.detectorName = detectorName
        self.detector = Finder.getInstance().find(detectorName)
        self.alignmentstage = Finder.getInstance().find("alignment_stage")
        self.xMotor = Finder.getInstance().find("sample_x")
        self.yMotor = Finder.getInstance().find("sample_y")
        self.i0_scantime = i0_scantime
        self.i0_numberscans = i0_numberscans
        self.it_scantime = it_scantime
        self.it_numberscans = it_numberscans
        if self.it_scantime == -1:
            self.it_scantime = self.i0_scantime
            
        if self.it_numberscans == -1:
            self.it_numberscans = self.i0_numberscans
        
    def setInBeamPosition(self,xPos,yPos=None):
        
        if yPos == None:
            # assume xPos is a string of an AlignmentStageScannable.Devices
            device = AlignmentStageScannable.Devices.getDevice(xPos)
            self.inbeamPosition = AlignmentStageScanPosition(EdePositionType.INBEAM,device,self.alignmentstage)
        else:
            self.inBeamPosition = ExplicitScanPositions(EdePositionType.INBEAM, xPos, yPos, self.xMotor, self.yMotor);

        
    def setOutBeamPosition(self,xPos,yPos=None):
        if yPos == None:
            # assume xPos is a string of an AlignmentStageScannable.Devices
            device = AlignmentStageScannable.Devices.getDevice(xPos)
            self.outbeamPosition = AlignmentStageScanPosition(EdePositionType.OUTBEAM,device,self.alignmentstage)
        else:
            self.outbeamPosition = ExplicitScanPositions(EdePositionType.OUTBEAM, xPos, yPos, self.xMotor, self.yMotor);

        
    def doCollection(self):
        i0scanparams = EdeScanParameters.createSingleFrameScan(self.i0_scantime,self.i0_numberscans);
        itscanparams = EdeScanParameters.createSingleFrameScan(self.it_scantime,self.it_numberscans);
        
        theExperiment = EdeSingleExperiment(i0scanparams, itscanparams, self.inBeamPosition, self.outBeamPosition, self.detector);
        theExperiment.runExperiment()
        
        return theExperiment.getAsciiFilename()
