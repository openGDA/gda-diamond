'''
Created on 14 May 2018

@author: fy65
'''
from gda.util import Gaussian
from java.lang import Math
from org.slf4j import LoggerFactory


class WaveformDataGenerator(object):
    
    def __init__(self, pointCounter=0):
        self.logger = LoggerFactory.getLogger("WaveformDataGenerator" )
        self.channel=None
        self.useGaussian=False
        self.gaussian=None
        self.pointCounter=pointCounter
        self.incrementCounter=1
        self.dataDecimalPlaces=2
        self.roundingFactor = Math.pow(10.0, self.dataDecimalPlaces)
        self.gaussianPosition = 10.0
        self.gaussianWidth = 5.0
        self.gaussianHeight = 10.0
        self.noiseLevel=0.1
        self.data=[]
        
    def generateData(self, numofpoints):
        if self.useGaussian:
            baseValue=self.gaussian.yAtX(self.pointCounter)
            for i in range(numofpoints):
                self.data.append(self.round((baseValue + self.channel) * (1.0 + self.noiseLevel * (2.0 * Math.random() - 1.0))))
        else:
            for i in range(numofpoints):
                self.data.append(self.round(int(Math.random() * 10.0) * (self.pointCounter + 1)))
        return self.data
    
    def round(self, value):
        return Math.rint(value * self.roundingFactor) / self.roundingFactor
    
    def resetGaussian(self):
        '''In useGaussian mode what is actually produced is a set of Gaussians, the first
            centered on gaussianPosition, the next on gaussianPosition plus two times gaussianWidth
            and so on. Each gaussian is also higher than the previous.
        '''
        self.logger.debug("%%%%%%% pointCounter now " + self.pointCounter);
        if self.pointCounter == int(self.gaussianPosition) + 2 * int(self.gaussianWidth):
            self.gaussianPosition += 4.0 * self.gaussianWidth
            self.incrementCounter +=1
            self.gaussian = Gaussian(self.gaussianPosition, self.gaussianWidth, self.incrementCounter * self.gaussianHeight)
    
    def initializeGaussian(self):
        if self.useGaussian and self.gaussian == None:
            self.pointCounter=0
            self.incrementCounter=1
            self.gaussianPosition = 10.0
            self.gaussian=Gaussian(self.gaussianPosition, self.gaussianWidth, self.incrementCounter * self.gaussianHeight)
        