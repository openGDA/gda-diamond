"""
Created on Fri Sep  6 13:29:38 2019

@author: xke49157
"""

def sample_scan(scan_size, exposure_time, scan_centre=[12.3, 12.9], step_size=0.2):
    ''' This function aims to simplify the scan command.
        The user can enter a minimum of 2 arguments to perform the scan.
        'scan_size' is the size of the final image in mm
            For example, a value of 2 gives a final image of size 2mmx2mm
        'exposure_time' is the exposure time of the camera for each image capture
            This must be found by the user prior to performing the scan
        'scan_centre' denotes the centre of the scan in PCSS coordinates.
            The default value is set to be at roughly the centre of the cartridge cap.
            So a scan_size of 8 will produce an 8mmx8mm image centred on the cap centre.
            This variable is optional.
        'step_size' denotes the the step the motors take between each image capture (in mm).
            This doesn't need to be changed, but the program will work with values of less than
            0.2.
    '''
    try:
        scan_size = round(float(scan_size), 1)
        exposure_time = float(exposure_time)
    except:
        print("scan_size or exposure_time value invalid")
    if scan_size >= 8:
        scan_size = 8
    if step_size >= 0.2:
        step_size = 0.2
    scan_variables = []
    scan_variables.append(pcssx)
    scan_variables.append(scan_centre[0]-scan_size/2)
    scan_variables.append(scan_centre[0]+scan_size/2)
    scan_variables.append(step_size)
    scan_variables.append(pcssy)
    scan_variables.append(scan_centre[1]-scan_size/2)
    scan_variables.append(scan_centre[1]+scan_size/2)
    scan_variables.append(step_size)
    scan_variables.append(pcsscam)
    scan_variables.append(exposure_time)
    scan_variables.append(processImages)
    print scan_variables
    scan([x for x in scan_variables])