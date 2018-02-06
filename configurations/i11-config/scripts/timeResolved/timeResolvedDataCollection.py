'''
This module designed to support time resolved experiments using X-ray and laser source. The acquisition strategty is configured
 through TFG2, and diffraction data are collected using PSD detector.
 
 Usages: 
    1. users must 1st provide the following configuration parameters before run this script
        startDelayTime=0.0
        stopDelayTime=1.0
        stepDelayTime=0.01
        numberofframes=1
        numberofgates=100
        gatetime=0.00001
        writerTime=2.0
    2. Data file are named as "scanNumber-mythen-collectionNumber.dat". 
    each collection number is corresponding to a specific time delay
 
Created on 10 Jun 2015

@author: fy65
'''
from gda.data import NumTracker
from gdascripts.utils import frange
scanNumTracker = NumTracker("i11");
scanNumber=scanNumTracker.incrementNumber()

startDelayTime=0.0
stopDelayTime=1.0
stepDelayTime=0.01

numberofframes=1
numberofgates=100
gatetime=0.00001
writerTime=2.0

def doCollection(numberofframes, numberofgates, gatetime, delaybefore, writerTime, collectionNumber, detector=mythen, tfg=tfg2):  # @UndefinedVariable
    tfg.configure4TimeResolvedExperiment(gatetime, numberofgates, numberofframes, delaybefore, writerTime)
    detector.gated(numberofframes, numberofgates, scanNumber, collectionNumber)
    tfg.start()
    
collectionNumber=0
for delayTime in frange(startDelayTime, stopDelayTime, stepDelayTime):
    doCollection(numberofframes, numberofgates, gatetime, delayTime, writerTime, collectionNumber)
    collectionNumber++