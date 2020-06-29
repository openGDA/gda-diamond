'''
Created on 4 Mar 2015

@author: fy65
'''
#from gda.factory import Finder
#das4etfg=Finder.find("daserverForTfg")

delayBeforeStart=0.0
#numberOfFramesBetweenValueTriggers=5
numberOfSpectrum=101

DELAY_BEFORE_DETECTOR_START="1 " + str(delayBeforeStart) + "0.0 0 0 0 0 \n"
DETECTOR_START             ="1 0.0001 0.0 2 0 0 0 \n"
#DETECTOR_FRAMES_SYNC       =str(numberOfFramesBetweenValueTriggers)+" 0 0.000001 0 0 0 9 \n"
TRIGGER_TO_VALVE1          ="1 0.0001 0.0 8 0 0 0 \n"
TRIGGER_TO_VALVE2          ="1 0.0001 0.0 4 0 0 0 \n"

GROUP_END="-1 0 0 0 0 0 0 \n"
GROUP_DEF="tfg setup-groups \n"

TFG2_CONFIG="tfg config 'etfg0' tfg2\n"

def collectNumberFramesFromDetector(numberOfFrames):
    return str(numberOfFrames)+" 0 0.000001 0 0 0 9 \n"

def getCommands4ExternalTFG():
    command =  GROUP_DEF
    command += DELAY_BEFORE_DETECTOR_START
    command += DETECTOR_START
    
    command += collectNumberFramesFromDetector(10)
    command += TRIGGER_TO_VALVE1
    command += collectNumberFramesFromDetector(1)
    command += TRIGGER_TO_VALVE1
    
    command += collectNumberFramesFromDetector(20)
    command += TRIGGER_TO_VALVE2
    command += collectNumberFramesFromDetector(1)
    command += TRIGGER_TO_VALVE2
    
    command += collectNumberFramesFromDetector(numberOfSpectrum-30)
    
    
    command += GROUP_END
    return command

#das4etfg.sendCommand(command)