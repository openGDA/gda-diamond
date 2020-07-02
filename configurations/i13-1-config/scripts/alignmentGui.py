from gda.factory import Finder
import sys
from gdascripts.messages import handle_messages
from gdascripts.parameters import beamline_parameters
from gda.jython import InterfaceProvider
from epics_scripts.pv_scannable_utils import caput

class TomoDet():
    def __getController(self, name):
        pco1_plugins=Finder.find("pco1_plugins")
        controller = pco1_plugins.get(name)
        if controller is None:
            raise Exception(name + " not found")
        return controller
    def __init__(self):
        self.pco1_ffmpeg = self.__getController("pco1_ffmpeg")
        self.pco1_proc = self.__getController("pco1_proc")
        self.pco1_roi = self.__getController("pco1_roi")        
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
            scale = self.pco1_proc.getScale_RBV()
        
        self.pco1_cam_base.stopAcquiring() 
        
        if self.model == "PCO.Camera Dimax":
            self.pco1_autoContinuousTrigger.triggerMode=2 #EXTERNAL_AND_SOFTWARE otherwise it runs too fast
        else:
            if self.model == "GC1020C" or self.model =="Basic simulator":
                pass # gige camera from test lab
            else:
                self.pco1_autoContinuousTrigger.triggerMode=0 #AUTO - ok for PCO4000
            
        self.pco1_autoContinuousTrigger.prepareForCollection(exposureTime,1,None)

        self.pco1_proc.getPluginBase().disableCallbacks()
        self.pco1_proc.getPluginBase().setBlockingCallbacks(1)
        self.pco1_proc.getPluginBase().setMinCallbackTime(0.5)
        self.pco1_proc.getPluginBase().setNDArrayPort(self.pco1_cam_base.getPortName_RBV())
        self.pco1_proc.setEnableOffsetScale(1)
        self.pco1_proc.setScale(scale)
        self.pco1_proc.getPluginBase().enableCallbacks()

        self.pco1_stat.getPluginBase().disableCallbacks()
        self.pco1_stat.getPluginBase().setBlockingCallbacks(1)
        self.pco1_stat.getPluginBase().setMinCallbackTime(0.5)
        self.pco1_stat.getPluginBase().setNDArrayPort(self.pco1_cam_base.getPortName_RBV())
        self.pco1_stat.getPluginBase().enableCallbacks()
        
        
        self.pco1_roi.getPluginBase().disableCallbacks()
        self.pco1_roi.getPluginBase().setMinCallbackTime(0.5)
        self.pco1_roi.getPluginBase().setBlockingCallbacks(1)
        self.pco1_roi.getPluginBase().setNDArrayPort(self.pco1_cam_base.getPortName_RBV())
        self.pco1_roi.getPluginBase().enableCallbacks()
 
        self.pco1_arr.getPluginBase().disableCallbacks()
        self.pco1_arr.getPluginBase().setMinCallbackTime(0.5)
        self.pco1_arr.getPluginBase().setBlockingCallbacks(1)
        self.pco1_arr.getPluginBase().setNDArrayPort(self.pco1_roi.getPluginBase().getPortName_RBV())
        self.pco1_arr.getPluginBase().enableCallbacks()
 
        self.pco1_ffmpeg.getPluginBase().disableCallbacks()
        self.pco1_ffmpeg.getPluginBase().setBlockingCallbacks(0)
        self.pco1_ffmpeg.getPluginBase().setNDArrayPort(self.pco1_proc.getPluginBase().getPortName_RBV())
        self.pco1_ffmpeg.getPluginBase().enableCallbacks()
        
#        if self.model != "GC1020C":
#            self.pco1_ffmpeg2.getPluginBase().disableCallbacks()

        if self.pco1_cam_base.model_RBV == "PCO.Camera Dimax":
#            self.pco1_cam_base.startAcquiring() 
#epg 7/8/13 hack to get live stream working - the above line arms the detector which seems to stop it working 
#in continuous mode
            caput("BL13I-EA-DET-01:CAM:Acquire",1 )
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
            print "Setting lens to " + `position`
            lens=Finder.find("lens")
            lens.moveTo(position)
            lens.waitWhileBusy()
            print "Done"
        except :
            exceptionType, exception, traceback = sys.exc_info()
            handle_messages.log(None, "Error setting lens to "+ `position` , exceptionType, exception, traceback, False)      
