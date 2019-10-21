'''
A wrapper detector that ensures a given motor is moving while detector is exposing

Created on 2 Aug 2019

@author: fy65
'''
from gda.device.detector import NXDetector
import math
from gda.device import DeviceException

class NXDetectorWithRockingMotion(NXDetector):
    '''
    A wrapper detector that ensures a given motor is moving while detector is exposing
    '''


    def __init__(self, name, motor, detector):
        '''
        Constructor
        @param name: name of this detector
        @param motor: the motor to be moving during detector collection
        @param detector: the detector to collect data from   
        '''
        self.setName(name)
        self.motor=motor
        if not isinstance(detector, NXDetector):
            raise Exception("The input detector is not NXDetector!")
        self.detector=detector
        self.start_motor_angle,self.end_motor_angle = 0.0, 0.0
        self.rockingCentre=0.0
        self.changeSpeed=False
        
    def setRockingCentre(self, value):
        self.rockingCentre=value
    
    def getRockingCentre(self):
        return self.rockingCentre
    
    def setChangeSpeed(self, b):
        self.changeSpeed=b
        
    def isChangeSpeed(self):
        return self.changeSpeed
        
    def calculateStartStopPosition(self,changeSpeed):
        if not changeSpeed:
            motor_range = self.motor.getSpeed()*self.detector.getCollectionTime()
            
            if motor_range > (self.motor.getUpperMotorLimit()-self.motor.getLowerMotorLimit()):
                raise Exception("motor rocking range is greater than hardware limits permitted")
            
            start_motor_angle=self.rockingCentre-motor_range/2.0
            end_motor_angle=self.rockingCentre+motor_range/2.0
            
            if start_motor_angle < self.motor.getLowerMotorLimit():
                raise Exception("start rocking angle is outside hardware low limit")
            if end_motor_angle > self.motor.getUpperMotorLimit():
                raise Exception("end rocking angle is outside hardware high limit")
        else:
            # there is minimum exposure time implied here
            motorspeed=(self.motor.getUpperMotorLimit() - self.motor.getLowerMotorLimit())/self.detector.getCollectionTime()
            if motorspeed < 0.0 or motorspeed > 1.388889 :
                raise DeviceException("motor speed %f calculated is outside allowed range [0.0, 1.388889]" % motorspeed)
            self.motor.setSpeed(motorspeed)
            start_motor_angle = self.motor.getLowerMotorLimit()
            end_motor_angle = self.motor.getUpperMotorLimit()
        return start_motor_angle, end_motor_angle

    def atScanStart(self):
        self.start_motor_angle,self.end_motor_angle = self.calculateStartStopPosition(self.changeSpeed)
        print("move theta to start position %f at Scan Start ..." % self.start_motor_angle)
        self.motor.moveTo(self.start_motor_angle)
        self.detector.atScanStart()
        self.point_count=1
        
    def collectData(self):
#         print("Acquiring image %d" % self.point_count)
        if self.motor.isBusy():
            self.motor.waitWhileBusy()
        curpos = float(self.motor.getPosition())
        if math.fabs(curpos - self.start_motor_angle) < math.fabs(curpos - self.end_motor_angle): 
            print("move theta to end position %f while collecting image number %d ..." % (self.end_motor_angle, self.point_count))
            self.motor.asynchronousMoveTo(self.end_motor_angle)
        else:
            print("move theta to start position %f while collecting image number %d ..." % (self.start_motor_angle, self.point_count))
            self.motor.asynchronousMoveTo(self.start_motor_angle)
        self.detector.collectData()
        self.point_count=self.point_count+1
    
    def readout(self):
        self.motor.stop()
        return self.detector.readout()    

    def stop(self):
        self.detector.stop()
        self.motor.stop()
        
    def setCollectionTime(self,time):
        self.detector.setCollectionTime(time)
        
    def getCollectionTime(self):
        return self.detector.getCollectionTime()
        
    def atCommandFailure(self):
        self.detector.atCommandFailure()
        self.motor.stop()
        
    def afterPropertiesSet(self):
        self.detector.afterPropertiesSet()
        
    def setCollectionStrategy(self,collectionStrategy):
        self.detector.setCollectionStrategy(collectionStrategy)
        
    def setAdditionalPluginList(self,additionalPluginList):
        self.detector.setAdditionalPluginList(additionalPluginList)
        
    def getCollectionStrategy(self):
        return self.detector.getCollectionStrategy()
    
    def getAdditionalPluginList(self):
        return self.detector.getAdditionalPluginList()
    
    def getPluginList(self):
        return self.detector.getPluginList()
    
    def getPluginMap(self):
        return self.detector.getPluginMap()
    
    def __str__(self):
        return self.detector.__str__()
    
    def setInputNames(self, names):
        self.detector.setInputNames(names)
        
    def setExtraNames(self,names):
        self.detector.setExtraNames(names)
        
    def setOutputFormat(self, names):
        self.detector.setOutputFormat(names)
        
    def asynchronousMoveTo(self, collectionTime):
        self.detector.asynchronousMoveTo(collectionTime)
        
    def isBusy(self):
        return self.detector.isBusy()
    
    def getPosition(self):
        return self.detector.getPosition()
    
    def prepareForCollection(self):
        self.detector.prepareForCollection()
        
    def createsOwnFiles(self):
        return self.detector.createsOwnFiles()
    
    def getInputNames(self):
        return self.detector.getInputNames()
    
    def getExtraNames(self):
        return self.detector.getExtraNames()
    
    def getOutputFormat(self):
        return self.detector.getOutputFormat()
    
    def atScanLineStart(self):
        self.detector.atScanLineStart()
        
    def getStatus(self):
        return self.detector.getStatus()
    
    def waitWhileBusy(self):
        self.detector.waitWhileBusy()
        
    def getPositionCallable(self):
        return self.detector.getPositionCallable()
    
    def atScanLineEnd(self):
        self.detector.atScanLineEnd()
        
    def atScanEnd(self):
        self.detector.atScanEnd()
        