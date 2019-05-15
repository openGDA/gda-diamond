'''
A module defines a Scannable class for beam size. It contains definition of coefficients of linear relationship between 
beam size required, and the slit y-gap size and raster amplitude, respectively.

Once calibrated, these coefficients must be updated accordingly.
fixed I06-546
  
Created on 28 Nov 2018

@author: fy65
'''

from gda.epics import CAClient
from time import sleep
from gdaserver import s4ygap
from gda.device.scannable import ScannableMotionBase

#beamSize>10 gap=4.9302beamsize-19.767 R^2=0.9973, amp=0.0193beamsize+0.1523 R^2=0.9001
#beamSize<10 gap=3.75beamsize-12.5 R^2=1, amp=0.0125beamsize-0.025 R^2=1

GAP_SLOPE_4_BEAM_SIZE_GREAT_THAN_10=4.9302
GAP_OFFSET_4_BEAM_SIZE_GREAT_THAN_10=-19.767
AMPLITUDE_SLOPE_4_BEAM_SIZE_GREAT_THAN_10=0.0193
AMPLITUDE_OFFSET_4_BEAM_SIZE_GREAT_THAN_10=0.1523

GAP_SLOPE_4_BEAM_SIZE_LESS_THAN_10=3.75
GAP_OFFSET_4_BEAM_SIZE_LESS_THAN_10=-12.5
AMPLITUDE_SLOPE_4_BEAM_SIZE_LESS_THAN_10=0.0125
AMPLITUDE_OFFSET_4_BEAM_SIZE_LESS_THAN_10=0.025


RASTER_MODE=["Horizontal","Vertical"]

class BeamSize(ScannableMotionBase):
    '''
    A scannable to set beam size on the sample by defining s4 slit y-gap, raster amplitude, and raster mode.
    For beam size > 10 micron, raster mode should be "Horizontal", otherwise, "Vertical"
    It is assumed that there is a linear relationship between beam size and amplitude or slit aperture size.
    '''


    def __init__(self, name, pvroot, scannable):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(['%5.5f'])
        self.hampCh=CAClient(pvroot+":HFM:FPITCH:AMPL")
        self.vampCh=CAClient(pvroot+":VFM:FPITCH:AMPL")
        self.modeCh=CAClient(pvroot+":RASTER:MODE")
        self.scannable=scannable
        self.beamsize=None
        
    def setRasterMode(self, mode):
        if not mode in RASTER_MODE:
            raise Exception("Input String value is not supported!, Supported value must be one of "+str(RASTER_MODE))
        if not self.modeCh.isConfigured():
            self.modeCh.configure()
        self.modeCh.caput(mode)

    def setHorizontalRasterAmplitude(self, amp):
        if not self.hampCh.isConfigured():
            self.hampCh.configure()
        self.hampCh.caputWait(amp)
        
    def setVerticalRasterAmplitude(self, amp):
        if not self.vampCh.isConfigured():
            self.vampCh.configure()
        self.vampCh.caputWait(amp)       
    
    def atScanStart(self):
        if not self.modeCh.isConfigured():
            self.modeCh.configure()
        if not self.hampCh.isConfigured():
            self.hampCh.configure()
        if not self.vampCh.isConfigured():
            self.vampCh.configure()
    
    def atScanEnd(self):
        if self.modeCh.isConfigured():
            self.modeCh.clearup()
        if self.hampCh.isConfigured():
            self.hampCh.clearup()
        if self.vampCh.isConfigured():
            self.vampCh.clearup()
    
    def getPosition(self):
        return self.beamsize
    
    def asynchronousMoveTo(self, beamsize):
        try:
            if float(beamsize) > 10.0:
                self.setRasterMode("Horizontal")
                sleep(1)
                self.setHorizontalRasterAmplitude(AMPLITUDE_SLOPE_4_BEAM_SIZE_GREAT_THAN_10*beamsize+AMPLITUDE_OFFSET_4_BEAM_SIZE_GREAT_THAN_10)
                self.scannable.asynchronousMoveTo(GAP_SLOPE_4_BEAM_SIZE_GREAT_THAN_10*beamsize+GAP_OFFSET_4_BEAM_SIZE_GREAT_THAN_10)
            elif float(beamsize) <= 10.0:
                self.setRasterMode("Vertical")
                sleep(1)
                self.setHorizontalRasterAmplitude(AMPLITUDE_SLOPE_4_BEAM_SIZE_LESS_THAN_10*beamsize+AMPLITUDE_OFFSET_4_BEAM_SIZE_LESS_THAN_10)
                self.scannable.asynchronousMoveTo(GAP_SLOPE_4_BEAM_SIZE_LESS_THAN_10*beamsize+GAP_OFFSET_4_BEAM_SIZE_LESS_THAN_10)
            self.beamsize=beamsize
            print "-> beam size set to %f micron" % (beamsize)
        except Exception, e:
            raise e
    
    def isBusy(self):
        return self.scannable.isBusy()
    
beamsize=BeamSize("beamsize", "BL06I-OP-KBM-01", s4ygap)  