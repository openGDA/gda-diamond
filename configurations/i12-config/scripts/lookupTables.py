'''
Created on 11 May 2012

@author: rsr31645
'''
import sys
from gda.factory import Finder

def reloadModuleLookup():
    moduleLookupTable =Finder.getInstance().find("moduleMotorPositionLUT")
    moduleLookupTable.reload()
    
def reloadCameraMotionLookup():
    cameraMotionLookup =Finder.getInstance().find("cameraMotionLUT")
    cameraMotionLookup.reload()
    
def reloadTiltBallPosition():
    tiltBallPositionLookup= Finder.getInstance().find("tiltBallRoiLut")
    tiltBallPositionLookup.reload()