"""
Performs software triggered tomography
"""

from time import sleep

from pcoDetectorWrapper import PCODetectorWrapper
from gda.jython.commands.ScannableCommands import inc, scan, pos, createConcurrentScan

import sys
import time
import shutil
import gda
from gdascripts.parameters import beamline_parameters
from gdascripts.messages import handle_messages
from gda.device.scannable import ScannableBase
from gda.device.detector import DetectorBase
from gda.scan import ScanPositionProvider
from gda.device.scannable import ScannableBase, ScannableUtils
from gda.device.scannable.scannablegroup import ScannableGroup

class EnumPositionerDelegateScannable(ScannableBase):
    def __init__(self, name, delegate):
        self.name = name
        self.inputNames = [name]
        self.delegate = delegate
    def isBusy(self):
        return self.delegate.isBusy()
    def rawAsynchronousMoveTo(self,new_position):
        if int(new_position) == 1:
            self.delegate.asynchronousMoveTo("Open")
        else:
            self.delegate.asynchronousMoveTo("Close")
    def rawGetPosition(self):
        pos = self.delegate.getPosition()
        if pos == "Open":
            return 1 
        return 0

def make_tomoScanDevice(tomography_theta, tomography_shutter, tomography_translation, 
                        tomography_imageIndex):
    tomoScanDevice = ScannableGroup()
    tomoScanDevice.addGroupMember(tomography_theta)
    tomoScanDevice.addGroupMember(EnumPositionerDelegateScannable("tomography_shutter", tomography_shutter))
    tomoScanDevice.addGroupMember(tomography_translation)
    tomoScanDevice.addGroupMember(tomography_imageIndex)
    tomoScanDevice.setName("tomoScanDevice")
    tomoScanDevice.configure()
    return tomoScanDevice


class   tomoScan_positions(ScanPositionProvider):
    def __init__(self, step, darkFieldInterval, flatFieldInterval,
             inBeamPosition, outOfBeamPosition, points):
        self.step = step
        self.darkFieldInterval = darkFieldInterval
        self.flatFieldInterval = flatFieldInterval
        self.inBeamPosition = inBeamPosition
        self.outOfBeamPosition = outOfBeamPosition
        self.points = points

    def get(self, index):
        return self.points[index]
    
    def size(self):
        return len(self.points)
    
    def __str__(self):
        return "Step: %f Darks every:%d Flats every:%d InBeamPosition:%f OutOfBeamPosition:%f numImages %d" % \
            ( self.step,self.darkFieldInterval,self.flatFieldInterval, self.inBeamPosition, self.outOfBeamPosition, self.size() ) 
    def toString(self):
        return self.__str__()

from gda.device.scannable import SimpleScannable

"""
perform a simple tomogrpahy scan
"""
def tomoScan(step, darkFieldInterval, flatFieldInterval,
             inBeamPosition, outOfBeamPosition, exposureTime):
    try:
        darkFieldInterval=int(darkFieldInterval)
        flatFieldInterval=int(flatFieldInterval)
        
        start=0.
        stop=180.
        jns=beamline_parameters.JythonNameSpaceMapping()
        tomography_theta=jns.tomography_theta
        if tomography_theta is None:
            raise "tomography_theta is not defined in Jython namespace"
        tomography_shutter=jns.tomography_shutter
        if tomography_shutter is None:
            raise "tomography_shutter is not defined in Jython namespace"
        tomography_translation=jns.tomography_translation
        if tomography_translation is None:
            raise "tomography_translation is not defined in Jython namespace"
        
        tomography_detector=jns.tomography_detector
        if tomography_detector is None:
            raise "tomography_detector is not defined in Jython namespace"
        
        index=SimpleScannable()
        index.setCurrentPosition(0.0)
        index.setInputNames(["imageNumber"])
        index.setName("imageNumber")
        index.configure()
        
        tomoScanDevice = make_tomoScanDevice(tomography_theta, tomography_shutter, 
                                             tomography_translation, index)
        #generate list of positions
        numberSteps = ScannableUtils.getNumberSteps(tomography_theta, start, stop, step)
        theta_points = []
        theta_points.append(start)
        previousPoint = start
        for i in range(numberSteps):
            nextPoint = ScannableUtils.calculateNextPoint(previousPoint, step);
            theta_points.append(nextPoint)
            previousPoint = nextPoint
        
        scan_points = []
        theta_pos = theta_points[0]
        index=0
        scan_points.append((theta_pos, 0, inBeamPosition, index )) #dark
        index = index + 1        
        scan_points.append((theta_pos, 1, outOfBeamPosition, index )) #flat
        index = index + 1        
        scan_points.append((theta_pos, 1, inBeamPosition, index )) #first
        index = index + 1        
        imageSinceDark=0
        imageSinceFlat=0
        for i in range(numberSteps):
            theta_pos = theta_points[i+1]
            scan_points.append((theta_pos, 1, inBeamPosition, index ))#main image
            index = index + 1        
            
            
            imageSinceFlat = imageSinceFlat + 1
            if imageSinceFlat == flatFieldInterval and flatFieldInterval != 0:
                scan_points.append((theta_pos, 1, outOfBeamPosition, index ))
                index = index + 1        
                imageSinceFlat=0
            
            imageSinceDark = imageSinceDark + 1
            if imageSinceDark == darkFieldInterval and darkFieldInterval != 0:
                scan_points.append((theta_pos, 0, inBeamPosition, index ))
                index = index + 1        
                imageSinceDark=0
                
        #add dark and flat only if not done in last steps
        if imageSinceFlat != 0:
            scan_points.append((theta_pos, 1, outOfBeamPosition, index )) #flat
            index = index + 1
        if imageSinceDark != 0:
            scan_points.append((theta_pos, 0, inBeamPosition, index )) #dark
            index = index + 1        
                
        positionProvider = tomoScan_positions( step, darkFieldInterval, flatFieldInterval, \
                                               inBeamPosition, outOfBeamPosition, scan_points ) 
        scan_args = [tomoScanDevice, positionProvider, tomography_detector, exposureTime  ]
        scanObject=createConcurrentScan(scan_args)
        scanObject.runScan()
        return scanObject;
    except :
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "Error in tomoScan", exceptionType, exception, traceback, False)

def test1_tomoScan():
    jns=beamline_parameters.JythonNameSpaceMapping()    
    sc=tomoScan(step=5, darkFieldInterval=5, flatFieldInterval=5,
             inBeamPosition=0., outOfBeamPosition=10., exposureTime=1.)
    lsdp=jns.lastScanDataPoint()
    positions=lsdp.getPositionsAsDoubles()
    if positions[0] != 180. or positions[3] != 54.:
        print "Error - points are not correct :" + `positions`
    return sc

def test2_tomoScan():
    jns=beamline_parameters.JythonNameSpaceMapping()    
    sc=tomoScan(step=5, darkFieldInterval=5, flatFieldInterval=0,
             inBeamPosition=0., outOfBeamPosition=10., exposureTime=1.)
    lsdp=jns.lastScanDataPoint()
    positions=lsdp.getPositionsAsDoubles()
    if positions[0] != 180. or positions[3] != 47.:
        print "Error - points are not correct :" + `positions`
    return sc

def test3_tomoScan():
    jns=beamline_parameters.JythonNameSpaceMapping()    
    sc=tomoScan(step=5, darkFieldInterval=0, flatFieldInterval=5,
             inBeamPosition=0., outOfBeamPosition=10., exposureTime=1.)
    lsdp=jns.lastScanDataPoint()
    positions=lsdp.getPositionsAsDoubles()
    if positions[0] != 180. or positions[3] != 47.:
        print "Error - points are not correct :" + `positions`
    return sc

def test4_tomoScan():
    jns=beamline_parameters.JythonNameSpaceMapping()    
    sc=tomoScan(step=5, darkFieldInterval=0, flatFieldInterval=0,
             inBeamPosition=0., outOfBeamPosition=10., exposureTime=1.)
    lsdp=jns.lastScanDataPoint()
    positions=lsdp.getPositionsAsDoubles()
    if positions[0] != 180. or positions[3] != 40.:
        print "Error - points are not correct :" + `positions`
    return sc

def standardtomoScan():
    jns=beamline_parameters.JythonNameSpaceMapping()    
    sc=tomoScan(step=1, darkFieldInterval=0, flatFieldInterval=20,
             inBeamPosition=0., outOfBeamPosition=10., exposureTime=1.)
    lsdp=jns.lastScanDataPoint()
    positions=lsdp.getPositionsAsDoubles()
    if positions[0] != 180. or positions[3] != 40.:
        print "Error - points are not correct :" + `positions`
    return sc