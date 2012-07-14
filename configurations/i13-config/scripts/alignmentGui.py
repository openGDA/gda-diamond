from gda.factory import Finder
class TomoDet():
    def __getController(self, name):
        finder = Finder.getInstance()
        pco1_plugins=finder.find("pco1_plugins")
        controller = pco1_plugins.get(name)
        if controller is None:
            raise Exception(name + " not found")
        return controller
    def __init__(self):
        self.pco1_autoContinuousTrigger = self.__getController("pco1_autoContinuousTrigger")
        self.pco1_ffmpeg1 = self.__getController("pco1_ffmpeg1")
        self.pco1_proc1 = self.__getController("pco1_proc1")
        self.pco1_roi1 = self.__getController("pco1_roi1")        
        self.pco1_cam_base = self.__getController("pco1_cam_base")        
        return
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
        
        self.pco1_autoContinuousTrigger.prepareForCollection(exposureTime,1)
        self.pco1_proc1.getPluginBase().disableCallbacks()
        self.pco1_proc1.getPluginBase().setBlockingCallbacks(0)
        self.pco1_proc1.getPluginBase().setNDArrayPort(self.pco1_cam_base.getPortName_RBV())

        self.pco1_proc1.setEnableOffsetScale(1)
        self.pco1_proc1.setScale(scale)
        self.pco1_proc1.getPluginBase().enableCallbacks()
 
        self.pco1_ffmpeg1.getPluginBase().disableCallbacks()
        self.pco1_ffmpeg1.getPluginBase().setBlockingCallbacks(0)
        self.pco1_ffmpeg1.getPluginBase().setNDArrayPort(self.pco1_proc1.getPluginBase().getPortName_RBV())
        self.pco1_ffmpeg1.getPluginBase().enableCallbacks()
        
        self.pco1_autoContinuousTrigger.collectData()
        
        return True
    