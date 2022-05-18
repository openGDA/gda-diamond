'''
define functions and commands for acquiring image data only.

Created on May 6, 2022

@author: fy65
'''
from time import sleep
from gdascripts.utils import caput
from gdascripts.scan.installStandardScansWithProcessing import scan
from gdaserver import sgmpitch, fastshutter  # @UnresolvedImport
from shutters.detectorShutterControl import primary, polarimeter, erio
from gda.jython.commands.GeneralCommands import alias   
from gda.device.scannable import DummyScannable

ENABLE_ENCODER_LIGHT_CONTROL=False
# repeat acquire at a fixed point
def acquireImages(n, det, exposure_time, *args):
    '''acquire image data from detector which has build in control of encoder light, - default light control is False
    '''
    ds = DummyScannable("ds")
    try:
        newargs=[ds,1,n,1,det,exposure_time] # @UndefinedVariable
        for arg in args:
            newargs.append(arg)
        if ENABLE_ENCODER_LIGHT_CONTROL:
            # last recorded position of sgmpitch when the light was switched off
            ENCODER_POSITION_BEFORE_LIGHT_OFF=float(sgmpitch.getPosition())
            sleep(0.1)
            # kill sgmpitch
            caput("BL21I-OP-SGM-01:PITCH:KILL.PROC",1)
            sleep(0.1)
            # switch off encoder power
            caput("BL21I-OP-SGM-01:TVLR:ENC_POWER",1)
        scan([e for e in newargs])
    finally:
        if ENABLE_ENCODER_LIGHT_CONTROL:
            # switch on encoder power
            caput("BL21I-OP-SGM-01:TVLR:ENC_POWER",0)
            sleep(0.1)
            clearEncoderLoss()
            sleep(0.1)
            sgmpitch.moveTo(ENCODER_POSITION_BEFORE_LIGHT_OFF)
                

def clearEncoderLoss():
    '''clear encloder loss
    '''
    caput("BL21I-OP-SGM-01:PITCH:ELOSSRC.A", 0)
    sleep(2.0)
         
alias("clearEncoderLoss")
    
def acquireRIXS(n, det, exposure_time, *args):
    ''' collect RIXS data from detector
    '''
    if det is andor:  # @UndefinedVariable
        primary()
    elif det is andor2:  # @UndefinedVariable
        polarimeter()
    fastshutter("Open")
    acquireImages(n, det, exposure_time, *args)

alias("acquireRIXS")

def acquiredark(n, det, exposure_time, *args):
    '''collect dark image data without creating node link in subsequent scan data files.
    '''
    fastshutter("Closed")
    erio()
    acquireImages(n, det, exposure_time, *args)

alias("acquiredark")
