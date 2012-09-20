'''
Created on 7 Jun 2011

@author: rjw82
'''

from BeamlineParameters import JythonNameSpaceMapping
from gda.scan import SimpleContinuousScan
from gda.jython.scriptcontroller.event import ScanCreationEvent, ScanFinishEvent, ScriptProgressEvent
from gda.factory import Finder
from uk.ac.gda.beans import BeansFactory
from gda.data import PathConstructor

def ede(edescan,useroptions,tfgParameters,folderName, numberRepetitions):
    
    jython_mapper = JythonNameSpaceMapping()
    xmlFolderName = ExafsEnvironment().getScriptFolder() + folderName + "/"
    
    controller = Finder.getInstance().find("EdeScriptObserver")
    
    # set up any sample environments here
    controller.update(None,ScriptProgressEvent("Running user script"))
    edescanBean = BeansFactory.getBeanObject(xmlFolderName, edescan);
    
    # configure the detector
    print "Loading parameters from file",edescan
    controller.update(None,ScriptProgressEvent("Loading parameters into detector"))
    xhDet = jython_mapper.XHDetector
    xhDet.loadParameters(edescanBean)
    
    # run any user defined script here 
    
    print "Running EDE scan:",edescan
    controller.update(None,ScriptProgressEvent("Running scan"))
    thisscan = SimpleContinuousScan(xhDet)
    controller.update(None,ScanCreationEvent(thisscan.getName()))
    thisscan.runScan()  
    controller.update(None,ScanFinishEvent(thisscan.getName(),ScanFinishEvent.FinishType.OK));

    
    #xhDet.start()
    
    
class ExafsEnvironment:
    testScriptFolder = None
    
    def getScriptFolder(self):
        if ExafsEnvironment.testScriptFolder != None:
            return ExafsEnvironment.testScriptFolder
        dataDirectory = PathConstructor.createFromDefaultProperty()
        return dataDirectory + "/xml/"

    testScannable = None
    
    def getScannable(self):
        if ExafsEnvironment.testScannable != None:
            return ExafsEnvironment.testScannable
        # The scannable name is defined in the XML when not in testing mode.
        # Therefore the scannable argument is omitted from the bean
        return None

    