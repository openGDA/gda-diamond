'''
Created on 6 Dec 2017

@author: fy65
'''
from gda.device.zebra.controller.impl import ZebraImpl
from gda.device.detector.areadetector.v17.impl import ADBaseImpl
from detectors.ZebarDetectorCollectionStrategy import ZebraDetectorCollectionStrategy
from detectors.ZebraDetector import ZebraDetector

#Zebra Controller instance communicate with EPICS Zebra IOC
zebraController=ZebraImpl()
zebraController.setZebraPrefix("BL21I-EA-ZEBRA-01:")
#Zebra EPICS Area Detector wrapper
zebraADBase=ADBaseImpl()
zebraADBase.setBasePVName("BL21I-EA-ZEBRA-01:")
#Zebra capture waveforms writing to data file 
zebraCollectionStrategy=ZebraDetectorCollectionStrategy("zebraCollectionStrategy", zebraController, zebraADBase=zebraADBase)
#zebra as NXDetector in GDA
zebradetector=ZebraDetector("zebradetector",zebraController,zebraCollectionStrategy)
#Zebra configuration for PGM pitch vibration monitoring
zebradetector.configureSetup(["PC_ENC3", "PC_ENC4","PC_TIME"], "Enc1", "Positive", "ms")
zebradetector.configureGate("Time", 0.0, 20.0, 1, 20.001)
zebradetector.configurePulse("Time", 0.0, 0.001, 0.002, 0.0, 10000)
#to change captured waveform fields after configureSetup()
#zebradetector.setCaptureFields(["PC_ENC3", "PC_ENC4","PC_TIME"])