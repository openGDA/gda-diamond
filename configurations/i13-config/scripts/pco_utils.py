"""
File with functions to switch pco1 into different modes using controllers in gda.device.FindableObjectHolder pco1_plugins
"""
from gda.factory import Finder
class PCO_Util:
    def __getController(self, name):
        finder = Finder.getInstance()
        pco1_plugins=finder.find("pco1_plugins")
        controller = pco1_plugins.get(name)
        if controller is None:
            raise Exception(name + " not found")
        return controller
    def __init__(self):
        self.pco1_continuousSoftwareTrigger = self.__getController("pco1_continuousSoftwareTrigger")
        self.pco1_ffmpeg1 = self.__getController("pco1_ffmpeg1")
        self.pco1_proc1 = self.__getController("pco1_proc1")
        self.pco1_cam_base = self.__getController("pco1_cam_base")
    def setupForAlignment(self):
        """
        Turns camera on to auto continuous mode 
        """
        self.pco1_continuousSoftwareTrigger.prepareForCollection(1.0,1)
        self.pco1_continuousSoftwareTrigger.collectData()
#        self.pco1_ffmpeg1.
        self.pco1_proc1.getPluginBase().setNDArrayPort("pco1.cam")
        self.pco1_proc1.getPluginBase().enableCallbacks()
        self.pco1_proc1.setEnableOffsetScale(1)
        self.pco1_ffmpeg1.getPluginBase().setNDArrayPort(self.pco1_proc1.getPluginBase().getPortName())
        self.pco1_ffmpeg1.getPluginBase().enableCallbacks()
        
        