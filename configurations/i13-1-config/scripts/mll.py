from gdascripts.parameters import beamline_parameters
def mpx(xPixels, yPixels=0,title="No title"):
    """
    
    Allows the maxipix detector to be used to monitor an external triggering system.
    If yPixels=0 (default) the data is recorded in a 1d series of xPixels+1 images
    If yPixels>0 the data is recorded in a 2d array of (xPixels+1) * (yPixels+1) images
    
    
    """    
    jms=beamline_parameters.JythonNameSpaceMapping()    
    jms.mpx_external_scan_monitor.run(xPixels=xPixels,yPixels=yPixels, scannablesToRecord=[jms.mll_ssx, jms.mll_ssy, jms.mll_ssz], title=title)