import time, sys
import gda.factory.Finder
import uk.ac.gda.arpes.beans.ARPESScanBean
from gda.data.metadata import GDAMetadataProvider
import gda.jython.commands.ScannableCommands
from gda.commandqueue import JythonScriptProgressProvider

class APRESRun:
    
    def __init__(self, beanFile):
        self.bean = uk.ac.gda.arpes.beans.ARPESScanBean.createFromXML(beanFile)
        self.scienta = gda.factory.Finder.getInstance().listAllLocalObjects("uk.ac.gda.arpes.detector.VGScientaAnalyser")[0]
        self.progresscounter = 0
        self.totalSteps = 5
        self.lastreportedmeasurement = None
        
    def reportProgress(self, message):
        self.progresscounter += 1
        if self.totalSteps < self.progresscounter:
            self.totalSteps = self.progresscounter
            print "max progress steps: %d" % self.totalSteps
        JythonScriptProgressProvider.sendProgress(100.0*self.progresscounter/self.totalSteps, "%s  (%3.1f%% done)" % (message, 100.0*self.progresscounter/self.totalSteps))
    
        
    def checkDevice(self):
        pass
    
    def setStorageTemperature(self):
        self.monitorAsynchronousMethod(self.bssc.waitTemperatureSample(self.bean.getSampleStorageTemperature()))
        #pass
    
    def setExposureTemperature(self, temperature):
        self.monitorAsynchronousMethod(self.bssc.waitTemperatureSEU((temperature)))
        #pass
    
    def setTitle(self, title):
        GDAMetadataProvider.getInstance().setMetadataValue("title", title)
    
    def run(self):
        self.reportProgress("Initialising")
        self.checkDevice()
        if self.bean.isSweptMode():
            raise "swept mode not supported"
        self.scienta.prepareFixedMode()
        self.scienta.controller.setPassEnergy(self.bean.getPassEnergy())
        self.scienta.controller.setLensMode(self.bean.getLensMode())
        self.scienta.controller.setCentreEnergy((self.bean.getEndEnergy()+self.bean.getStartEnergy())/2.0)
        self.scienta.getAdBase().setNumExposures(self.bean.getIterations())
        self.scienta.getAdBase().setTriggerMode(0)
        self.scienta.getAdBase().setImageMode(0)
        self.scienta.setCollectionTime(self.bean.getTimePerStep())
        #set temperature
        #set photonenergy
        self.reportProgress("Running Acquisition")
        gda.jython.commands.ScannableCommands.staticscan([self.scienta])
        self.reportProgress("Finalising")
        time.sleep(2)
