'''
Created on 16 Apr 2015

@author: fy65
'''
from gda.factory import Finder
from gda.device.lima.LimaCCD import AcqMode, AcqTriggerMode, AccTimeMode
from gda.device.frelon.Frelon import ImageMode, InputChannels, ROIMode, SPB2Config

edefrelon=Finder.find("frelon")
# object used to access real detector data in Tango
frelon1=edefrelon.getFrelon()
limaccd=edefrelon.getLimaCcd()

#object used to setup frelon detector for later data collection
detectorConfig=frelon1.getDetectorData()

#access to acq_mode
#limaccd.setAcqMode(AcqMode.SINGLE)
#limaccd.getAcqMode()