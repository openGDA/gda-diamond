from gda.device.detector import NXDetector
from gda.factory import Finder

merlin_plugins = Finder.find("merlin_plugins")
merlin_roi1 = merlin_plugins.get("merlin_roi1")
merlin_roi2 = merlin_plugins.get("merlin_roi2")
merlin_stat1 = merlin_plugins.get("merlin_stat1")
merlin_stat2 = merlin_plugins.get("merlin_stat2")

class stxm_det(NXDetector):
    def __getController(self, name):
        plugins=Finder.find("merlin_plugins")
        controller = plugins.get(name)
        if controller is None:
            raise Exception(name + " not found")
        return controller
    
    def __init__(self, name, det, extraPluginList=[merlin_roi1, merlin_roi2, merlin_stat1, merlin_stat2]):
        print "init called"
        self.setName(name)
        self.det = det
        self.setCollectionStrategy(self.det.getCollectionStrategy())
        #print "collectionStrategy = " + str(type(self.getCollectionStrategy()))
        
        self.detPluginList = self.det.getAdditionalPluginList()
        #type(self.detPluginList)
        #print "additionalPluginList = " + len(self.getAdditionalPluginList())
        self.setAdditionalPluginList(self.detPluginList)
        #self.setAdditionalPluginList(extraPluginList)
        self.stat1 = self.__getController("merlin_stat1")
        self.stat2 = self.__getController("merlin_stat2")
        self.roi11 = self.__getController("merlin_roi1")
        self.roi11 = self.__getController("merlin_roi2")
        
        self.stat1.getPluginBase().disableCallbacks()
        name1 = self.roi1.getPortName_RBV()
        print "roi1 = " + name1
        #self.stat1.getPluginBase().setNDArrayPort(self.roi1.getPortName_RBV())
        self.stat1.getPluginBase().enableCallbacks()
        
        self.stat2.getPluginBase().disableCallbacks()
        name2 = self.roi2.getPortName_RBV()
        print "roi2 " + name2
        #self.stat2.getPluginBase().setNDArrayPort(self.roi2.getPortName_RBV())
        self.stat2.getPluginBase().enableCallbacks()
    
    def atScanEnd(self):
        NXDetector.atScanEnd()
        # add more
    
    def testFn(self):
        print "testFn called"