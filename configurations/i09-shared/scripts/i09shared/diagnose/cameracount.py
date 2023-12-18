'''
Created on 26 Sep 2012

@author: fy65
'''
from gda.device.detector import DetectorBase
from gda.device import Detector
from gda.epics import CAClient
from gov.aps.jca.event import MonitorListener
from threading import Timer
import scisoftpy as dnp
from gda.data import NumTracker
from gda.jython import InterfaceProvider
import os

i09NumTracker = NumTracker("i09");
def nextDataFile():
    '''query the absolute path of the next working file'''
    curdir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    filenumber = i09NumTracker.incrementNumber();
    return os.path.join(curdir,str(filenumber)+".txt")
    
class CameraCount(DetectorBase):
    '''
    A scannable detector for diagnose camera providing Starndard EPICS area detector interface.
    By default it returns the total count of the camera when scanning. It also designed to record
    a time series of counts over specified period into a data file.
    Usage:
        to create an diagnose camera scannable object:
        >>>sd3cam=CameraCount("sd3cam","SD3","BL09J-MO-SD-03","counts", "%d")
        to collect time series for 30 seconds at exposure time of 0.1 second
        >>>sd3cam.collectFor(30, 0.1)
        to scan a motor with exposure time of 0.1 second
        >>>scan motor 1 100 1 sd3cam 0.1
    '''


    def __init__(self, name, epicsdevicename, pvroot, unitstring, formatstring):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.Units=[unitstring]
        self.setOutputFormat([formatstring])
        self.epicsdevicename=epicsdevicename
        self.pvroot=pvroot
        self.exposure=CAClient(pvroot+":CAM:AcquireTime")
        self.imagemode=CAClient(pvroot+":CAM:ImageMode")
        self.acquire=CAClient(pvroot+":CAM:Acquire")
        self.roiport=CAClient(pvroot+":ROI:NDArrayPort")
        self.roienablecallback=CAClient(pvroot+":ROI:EnableCallbacks")
        self.roienablex=CAClient(pvroot+":ROI:EnableX")
        self.roienabley=CAClient(pvroot+":ROI:EnableY")
        self.roiminx=CAClient(pvroot+":ROI:MinX")
        self.roiminy=CAClient(pvroot+":ROI:MinY")
        self.roisizex=CAClient(pvroot+":ROI:SizeX")
        self.roisizey=CAClient(pvroot+":ROI:SizeY")
        self.statenablecallback=CAClient(pvroot+":STAT:EnableCallbacks")
        self.statport=CAClient(pvroot+":STAT:NDArrayPort")
        self.statcompute=CAClient(pvroot+":STAT:ComputeStatistics")
        self.stattimestamp=CAClient(pvroot+":STAT:TimeStamp_RBV")
        self.stattotal=CAClient(pvroot+":STAT:Total_RBV")
        self.timestamp=[]
        self.counts=[]
    #override scannable APIs    
    def atScanStart(self):
        if not self.exposure.isConfigured():
            self.exposure.configure()
        self.exposurevalue=float(self.exposure.caget())
        if not self.acquire.isConfigured():
            self.acquire.configure()
        self.acquirestate=int(self.acquire.caget())
        if not self.stattotal.isConfigured():
            self.stattotal.configure()
        self.acquire.caput(0)
        #set camera
        if not self.imagemode.isConfigured():
            self.imagemode.configure()
        self.imagemodedata=int(self.imagemode.caget())
        self.imagemode.caput(0) #Single mode

    def atScanEnd(self):
        self.exposure.caput(self.exposurevalue)
        self.imagemode.caput(self.imagemodedata)
        self.acquire.caput(self.acquirestate)
        if self.exposure.isConfigured():
            self.exposure.clearup()
        if self.acquire.isConfigured():
            self.acquire.clearup()
        if self.stattotal.isConfigured():
            self.stattotal.clearup()
        if self.imagemode.isConfigured():
            self.imagemode.clearup()
            
    def stop(self):
        if not self.acquire.isConfigured():
            self.acquire.configure()
            self.acquire.caput(0)
            self.acquire.clearup()
        else:
            self.acquire.caput(0)        
    
    
    #override Detector APIs
    def prepareForCollection(self):
        #set ROI
        if not self.roiport.isConfigured():
            self.roiport.configure()
        self.roiport.caput(self.epicsdevicename+".CAM")
        if not self.roienablecallback.isConfigured():
            self.roienablecallback.configure()
        self.roienablecallback.caput(1)
        #set STAT
        if not self.statport.isConfigured():
            self.statport.configure()
        self.statport.caput(self.epicsdevicename+".ROI")
        if not self.statenablecallback.isConfigured():
            self.statenablecallback.configure()
        self.statenablecallback.caput(1)
        if not self.statcompute.isConfigured():
            self.statcompute.configure()
        self.statcomputedata=int(self.statcompute.caget())
        self.statcompute.caput(1)
        
    def endCollection(self):
        #set ROI
        if self.roiport.isConfigured():
            self.roiport.clearup()
        if self.roienablecallback.isConfigured():
            self.roienablecallback.clearup()
        #set STAT
        if self.statport.isConfigured():
            self.statport.clearup()
        if self.statenablecallback.isConfigured():
            self.statenablecallback.clearup()
        self.statcompute.caput(self.statcomputedat)
        if self.statcompute.isConfigured():
            self.statcompute.clearup()
        

    def setCollectionTime(self, t):
        if not self.exposure.isConfigured():
            self.exposure.configure()
            self.exposure.caput(t)
            self.exposure.clearup()
        else:
            self.exposure.caput(t)
    
    def getCollectionTime(self):
        value=-1.0
        if not self.exposure.isConfigured():
            self.exposure.configure()
            value=float(self.exposure.caget())
            self.exposure.clearup()
        else:
            value=float(self.exposure.caget())
        return value

    def collectData(self):
        if not self.acquire.isConfigured():
            self.acquire.configure()
            self.acquire.caput(1)
            self.acquire.clearup()
        else:
            self.acquire.caput(1)
            
    def readout(self):
        ''' return current total count'''
        output=0.0
        if not self.stattotal.isConfigured():
            self.stattotal.configure()
            output=float(self.stattotal.caget())
            self.stattotal.clearup()
        else:
            output=float(self.stattotal.caget())
        return float(output)
    
    def getStatus(self):
        status=-1
        if not self.acquire.isConfigured():
            self.acquire.configure()
            status=int(self.acquire.caget())
            self.acquire.clearup()
        else:
            status=self.acquire.caput(0)
        if status==1:
            return Detector.BUSY
        return Detector.IDLE
    

    # Area Detector ROI interface
    def setROI(self, minx,miny,sizex, sizey):
        if not self.roiminx.isConfigured():
            self.roiminx.configure()
            self.roiminx.caput(minx)
            self.roiminx.clearup()
        else:
            self.roiminx.caput(minx)
        if not self.roiminy.isConfigured():
            self.roiminy.configure()
            self.roiminy.caput(miny)
            self.roiminy.clearup()
        else:
            self.roiminy.caput(miny)
        if not self.roisizex.isConfigured():
            self.roisizex.configure()
            self.roisizex.caput(sizex)
            self.roisizex.clearup()
        else:
            self.roisizex.caput(sizex)
        if not self.roisizey.isConfigured():
            self.roisizey.configure()
            self.roisizey.caput(sizey)
            self.roisizey.clearup()
        else:
            self.roisizey.caput(sizey)
        
    def enableROI(self):
        if not self.roienablex.isConfigured():
            self.roienablex.configure()
            self.roienablex.caput(1)
            self.roienablex.clearup()
        else:
            self.roienablex.caput(1)
        if not self.roienabley.isConfigured():
            self.roienabley.configure()
            self.roienabley.caput(1)
            self.roienabley.clearup()
        else:
            self.roienabley.caput(1)
        
    def disableROI(self):
        if not self.roienablex.isConfigured():
            self.roienablex.configure()
            self.roienablex.caput(0)
            self.roienablex.clearup()
        else:
            self.roienablex.caput(0)
        if not self.roienabley.isConfigured():
            self.roienabley.configure()
            self.roienabley.caput(0)
            self.roienabley.clearup()
        else:
            self.roienabley.caput(0)

    #time series
    def collectFor(self, t, exposure=1.0):
        #get camera ready
        self.stop()
        if not self.imagemode.isConfigured():
            self.imagemode.configure()
            self.imagemode.caput(2) #Continuous mode
            self.imagemode.clearup()
        else:
            self.imagemode.caput(2) #Continuous mode
        self.prepareForCollection()
        self.setCollectionTime(exposure)
        self.timedata=EpicsMonitor('time')
        if not self.stattimestamp.isConfigured():
            self.stattimestamp.configure()
        self.timemonitor=self.stattimestamp.camonitor(self.timedata)
        self.countdata=EpicsMonitor('count')
        if not self.stattotal.isConfigured():
            self.stattotal.configure()
        self.countmonitor=self.stattotal.camonitor(self.countdata)
        timer=Timer(t,self.writeData)
        self.collectData()
        timer.start()
        
    def writeData(self):
        self.stop()
        self.stattimestamp.removeMonitor(self.timemonitor)
        self.stattotal.removeMonitor(self.countmonitor)
        filename=nextDataFile()
        print "saving data to %s, please wait..." % filename
        #length=min(self.timedata.getData().size, self.countdata.getData().size)
        timedataset=self.timedata.getData()
        countdataset=self.countdata.getData()
        dnp.plot.plot(timedataset, countdataset, "Plot")
        outfile=open(filename,"w")
        for time, count in zip(timedataset.getData().tolist(), countdataset.getData().tolist()):
            outfile.write("%f\t%d\n"% (time, count))
        outfile.close()
        #dnp.io.save(filename, [timedataset, countdataset], format="text") # write 2 text fileseach with one dataset
        print "collection completed."

class EpicsMonitor(MonitorListener):
    def __init__(self, name):
        self.data=[]
        self.name=name
        
    def monitorChanged(self, mevent):
        self.data.append(float(mevent.getDBR().getDoubleValue()[0]))
        
    def getData(self):
        dataset=dnp.asDataset(self.data[1:]) #@UndefinedVariable
        dataset.setName(self.name)
        return dataset

sd3cam=CameraCount("sd3cam","SD3","BL09J-MO-SD-03","counts", "%d")
