from gdascripts.parameters import beamline_parameters
def run(xPixels=100, yPixels=0, scannablesToRecord=[], fast=False, title=""):
    """
    
    Allows the maxipix detector to be used to monitor an external triggering system.
    If yPixels=0 (default) the data is recorded in a 1d series of xPixels+1 images
    If yPixels>0 the data is recorded in a 2d array of (xPixels+1) * (yPixels+1) images
    
    If fast=False a single frame acquisition is performed for each point. This allows a list of other scannables
    to be recorded at the time of each frame in the tuple argument scannablesToRecord
    If fast=True then the detector is configured to acquire a stream of events as fast as the maxipix system allows
    In fast mode no extra scannables can be recorded.
    
    """
    
    if not xPixels > 0:
        raise ValueError("xPixels must be > 0")
    if not yPixels >= 0:
        raise ValueError("yPixels must be >= 0")
    jms=beamline_parameters.JythonNameSpaceMapping()    

    jms.setTitle(title)
    #get variables from global namespace
    mpx=jms.mpx
    if fast :
        if len(scannablesToRecord) > 0 :
            raise ValueError("Unable to record extra scannables in fast mode")
        mpx = jms.mpx_hardwareTrigger
        
    mpx_limaCCD = jms.mpx_limaCCD
    ix=jms.ix
    iy=jms.iy
    scan=jms.scan
    LimaCCD=jms.LimaCCD

    #setup detector
    try:

        mpx_limaCCD.setAcqMode( LimaCCD.AcqMode.SINGLE)
        mpx.setNumberOfFrames(1)
        mpx_limaCCD.setAcqNbFrames(1)
        mpx_limaCCD.setAcqTriggerMode(LimaCCD.AcqTriggerMode.EXTERNAL_TRIGGER_MULTI)
        mpx_limaCCD.stopAcq()
    
    
        #create scan arguments    
        numberFrames=xPixels+1
        scan_args = [ix, 0, xPixels, 1]
        if yPixels!=0:
            numberFrames*=(yPixels+1)
            scan_args += [iy, 0, yPixels, 1 ]
        scan_args += [mpx, .01]
        if not fast:
            scan_args += scannablesToRecord
            #add time last so this is plotted
            scan_args += [ jms.actualTime]
        if fast:
            mpx.atRepScanStart(numberFrames)
            mpx.setNumRepScansIsPerScanLine(False)
            
        
        #run scan
        
        scan(scan_args)
    finally:
        if fast:
            mpx.setNumRepScansIsPerScanLine(True)
        mpx_limaCCD.stopAcq()
        mpx_limaCCD.setAcqTriggerMode(LimaCCD.AcqTriggerMode.INTERNAL_TRIGGER)
        mpx_limaCCD.setAcqMode( LimaCCD.AcqMode.ACCUMULATION)
        

