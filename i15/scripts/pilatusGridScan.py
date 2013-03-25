def pilatusGridScan():
    
    jythonNameMap = beamline_parameters.JythonNameSpaceMapping()

    #pixel size = 172 x 172 micrometers
    
    ktheta_center = 0
    ktheta_range = 10
    
    gamma_center = 0    
    gamma_range = 10
    
    ktheta_start = ktheta_center - (ktheta_range/2.)
    ktheta_stop = ktheta_center + (ktheta_range/2.)

    gamma_start = gamma_center - (gamma_range/2.)
    gamma_stop = gamma_center + (gamma_range/2.)

    pilatus_size_x = 83.8 #mm
    pilatus_size_y = 33.5 #mm

    detector_distance = 100

    ktheta_step = math.tan(pilatus_size_y/detector_distance)
    gamma_step = math.tan(pilatus_size_x/detector_distance)

    ktheta = jythonNameMap.ktheta
    gamma = jythonNameMap.gamma
    
    pilatus = jythonNameMap.pilatus
    exposureTime = 30
    noOfExpPerPos = 1
    fileName="grid"
    sync=False
    
    wrappedDetector = detector_axis_wrappers._getWrappedDetector(None, 1, 1, 1, pilatus,  exposureTime, noOfExpPerPos, fileName, sync)
    scan = ConcurrentScan([ktheta, ktheta_start, ktheta_stop, ktheta_step, gamma, gamma_start, gamma_stop, gamma_step, wrappedDetector])
    scan.runScan()