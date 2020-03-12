#from gdaserver import theta
from gdaserver import *
from localStation import *
import time
#from gdascripts.mscanHandler import *

#import importlib
#motor_name = 'theta'
#motor = importlib.import_module('gdaserver.%s' % motor_name)
#print motor

#mscan(motor, 'points', 0,10, 'step', 0.1)
#print('hello there from the script')

#print(beam_x)
#print(beam_y)
#mscan(path=grid((beam_x, beam_y), (1,1), (0,0), (10,4)), dev=('mandelbrot'))

#print locals()['simx']

#def testMscan(motor):
#    malc = getRunnableDeviceService().getRunnableDevice("ws157-ML-SCAN-01")
    #malc.model.getExposureTime()
    #dir(malc)
#    print "MY MOTOR"
#    print motor
#    print malc
#    mscan motor axis 0 10 step 0.2 malc
    #mscan motor axis 0 10 step 0.2
    #pos stagex 20
    #mymotor = locals()['theta']
    #mscan mymotor 'axis'
    
#testMscan(locals()['simx'])

class MissingParameter(Exception):
    def __init__(self, parameter, msg=None):
        if msg is None:
            # Set some default useful error message
            self.msg = "Missing parameter %s" % parameter
        else:
            self.msg = msg
        self.parameter = parameter
        print self.msg

# Better would be to have a class to deserialize the message but for now this looks more handy
class TomographyJSON:    
    START_OBJ = 'start'
    START_ANGLE = 'start'      
    
    END_OBJ = 'end'
    RANGE_TYPE = 'rangeType'
    RANGE_180 = 'RANGE_180'
    RANGE_360 = 'RANGE_360'
    RANGE_CUSTOM = 'RANGE_CUSTOM'
    CUSTOM_ANGLE = 'customAngle'
    
    
    IMAGE_CALIBRATION = 'imageCalibration'
    DARK_EXPOSURE = 'darkExposure'
    FLAT_EXPOSURE = 'flatExposure'
    
    PROJECTIONS = 'projections'
    TOTAL_PROJECTIONS = 'totalProjections'
    ANGULAR_STEP = 'angularStep'
    
    MULTIPLE_SCANS = 'multipleScans'

    EXPOSURE = 'EXPOSURE'

    STAGE_ROT_Y = 'MOTOR_STAGE_ROT_Y'
    
    MODE = 'stageDescription'
    MOTORS = 'motors'
    METADATA = 'metadata'
    MALCOLM_TOMO = 'MALCOLM_TOMO'
    
    MOTOR_POSITIONS = 'motorsPositions'
    START = 'START'
    OUT_OF_BEAM = 'OUT_OF_BEAM'
    
    
class TomographySlave:      

    def __init__(self, configuration, mode, motorPositions, task, env):
        if (configuration is None):
            raise MissingParameter()
        self.configuration = configuration.get('acquisitionParameters', {})
        self.mode = mode
        self.motorPositions = motorPositions
        self.task = task
        self.env = env
        self._malcolmTomographyDevice = None

    def _getObjectParameter(self, object, parameterName):
        if (not object.has_key(parameterName)):
            raise MissingParameter(parameterName)
        return object.get(parameterName)

    def _getImageCalibration(self):
        return self._getObjectParameter(self.configuration, TomographyJSON.IMAGE_CALIBRATION)

    def _getProjections(self):
        return self._getObjectParameter(self.configuration, TomographyJSON.PROJECTIONS)
    
    def _getMultipleScans(self):
        return self._getObjectParameter(self.configuration, TomographyJSON.MULTIPLE_SCANS)
    
    def _getStartObject(self):
        return self._getObjectParameter(self.configuration, TomographyJSON.START_OBJ)
    
    def _getEndObject(self):
        return self._getObjectParameter(self.configuration, TomographyJSON.END_OBJ)    
    
    def _getMotors(self):
        return self._getObjectParameter(self.mode, TomographyJSON.MOTORS)
    
    def _getModeMetadata(self):
        return self._getObjectParameter(self.mode, TomographyJSON.METADATA)
    
    def _closeShutter(self):
        print 'closeShutter'
    
    def _openShutter(self):
        print 'openShutter'
    
    def _movesToPosition(self, definedPosition):
        oobPositions = self._getObjectParameter(self.motorPositions, definedPosition)
        for position in oobPositions:
            self._moveMotor(position.get('name'), position.get('value'))
        
    def _moveMotor(self, name, value):        
        motor = self._getMotorInstance(name);
        if (motor is not None):
            pos motor value
    
    def _getMotorInstance(self, name):
        if (self._getMotors().has_key(name)):
            return self.env[self._getMotors().get(name).get('name', None)]
    
    def _takeDarkImage(self):
        imageCalibration = self._getImageCalibration()
        numImages = imageCalibration.get('numberDark',0)
        if (numImages > 0):
            self._closeShutter()
            malc = self._getMalcolmTomographyDevice()
            self._setMalcolmTomographyDeviceExposure(malc, imageCalibration.get(TomographyJSON.DARK_EXPOSURE, 0))
            print "DARK exposure " + str(malc.model.getExposureTime())
        for index in range(0, numImages):
            print 'takeDarkImage'
        self._openShutter()
        
    
    def _takeFlatImage(self):
        imageCalibration = self._getImageCalibration()
        numImages = imageCalibration.get('numberFlat',0)
        if (numImages > 0):
            print 'Goes out of beam'
            self._movesToPosition(TomographyJSON.OUT_OF_BEAM)
            malc = self._getMalcolmTomographyDevice()
            self._setMalcolmTomographyDeviceExposure(malc, imageCalibration.get(TomographyJSON.FLAT_EXPOSURE, 0))
            print "FLAT exposure " + str(malc.model.getExposureTime())
        for index in range(0, numImages):
            print 'takeFlatImage'
        if (numImages > 0):      
            print 'Restores start position'      
            self._movesToPosition(TomographyJSON.START)

    def _getMalcolmTomographyDeviceName(self):
        return self._getModeMetadata().get(TomographyJSON.MALCOLM_TOMO, None)

    def _acquireDarkAndFlat(self):
        self._takeDarkImage()
        self._takeFlatImage()
    
    def _getMalcolmTomographyDevice(self):
        if (self._malcolmTomographyDevice is None):
            self._malcolmTomographyDevice = getRunnableDeviceService().getRunnableDevice(self._getMalcolmTomographyDeviceName())
        return self._malcolmTomographyDevice
    
    def _setMalcolmTomographyDeviceExposure(self, malc, exposureTime):
        malc.model.setExposureTime(exposureTime)

    def _getEndAngle(self, range):
        if (range == TomographyJSON.RANGE_180):
            return 180.0
        if (range == TomographyJSON.RANGE_360):
            return 360.0
        return self._getEndObject().get(TomographyJSON.CUSTOM_ANGLE)         
    
    def _getCameraExposure(self):
        return float(self._getModeMetadata().get(TomographyJSON.EXPOSURE, 100))
    
    def _acquire(self):
        rotStage = self._getMotorInstance(TomographyJSON.STAGE_ROT_Y)
        malc = self._getMalcolmTomographyDevice()
        exposureTime = self._getCameraExposure() # exposure is in seconds while UI return in milliseconds
        #self._setMalcolmTomographyDeviceExposure(malc, exposureTime)
        start_angle = self._getStartObject().get(TomographyJSON.START_ANGLE)
        end_angle = self._getEndAngle(self._getEndObject().get(TomographyJSON.RANGE_TYPE))
        angularStep = self._getProjections().get(TomographyJSON.ANGULAR_STEP)
        mscan rotStage axis start_angle end_angle step angularStep malc exposureTime
        
        #totalProjections = self._getProjections().get(TomographyJSON.TOTAL_PROJECTIONS)
        #mscan rotStage axis start_angle end_angle points totalProjections malc exposureTime
        

    def _doAcquisition(self):     
        if (self._getImageCalibration().get('beforeAcquisition', False)):
            self._acquireDarkAndFlat()                

        self._acquire()
        
        if (self._getImageCalibration().get('afterAcquisition', False)):
            self._acquireDarkAndFlat()

    def _doAcquisitions(self):
        print 'startAcquisitions'
        multipleScans = self._getMultipleScans()
        isSwitchback = False
        sleepTime = 0
        if (multipleScans['numberRepetitions'] > 0):
            sleepTime = multipleScans['numberRepetitions']/1000.
        if multipleScans['numberRepetitions'] == 'SWITCHBACK_SCAN':
            isSwitchback = True          

        #Dummy code until switchback is clear how do switchback
        if isSwitchback:
            print 'startAcquisition in switchback mode'
        else:
            print 'startAcquisition in repetition mode'
        
        for index in range(0, multipleScans['numberRepetitions']):
            print 'startAcquisition n. ' + str(index)
            self._doAcquisition()
            time.sleep(sleepTime)
            print 'endAcquisition n. ' + str(index)
            
    def doTask(self):
        if self.task == 'sayHello':
            print 'Hello!'
            return
        if self.task == 'doAcquisition':
            return self._doAcquisitions()
        if self.task == 'doFlat':
            return self._takeFlatImage()        
        if self.task == 'doDark':
            return self._takeDarkImage()            


import json            
#{u'projections': {u'totalProjections': 1, u'anglarStep': 0.0}, u'start': {u'start': 0.0, u'useCurrentAngle': False, u'currentAngle': 4.9e-324}, u'multipleScans': {u'numberRepetitions': 1, u'waitingTime': 0, u'multipleScansType': u'REPEATE_SCAN'}, u'imageCalibration': {u'numberDark': 0, u'afterAcquisition': False, u'beforeAcquisition': False, u'numberFlat': 0}, u'name': u'Hello there!', u'end': {u'customAngle': 0.0, u'numberRotation': 1, u'rangeType': u'RANGE_180'}, u'scanType': u'FLY'}
tomoConfig = {}
if 'tomographyServiceMessage' in locals():
    tomoConfig = json.loads(locals()['tomographyServiceMessage'])
else:
    print('no tomoConfig')

task = 'sayHello'
if 'cmd' in locals():
    task = locals()['cmd']
else:
    print('noTask')    

print 'task: ' + task
print tomoConfig
slave = TomographySlave(tomoConfig['acquisition']['acquisitionConfiguration'], tomoConfig[TomographyJSON.MODE], tomoConfig[TomographyJSON.MOTOR_POSITIONS], task, locals())
slave.doTask()            