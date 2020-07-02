from gda.factory import Finder
import sys
from gdascripts.messages import handle_messages
from gdascripts.parameters import beamline_parameters
from gda.jython import InterfaceProvider
from epics_scripts.pv_scannable_utils import createPVScannable, caput, caget

class TomoDet():
    def __getController(self, name):
        pco1_plugins=Finder.find("pco1_plugins")
        controller = pco1_plugins.get(name)
        if controller is None:
            raise Exception(name + " not found")
        return controller
    def __init__(self):
        self.pco1_ffmpeg1 = self.__getController("pco1_ffmpeg1")
#        self.pco1_ffmpeg2 = self.__getController("pco1_ffmpeg2")
        self.pco1_proc1 = self.__getController("pco1_proc1")
        self.pco1_roi1 = self.__getController("pco1_roi1")        
        self.pco1_cam_base = self.__getController("pco1_cam_base")        
        self.pco1_stat = self.__getController("pco1_stat")        
        self.pco1_arr = self.__getController("pco1_arr")        
        self.model = self.pco1_cam_base.model_RBV
        self.pco1_autoContinuousTrigger = self.__getController("pco1_autoContinuousTrigger")
        return

    def getCurrentExposureTime(self):
		return self.pco1_cam_base.getAcquireTime_RBV()

    def setupStream(self, acqTime=None, procScaleFactor= None):
        """
        Function called from java
        """
        return self.setupForAlignment(exposureTime=acqTime, scale=procScaleFactor)
    
    def setupForAlignment(self, exposureTime=None, scale= None):
        """
        
        Function to configure the PCO areaDetector system to take images continuously with
        a given exposure time and/or scale. If either argument is undefined then the current
        value read from EPICS is used
        
        """
        if exposureTime is not None:
            exposureTime = float(exposureTime)
        else:
            exposureTime = self.pco1_cam_base.getAcquireTime_RBV()
        
        if scale is not None:
            scale = int(scale)
        else:
            scale = self.pco1_proc1.getScale_RBV()
        
        self.pco1_cam_base.stopAcquiring() 
        
        if self.model == "PCO.Camera Dimax":
            self.pco1_autoContinuousTrigger.triggerMode=2 #EXTERNAL_AND_SOFTWARE otherwise it runs too fast
            self.pco1_autoContinuousTrigger.prepareForCollection(exposureTime,1,None)
        elif self.model == "GC1020C":
            pass # gige camera from test lab
        elif self.model == "Basic simulator":
            self.pco1_cam_base.startAcquiring()
        else:
            self.pco1_autoContinuousTrigger.triggerMode=0 #AUTO - ok for PCO4000
            self.pco1_autoContinuousTrigger.prepareForCollection(exposureTime,1,None)
            
        self.pco1_proc1.getPluginBase().disableCallbacks()
        self.pco1_proc1.getPluginBase().setBlockingCallbacks(1)
        self.pco1_proc1.getPluginBase().setMinCallbackTime(0.5)
        self.pco1_proc1.getPluginBase().setNDArrayPort(self.pco1_cam_base.getPortName_RBV())
        self.pco1_proc1.setEnableOffsetScale(1)
        self.pco1_proc1.setScale(scale)
        self.pco1_proc1.getPluginBase().enableCallbacks()

        self.pco1_stat.getPluginBase().disableCallbacks()
        self.pco1_stat.getPluginBase().setBlockingCallbacks(1)
        self.pco1_stat.getPluginBase().setMinCallbackTime(0.5)
        self.pco1_stat.getPluginBase().setNDArrayPort(self.pco1_cam_base.getPortName_RBV())
        self.pco1_stat.getPluginBase().enableCallbacks()
        
        
        self.pco1_roi1.getPluginBase().disableCallbacks()
        self.pco1_roi1.getPluginBase().setMinCallbackTime(0.5)
        self.pco1_roi1.getPluginBase().setBlockingCallbacks(1)
        self.pco1_roi1.getPluginBase().setNDArrayPort(self.pco1_cam_base.getPortName_RBV())
        self.pco1_roi1.getPluginBase().enableCallbacks()
 
        self.pco1_arr.getPluginBase().disableCallbacks()
        self.pco1_arr.getPluginBase().setMinCallbackTime(0.5)
        self.pco1_arr.getPluginBase().setBlockingCallbacks(1)
        self.pco1_arr.getPluginBase().setNDArrayPort(self.pco1_roi1.getPluginBase().getPortName_RBV())
        self.pco1_arr.getPluginBase().enableCallbacks()
 
        self.pco1_ffmpeg1.getPluginBase().disableCallbacks()
        self.pco1_ffmpeg1.getPluginBase().setBlockingCallbacks(0)
        self.pco1_ffmpeg1.getPluginBase().setNDArrayPort(self.pco1_proc1.getPluginBase().getPortName_RBV())
        self.pco1_ffmpeg1.getPluginBase().enableCallbacks()
        
#        if self.model != "GC1020C":
#            self.pco1_ffmpeg2.getPluginBase().disableCallbacks()

        if self.pco1_cam_base.model_RBV == "PCO.Camera Dimax":
#            self.pco1_cam_base.startAcquiring() 
#epg 7/8/13 hack to get live stream working - the above line arms the detector which seems to stop it working 
#in continuous mode
            caput("BL13I-EA-DET-01:CAM:Acquire",1 )
        elif self.model =="Basic simulator":
            self.pco1_cam_base.setImageMode(2) # continuous
            self.pco1_cam_base.startAcquiring()
        else:
            self.pco1_autoContinuousTrigger.collectData()
	    return True
    
    def stop(self):
        self.pco1_cam_base.stopAcquiring() 
        
    def autoCentre(self):
        print "Auto-Centre"
        jns = beamline_parameters.JythonNameSpaceMapping(InterfaceProvider.getJythonNamespace())
        cameraXYScannable = jns.cameraXYScannable
        cameraXYScannable.autoCentre(2004, 1336)
        rotationAxisXScannable = jns.rotationAxisXScannable
        rotationAxisXScannable.autoCentre(2004)
    
    def setCameraLens(self, position):
        try:
            print "Setting cam01_objective to " + `position`
            cam01_objective=Finder.find("cam01_objective")
            cam01_objective.moveTo(position)
            cam01_objective.waitWhileBusy()
            print "Done"
        except :
            exceptionType, exception, traceback = sys.exc_info()
            handle_messages.log(None, "Error setting cam01_objective to "+ `position` , exceptionType, exception, traceback, False)      

    def setBinningX(self, externalPosition, internalPosition):
        try:
            print "Setting binning_x to " + `externalPosition`
            self.stop()
            self.pco1_cam_base.setBinX(internalPosition)
            self.pco1_cam_base.setSizeX(self.pco1_cam_base.getMaxSizeX_RBV())
            print "Done"
        except :
            exceptionType, exception, traceback = sys.exc_info()
            handle_messages.log(None, "Error setting binning x to "+ `externalPosition` , exceptionType, exception, traceback, False)      
    
    def setBinningY(self,  externalPosition, internalPosition):
        try:
            print "Setting binning_y to " + `externalPosition`
            self.stop()
            self.pco1_cam_base.setBinY(internalPosition)
            self.pco1_cam_base.setSizeY(self.pco1_cam_base.getMaxSizeY_RBV())
            print "Done"
        except :
            exceptionType, exception, traceback = sys.exc_info()
            handle_messages.log(None, "Error setting binning y to "+ `externalPosition` , exceptionType, exception, traceback, False)      


    def setRegionX(self, externalPosition, internalPosition):
        try:
            print "Setting region X to " + `externalPosition`
            self.stop()
#            self.pco1_cam_base.setBinX(internalPosition)
            maxX = self.pco1_cam_base.getMaxSizeX_RBV()
            maxXAfterBinning = maxX /self.pco1_cam_base.getBinX_RBV()
            
            if externalPosition == "Full":
                start = 0
                size = maxXAfterBinning
            else:
                start = maxXAfterBinning/4
                size = maxXAfterBinning/2
                
            print "Done"
        except :
            exceptionType, exception, traceback = sys.exc_info()
            handle_messages.log(None, "Error setting region x to "+ `externalPosition` , exceptionType, exception, traceback, False)      

    def setRegionY(self, externalPosition, internalPosition):
        try:
            print "Setting region Y to " + `externalPosition`
            self.stop()
#            self.pco1_cam_base.setBinX(internalPosition)
            maxY = self.pco1_cam_base.getMaxSizeY_RBV()
            maxYAfterBinning = maxY /self.pco1_cam_base.getBinY_RBV()
            
            if externalPosition == "Full":
                start = 0
                size = maxYAfterBinning
            else:
                start = maxYAfterBinning/4
                size = maxYAfterBinning/2
                
            print "Done"
        except :
            exceptionType, exception, traceback = sys.exc_info()
            handle_messages.log(None, "Error setting region y to "+ `externalPosition` , exceptionType, exception, traceback, False)      
