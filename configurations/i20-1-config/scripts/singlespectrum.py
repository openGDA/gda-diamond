#
# Example script to run a single spectrum scan.
#
# Uses new EDE scanning mechanism
#
# Richard Woolliscroft 22 July 2013
#

from gda.scan.ede import EdeSingleExperiment
from gda.scan.ede.position import ExplicitScanPositions;
from gda.scan.ede.position import EdePositionType;
from uk.ac.gda.exafs.ui.data import EdeScanParameters;

def runsinglespectrumscan():
    ########################
    # EDIT THESE VALUES:
    scanTimeInSeconds     = 0.001
    numberOfScansPerFrame  = 1
    
    xmotorobject   = sample_x
    ymotorobject   = sample_y
    detectorobject = xstrip
    
    inbeam_xmotorposition = 0
    inbeam_ymotorposition = 0
     
    outbeam_xmotorposition = 0.2
    outbeam_ymotorposition = 0.2
    ########################
    
    
    scanparams = EdeScanParameters.createSingleFrameScan(scanTimeInSeconds,numberOfScansPerFrame);
    
    outBeamPosition = ExplicitScanPositions(EdePositionType.OUTBEAM,outbeam_xmotorposition,outbeam_ymotorposition,xmotorobject,ymotorobject);
    inBeamPosition = ExplicitScanPositions(EdePositionType.INBEAM, inbeam_xmotorposition, inbeam_ymotorposition, xmotorobject, ymotorobject);
    
    theExperiment = EdeSingleExperiment(scanparams, outBeamPosition, inBeamPosition, detectorobject);
    theExperiment.runExperiment()
    
runsinglespectrumscan()


