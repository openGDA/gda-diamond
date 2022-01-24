from gda.device import Detector
from gda.device.detector import DetectorBase

import sys, time, math, random;


class DummyDetectorClass(DetectorBase):
    '''SoftCounterClass - A dummy detector that can returns random counts'''
    DETECTOR_STATUS_IDLE, DETECTOR_STATUS_BUSY, DETECTOR_STATUS_PAUSED, DETECTOR_STATUS_STANDBY, DETECTOR_STATUS_FAULT, DETECTOR_STATUS_MONITORING = range(6);
    
    def __init__(self, name):
        self.setName(name);
#        self.setInputNames(['ExposureTime'])
        self.setOutputFormat(['%6.2f'])
        self.setLevel(7);
        self.exposureTime = 0.1;
        self.counts=0;

# Detector implementations
    def getCollectionTime(self):
        return self.exposureTime;

    def setCollectionTime(self, newExpos):
        self.exposureTime = newExpos;

    def collectData(self):
        self.counts = random.randint(1, 10000);
        time.sleep(self.exposureTime);
        return;

    def readout(self):
        return self.counts;

    def getStatus(self):
        return Detector.IDLE;
    
    def createsOwnFiles(self):
        return False;


class DummyDetectorRandomClass(DetectorBase):
    '''A dummy detector that can returns many channels of Gaussian output with random parameters'''
    DETECTOR_STATUS_IDLE, DETECTOR_STATUS_BUSY, DETECTOR_STATUS_PAUSED, DETECTOR_STATUS_STANDBY, DETECTOR_STATUS_FAULT, DETECTOR_STATUS_MONITORING = range(6);
    
    def __init__(self, name, numberOfChannels=32):
        self.setName(name);
        self.setLevel(7);
        self.exposureTime = 0.1;
        self.numberOfChannels=numberOfChannels;
        self.currentPosition = 0;
        self.scannableSetup();

    def scannableSetup(self):
        self.setInputNames([]);

        extraNames = ['ExposureTime'];
        outputFormat = ['%f'];

        for c in range(self.numberOfChannels):
            extraNames.append('ch_%s' %c )
            outputFormat.append( '%f' )

        self.setExtraNames(extraNames);
        self.setOutputFormat(outputFormat);
        
# Detector implementations
    def getCollectionTime(self):
        return self.exposureTime;

    def setCollectionTime(self, newExpos):
        self.exposureTime = newExpos;

    def collectData(self):
        time.sleep(self.exposureTime);
        self.currentPosition += 1;
        
        return;

    def getStatus(self):
        return Detector.IDLE;

    def readout(self):
        result = [self.exposureTime];
        for c in range(self.numberOfChannels):
            counts = random.randint(1, 10000);
            result.append( counts );
        return result;

    def createsOwnFiles(self):
        return False;
    

class DummyDetectorGausianClass(DummyDetectorRandomClass):
    '''A dummy detector that can returns many channels of Gaussian output with random parameters'''
    def __init__(self, name, numberOfChannels=32):
        
        DummyDetectorRandomClass.__init__(self, name, numberOfChannels);
 
        self.chCentre = [random.randint(1, 100 ) for c in range(self.numberOfChannels) ]
        self.chSigma  = [random.randint(1, 30)   for c in range(self.numberOfChannels) ]
        self.chHeight = [random.randint(1, 1000) for c in range(self.numberOfChannels) ]
        self.chNoise  = [random.randint(1, 10)  for c in range(self.numberOfChannels) ]
        self.chOffset = [random.randint(1, 30)  for c in range(self.numberOfChannels) ]
   
        
    def getGaussian(self, x, centre, sigma, height, offset, noise):
        pure_y=offset + math.exp( -(x-centre)**2/(2*sigma**2) ) * height;
        y = (pure_y )* ( 1+(random.random()-0.5)*noise )

        return y;

    def readout(self):
        result = [self.exposureTime];
        for c in range(self.numberOfChannels):
            counts = self.getGaussian(self.currentPosition, self.chCentre[c], self.chSigma[c], self.chHeight[c], self.chOffset[c], self.chNoise[c]);
            result.append( counts );
        return result;

d1=DummyDetectorClass("d1");
d2=DummyDetectorClass("d2");
d3=DummyDetectorRandomClass("d3");
d4=DummyDetectorGausianClass("d4");
