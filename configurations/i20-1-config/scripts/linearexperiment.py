#
# Example script to run a single spectrum scan.
#
# Uses new EDE scanning mechanism
#
# Richard Woolliscroft 22 July 2013
#

from gda.scan.ede import EdeLinearExperiment
from gda.scan.ede.position import EdePositionType,ExplicitScanPositions
from uk.ac.gda.exafs.ui.data import EdeScanParameters, TimingGroup


def runlinearexperment():
    ########################
    # EDIT THESE VALUES:
    
    xmotorobject   = sample_x
    ymotorobject   = sample_y
    detectorobject = xstrip
    
    inbeam_xmotorposition = 0
    inbeam_ymotorposition = 0
     
    outbeam_xmotorposition = 0.2
    outbeam_ymotorposition = 0.2
    
    groups = []
    #
    # repeat this section for every timing group
    #
    group = TimingGroup();
    group.setLabel("group");
    group.setNumberOfFrames(10);
    group.setTimePerScan(0.05);
    group.setNumberOfScansPerFrame(5);
    groups += [group];

    ########################

    scanparams = EdeScanParameters(groups)
    
    outBeamPosition = ExplicitScanPositions(EdePositionType.OUTBEAM,outbeam_xmotorposition,outbeam_ymotorposition,xmotorobject,ymotorobject);
    inBeamPosition = ExplicitScanPositions(EdePositionType.INBEAM, inbeam_xmotorposition, inbeam_ymotorposition, xmotorobject, ymotorobject);
    
    theExperiment = EdeLinearExperiment(scanparams, outBeamPosition, inBeamPosition, detectorobject);
    theExperiment.runExperiment()
    
runlinearexperment()


