'''
Created on 7 Jun 2011

@author: rjw82
'''

from BeamlineParameters import JythonNameSpaceMapping
from gda.scan import SimpleContinuousScan
from gda.jython.scriptcontroller.event import ScanCreationEvent, ScanFinishEvent, ScriptProgressEvent
from gda.factory import Finder

def ede(edescan,useroptions):
    
    jython_mapper = JythonNameSpaceMapping()
    
    controller = Finder.getInstance().find("EdeScriptObserver")
    
    # set up any sample environments here
    controller.update(None,ScriptProgressEvent("Running user script"))
    print "would run the",useroptions.getScriptName(),"script at this point"
    
    # configure the detector
    controller.update(None,ScriptProgressEvent("Loading parameters into detector"))
    xhDet = jython_mapper.XHDetector
    xhDet.loadParameters(edescan)
    
    # run any user defined script here 
    
    print "running EDE scan:",edescan
    controller.update(None,ScriptProgressEvent("Running scan"))
    thisscan = SimpleContinuousScan(xhDet)
    controller.update(None,ScanCreationEvent(thisscan.getName()))
    thisscan.runScan()  
    controller.update(None,ScanFinishEvent(thisscan.getName(),ScanFinishEvent.FinishType.OK));

    
    #xhDet.start()
    