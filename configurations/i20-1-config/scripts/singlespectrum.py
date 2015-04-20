#working on 13 Feb 2015 after change EdeSingleExperiment to SingleSpectrumScan
# Example script to run a single spectrum scan.

from gda.scan.ede import SingleSpectrumScan

def runsinglespectrumscan():
    #########################
    # EDIT THESE VALUES:
    i0AccumulationTime = 0.000027 # In second
    i0NoOfAccumulcation = 500
    iTaccumulationTime = 0.000027 # In second
    iTNoOfAccumulcation = 500
    
#    i0MotorPositions = {'sample_x':0.0,'sample_y':1.0,'sample_finez':1.0}
    i0MotorPositions = {'sample_finex':9.9999}
    itMotorPositions = {'sample_finex':9.9999}

    # Uncomment the following to use IRef
        
#    iRefMotorPositions = {'sample_x':1.0,'sample_y':2.0,'sample_finex':1.0}
    iRefMotorPositions = {'sample_finex':9.9999,'sample_finey':12.0}
    irefIntegrationTime = 0.3 # In second
    irefNoOfAccumulations = 4
            
    filePrefix = "test"
    
    detectorName = "frelon"
    topCheckerScannable = "topup"
    shutterName = "shutter2"

    #########################
    # DO NOT EDIT:
    theExperiment = SingleSpectrumScan(i0AccumulationTime, i0NoOfAccumulcation, iTaccumulationTime, iTNoOfAccumulcation, mapToJava(i0MotorPositions), mapToJava(itMotorPositions), detectorName, topCheckerScannable, shutterName)
    if 'iRefMotorPositions' in locals():
         theExperiment.setIRefParameters(mapToJava(i0MotorPositions),mapToJava(iRefMotorPositions), i0AccumulationTime, i0NoOfAccumulcation, irefIntegrationTime, irefNoOfAccumulations)
    theExperiment.runExperiment()
    
    
runsinglespectrumscan()
