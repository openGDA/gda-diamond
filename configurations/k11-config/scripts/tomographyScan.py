from gdaserver import *
from localStation import *
import time

#print('hello there from the script')

#print(beam_x)
#print(beam_y)
#mscan(path=grid((beam_x, beam_y), (1,1), (0,0), (10,4)), dev=('mandelbrot'))

class MissingParameter(Exception):
    pass
    
class TomographySlave:      

    def __init__(self, configuration, task):
        self.configuration = configuration
        self.task = task

    def _getImageCalibration(self):
        if (not tomoConfig.has_key('imageCalibration')):
            raise MissingParameter()
        return tomoConfig['imageCalibration']

    def _getProjections(self):
        if (not tomoConfig.has_key('projections')):
            raise MissingParameter()
        return tomoConfig['projections']
    
    def _getMultipleScans(self):
        if (not tomoConfig.has_key('multipleScans')):
            raise MissingParameter()
        return tomoConfig['multipleScans']
    
    def _takeDarkImage(self):
        imageCalibration = self._getImageCalibration()
        print 'takeDarkImage'
    
    def _takeFlatImage(self):
        imageCalibration = self._getImageCalibration()
        print 'takeFlatImage'
    


    def _acquireDarkAndFlat(self, imageCalibration): 
        for index in range(0, imageCalibration['numberDark']):
            self._takeDarkImage()
        for index in range(0, imageCalibration['numberFlat']):
            self._takeFlatImage()
    
    def _acquire(self):
        print 'acquire'
        mscan(beam_x, beam_y, rect, 0, 0, 10, 10, rast, 1, 1, mandelbrot)

    def _doAcquisition(self):
        projections = self._getProjections()
        imageCalibration = self._getImageCalibration()      
        if (imageCalibration['beforeAcquisition']):
            self._acquireDarkAndFlat(imageCalibration)                

        self._acquire()
        
        if (imageCalibration['afterAcquisition']):
            self._acquireDarkAndFlat(imageCalibration)

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
slave = TomographySlave(tomoConfig, task)
slave.doTask()            