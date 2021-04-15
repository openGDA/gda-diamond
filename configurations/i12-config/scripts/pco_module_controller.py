# written by Robert Atwood
# modified to use GDA object in the embedded jython engine.
# $Id:$
### required libraries and modules
import math
from gda.device.scannable import ScannableMotionBase
import sys
from gda.factory import Finder

#store the safe excange position
cameraSafeZ = -10.0

#the correct tomography sample tilt alignment
sampleTiltX = 0.054157
sampleTiltZ = 0.0

#table of positions for each module for each motor
#cam1x=(248.0,164.0,85.0,9.815)
#cam1roll=(-0.89281,-0.4213,-0.1787,-0.5614)
#cam1z=(-91.3,-70.9,-50.5,-43.6565)
class CameraMag(ScannableMotionBase):
    def __init__(self, name, rootNameSpace={}):
        '''Constructor - Only succeed if it find the lookup table, otherwise raise exception.'''
        self.rootNameSpace = rootNameSpace
        self._busy = 0
        self.setName(name)
        self.setLevel(5)
        self.inputNames = ['module']
        self.module = 1
        self.lut = Finder.find("moduleMotorPositionLUT")

    def rawGetPosition(self):
        '''returns the positions of all child scannables.
           If a child scannable can not be reached for whatever reason, it just prints out a message, then continue to next.'''
        positions = []
        try:
            positions.append(self.module)
            positions.append(self.rootNameSpace['ss1_rx'].getPosition())
            positions.append(self.rootNameSpace['ss1_rz'].getPosition())
            positions.append(self.rootNameSpace['cam1_x'].getPosition())
            positions.append(self.rootNameSpace['cam1_z'].getPosition())
            positions.append(self.rootNameSpace['cam1_roll'].getPosition())
            return positions
        except:
            print "Error returning position", sys.exc_info()[0]
            raise

    def rawAsynchronousMoveTo(self, new_position):
        '''move every scannables to their corresponding values for this energy.
           If a child scannable can not be reached for whatever reason, it just prints out a message, then continue to next.'''
        new_position = float(new_position)
        self.module = new_position
        self.cameraMag(new_position, self.rootNameSpace)

                
    def isBusy(self):
        '''checks the busy status of all child scannable.
           If and only if all child scannable are done this will be set to False.'''  
        return (self.rootNameSpace['ss1_rx'].isBusy()) or self.rootNameSpace['ss1_rz'].isBusy() or self.rootNameSpace['cam1_x'].isBusy() or self.rootNameSpace['cam1_z'].isBusy() or self.rootNameSpace['cam1_roll'].isBusy()
    
    def getExtraNames(self):
        extraNames = []
        extraNames.append('ss1_rx')
        extraNames.append('ss1_rz')
        extraNames.append('cam1_x')
        extraNames.append('cam1_z')
        extraNames.append('cam1_roll')
        return extraNames


    def toString(self):
        '''formats what to print to the terminal console.'''
        return self.name + " : " + str(self.getPosition())

    def cameraMag(self, module, rootNameSpace={}):
        
        global sampleTiltX
        global sampleTiltZ
        global cameraSafeZ
        global cam1x
        global cam1roll
        global cam1z

        print "camera optical module switching\n"
        print "ss1_rx" , rootNameSpace['ss1_rx'], "\n"
        print "ss1_rz" , rootNameSpace['ss1_rz'], "\n"
        print "cam1_x" , rootNameSpace['cam1_x'], "\n"
        print "cam1_z" , rootNameSpace['cam1_z'], "\n"
        print "cam1_roll" , rootNameSpace['cam1_roll'], "\n" 
        #create a zero-based array index
        #self.execThread = thread.start_new_thread(self.execOperation, (module, rootNameSpace))
        rootNameSpace['ss1_rx'].asynchronousMoveTo(sampleTiltX)
        rootNameSpace['ss1_rz'].asynchronousMoveTo(sampleTiltZ)

        print "Moved ss1 motors %s, %s " % (rootNameSpace['ss1_rx'], rootNameSpace['ss1_rz']) 
        modnum = int(module);
        print modnum
        
        #check whether the camera is ALREADY in the required module
        #thisx=float(rootNameSpace['cam1_x'].getPosition())
        thisx = rootNameSpace['cam1_x'].getPosition()
        cam1x = self.lut.lookupValue(modnum, "cam1.x")
        cam1z = self.lut.lookupValue(modnum, "cam1.z")
        cam1Roll = self.lut.lookupValue(modnum, "cam1.roll")
        t3x = self.lut.lookupValue(modnum, "t3.x")
        t3m1y = self.lut.lookupValue(modnum, "t3.m1y")
        print thisx, modnum, cam1x
        
        print "Cam1xMoveToPosition:%s  cam1ZMoveToPosition:%s  cam1RollMoveToPosition:%s" % (cam1x, cam1z, cam1Roll)
        offset = (math.fabs(thisx - cam1x))
        print ("offset is %f", offset)
        if (offset < 0.1):
            print ("already in module %d", module)

        if (offset >= 0.1):
            #put camera in the safe position
            rootNameSpace['cam1_z'].moveTo(cameraSafeZ)
            #put lens translation in the position  for this module
            rootNameSpace['cam1_x'].moveTo(cam1x)
            #put camera in the focussed position
            rootNameSpace['cam1_z'].moveTo(cam1z)

        #set the camera roll for this module
        #even if we're already in this module
        rootNameSpace['cam1_roll'].moveTo(cam1Roll)
        print("adjusting the camera position")
        rootNameSpace['t3_x'].moveTo(t3x)
        rootNameSpace['t3_m1y'].moveTo(t3m1y)
                               

        print "camera optical module switching finished"
        return "OK"
    
    #def execOperation(self, module, rootNameSpace={}):
        #ensure the sample stage is in the tomography alignment
        

