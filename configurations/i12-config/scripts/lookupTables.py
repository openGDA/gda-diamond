'''
Created on 11 May 2012

@author: rsr31645
'''
import sys
from gda.factory import Finder

def reloadModuleLookup():
    moduleLookupTable =Finder.find("moduleMotorPositionLUT")
    moduleLookupTable.reload()
    
def reloadCameraMotionLookup():
    cameraMotionLookup =Finder.find("cameraMotionLUT")
    cameraMotionLookup.reload()
    
def reloadTiltBallPositionLookup():
    tiltBallPositionLookup= Finder.find("tiltBallRoiLut")
    tiltBallPositionLookup.reload()
    
def reloadScanResolutionLookup():
    tiltBallPositionLookup= Finder.find("scanResolutionLut")
    tiltBallPositionLookup.reload()
    