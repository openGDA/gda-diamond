"""
File with functions to switch pco1 into different modes using controllers in gda.device.FindableObjectHolder pco1_plugins
"""
from gda.factory import Finder
class PCO_Util:
    def __getController(self, name):
        pco1_plugins=Finder.find("pco1_plugins")
        controller = pco1_plugins.get(name)
        if controller is None:
            raise Exception(name + " not found")
        return controller
    def __init__(self):
        self.pco1_autoContinuousTrigger = self.__getController("pco1_autoContinuousTrigger")
        self.pco1_ffmpeg1 = self.__getController("pco1_ffmpeg1")
        self.pco1_proc1 = self.__getController("pco1_proc1")
        self.pco1_cam_base = self.__getController("pco1_cam_base")

    def setupForAlignment(self, collectionTime=1.0, scale=1):
        """
        Turns camera on to auto continuous mode 
        """
        self.pco1_autoContinuousTrigger.prepareForCollection(collectionTime,1)
        self.pco1_proc1.getPluginBase().setNDArrayPort(self.pco1_cam_base.getPortName_RBV())
        self.pco1_proc1.getPluginBase().enableCallbacks()
        self.pco1_proc1.getPluginBase().setBlockingCallbacks(0)
        self.pco1_proc1.setEnableOffsetScale(scale)

        self.pco1_ffmpeg1.getPluginBase().setNDArrayPort(self.pco1_proc1.getPluginBase().getPortName_RBV())
        self.pco1_ffmpeg1.getPluginBase().enableCallbacks()
        self.pco1_ffmpeg1.getPluginBase().setBlockingCallbacks(0)

#        self.pco1_autoContinuousTrigger.collectData()

        
def setupPCO400ForAlignment(collectionTime=1.0, scale=1):
    PCO_Util().setupForAlignment(collectionTime, scale)
        
