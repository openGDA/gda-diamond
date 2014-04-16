#
# Example script to run a single spectrum scan.
#

from gda.scan.ede import EdeSingleExperiment

def runsinglespectrumscan():
    #########################
    # EDIT THESE VALUES:
    i0AccumulationTime = 0.1 # In second
    i0NoOfAccumulcation = 1
    iTaccumulationTime = 0.1 # In second
    iTNoOfAccumulcation = 1
    
    i0MotorPositions = {'sample_x':0.0,'sample_y':1.0,'sample_finex':1.0}
    itMotorPositions = {'sample_x':1.0,'sample_y':2.0,'sample_finex':1.0}

    # Uncomment the following to use IRef
        
    iRefMotorPositions = {'sample_x':1.0,'sample_y':2.0,'sample_finex':1.0}
    irefIntegrationTime = 0.3 # In second
    irefNoOfAccumulations = 4
            
    filePrefix = "test"
    
    detectorName = "xh"
    topCheckerScannable = "topup"
    shutterName = "shutter2"

    #########################
    # DO NOT EDIT:
    theExperiment = EdeSingleExperiment(i0AccumulationTime, i0NoOfAccumulcation, iTaccumulationTime, iTNoOfAccumulcation, mapToJava(i0MotorPositions), mapToJava(itMotorPositions), detectorName, topCheckerScannable, shutterName)
    theExperiment.setFilenameTemplate(filePrefix + "_%s")
    if 'iRefMotorPositions' in locals():
         theExperiment.setIRefParameters(mapToJava(iRefMotorPositions), irefIntegrationTime, irefNoOfAccumulations)
    theExperiment.runExperiment()
    
runsinglespectrumscan()