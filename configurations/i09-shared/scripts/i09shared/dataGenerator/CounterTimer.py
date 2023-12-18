'''
Created on 14 May 2018

@author: fy65
'''
from gda.device.detector.countertimer import DummyCounterTimer
countTimer=DummyCounterTimer()
countTimer.setName("countTimer")
#countTimer.setTotalChans(1) #default is 8 channels
countTimer.setUseGaussian(True)
countTimer.setTimeChannelRequired(False)