'''
Script provided by Francesco Maccherozzi 
Created on 2 Oct 2017

@author: fy65
'''
from gda.epics import CAClient 

def pco2000binning(binning):
    ca = CAClient()
    binXpv = "BL06I-EA-DET-01:CAM:BinX"
    binYpv = "BL06I-EA-DET-01:CAM:BinY"
    sizeXpv = "BL06I-EA-DET-01:CAM:SizeX"
    sizeYpv = "BL06I-EA-DET-01:CAM:SizeY"
    pcoStop()
    if (binning==1):
        ca.caput(binXpv,1)
        ca.caput(binYpv,1)
        ca.caput(sizeXpv,2048)
        ca.caput(sizeYpv,2048)
    elif (binning==2):
        ca.caput(binXpv,2)
        ca.caput(binYpv,2)
        ca.caput(sizeXpv,1024)
        ca.caput(sizeYpv,1024)
    else:
        print "-> error: binning value should 1 or 2."

def pcoStart():
    ca = CAClient()
    ca.caput("BL06I-EA-DET-01:CAM:Acquire",1)
    
def pcoStop():
    ca = CAClient()
    ca.caput("BL06I-EA-DET-01:CAM:Acquire",0)
    
def pcoSetAcqTime(acqTime):
    ca = CAClient()
    expTimePV = "BL06I-EA-DET-01:CAM:AcquireTime"
    acqPeriodPV = "BL06I-EA-DET-01:CAM:AcquirePeriod"
    pcoStop()
    ca.caput(expTimePV, acqTime)
    ca.caput(acqPeriodPV, acqTime)
    pcoStart()

def pcopreview():
    ca = CAClient()
    pixelRatePV = "BL06I-EA-DET-01:CAM:PIX_RATE"  #0=10 KHz (default), 1=40KHz
    ADCModePV = "BL06I-EA-DET-01:CAM:ADC_MODE"  #0= 1ADC, 1= 2ADC
    avgEnablePV = "BL06I-EA-DET-01:PROC:EnableFilter"
    avgFilterNumPV = "BL06I-EA-DET-01:PROC:NumFilter"
    avgFilterTypePV = "BL06I-EA-DET-01:PROC:FilterType"
    pcoStop()
    #this is just to make sure the camera is in 10KHz pixelrate, 
    #otherwise the overexposure protection does not work!
    ca.caput(pixelRatePV,0) #this is just to make sure the camera is
    ca.caput(ADCModePV,1)
    #configure avg
    ca.caput(avgFilterTypePV,0)
    ca.caput(avgFilterNumPV,3)
    ca.caput(avgEnablePV,1)
    pcoSetAcqTime(0.1)
    pcoStart()
    
def pcoimaging():
    ca = CAClient()
    pixelRatePV = "BL06I-EA-DET-01:CAM:PIX_RATE"  #0=10 KHz (default), 1=40KHz
    ADCModePV = "BL06I-EA-DET-01:CAM:ADC_MODE"  #0= 1ADC, 1= 2ADC
    avgEnablePV = "BL06I-EA-DET-01:PROC:EnableFilter"
    pcoStop()
    #this is just to make sure the camera is in 10KHz pixelrate, 
    #otherwise the overexposure protection does not work!
    ca.caput(pixelRatePV,0) #this is just to make sure the camera is
    ca.caput(ADCModePV,0)
    #configure avg
    ca.caput(avgEnablePV,0)
    pcoStart()
    
def adjust():
    ca = CAClient()
    contrastAdjustPV = "BL06I-EA-DET-01:PROC:AutoOffsetScale"
    ca.caput(contrastAdjustPV,1)
    
def picture(acqTime):
    exec("scan t 1 1 1 pcotif acqTime") 
    
def pcorot(angle):
    ca = CAClient()
    rotPV = "BL06I-EA-DET-01:ROT:Angle"
    ca.caput(rotPV, -angle)