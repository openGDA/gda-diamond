#
# Example script to run a single spectrum scan.
#
# Uses new EDE scanning mechanism

from gda.scan.ede import EdeCyclicExperiment
from uk.ac.gda.exafs.ui.data import TimingGroup

def runcyclicexperment():
    ########################
    # EDIT THESE VALUES:
    numberOfRepetitions = 2
    
    i0AccumulationTime = 0.1 # In second
    i0NoOfAccumulcation = 1
    
    i0MotorPositions = {'sample_x':0.0,'sample_y':1.0,'sample_finex':1.0}
    itMotorPositions = {'sample_x':1.0,'sample_y':2.0,'sample_finex':1.0}
    
    # Uncomment the following 3 lines to use IRef
        
    iRefMotorPositions = {'sample_x':1.0,'sample_y':2.0,'sample_finex':1.0}
    irefIntegrationTime = 0.2 # In second
    irefNoOfAccumulations = 4
    
    plotEvery = 2 # In second
    
    groups = []
    #
    # repeat this section for every timing group
    #
    group = TimingGroup();
    group.setLabel("group1");
    group.setNumberOfFrames(10);
    group.setTimePerScan(0.05);
    group.setTimePerFrame(5);
    group.setPreceedingTimeDelay(0.0)
    groups += [group];
        
    group = TimingGroup();
    group.setLabel("group2");
    group.setNumberOfFrames(10);
    group.setTimePerScan(0.05);
    group.setTimePerFrame(5);
    group.setPreceedingTimeDelay(0.0)
    groups += [group];

    detectorName = "xh"
    topCheckerScannable = "topup"
    shutterName = "shutter2"

    ########################

    theExperiment = EdeCyclicExperiment(i0AccumulationTime, i0NoOfAccumulcation, groups,  mapToJava(i0MotorPositions), mapToJava(itMotorPositions), detectorName, topCheckerScannable, shutterName, numberOfRepetitions)
    theExperiment.setNoOfSecPerSpectrumToPublish(plotEvery)
    if 'iRefMotorPositions' in locals():
        theExperiment.setIRefParameters(mapToJava(iRefMotorPositions), irefIntegrationTime, irefNoOfAccumulations)
    theExperiment.runExperiment()
    
runcyclicexperment()