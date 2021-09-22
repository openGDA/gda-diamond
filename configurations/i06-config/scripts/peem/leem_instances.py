'''
create objects for LEEM control
Created on 21 Feb 2017

@author: fy65
'''
from i06shared import installation
from gda.device.scannable import DummyScannable
print "-"*100
print "Setup LEEM objects: leem_stv,leem_obj,leem_objStigmA,leem_objStigmB, leem_fov,leem_p2alignx"
from Diamond.Utility.BeamlineFunctions import logger
import sys
# Setup Leem2000 before calling usePeem as leem_fov is needed by it.
if installation.isLive():
    try:
        from peem import LEEM2000_tcp
        leem2000=LEEM2000_tcp.leem2000()
        leem_stv=LEEM2000_tcp.leem_scannable("leem_stv","Start voltage", '%.2f' , leem2000)
        leem_obj=LEEM2000_tcp.leem_scannable("leem_obj","Objective", '%.2f' , leem2000)
        leem_objStigmA=LEEM2000_tcp.leem_scannable("leem_objStigmA","Obj.stigm. a", '%.2f' , leem2000)
        leem_objStigmB=LEEM2000_tcp.leem_scannable("leem_objStigmB","Obj.stigm. b", '%.2f' , leem2000)
        FOV=LEEM2000_tcp.leem_readonly("FOV", "prl", leem2000)
        leem_p2alignx = LEEM2000_tcp.leem_scannable("leem_p2alignx","P2 align.x", '%.8f', leem2000)
        mcpScreen = LEEM2000_tcp.leem_scannable("mcpScreen", "val 104", '%.3f', leem2000); mcpScreen.readOnly=True; mcpScreen.setOffset(0.107)
        mcpPlate = LEEM2000_tcp.leem_scannable("mcpPlate", "val 105", '%.3f', leem2000); mcpPlate.readOnly=True; mcpPlate.setOffset(0.038098)
    except:
        exceptionType, exception, traceback=sys.exc_info();
        logger.dump("Error connecting to LEEM2000 ", exceptionType, exception, traceback, False)
else:
    leem_stv = DummyScannable("leem_stv"); leem_stv.setOutputFormat(['%.2f']); leem_stv.setIncrement(2.5)
    leem_obj = DummyScannable("leem_obj"); leem_obj.setOutputFormat(['%.2f']); leem_obj.setIncrement(1.0)
    leem_objStigmA = DummyScannable("leem_objStigmA"); leem_objStigmA.setOutputFormat(['%.2f']); leem_objStigmA.setIncrement(3.0)
    leem_objStigmB = DummyScannable("leem_objStigmB"); leem_objStigmB.setOutputFormat(['%.2f']); leem_objStigmB.setIncrement(4.0)
    FOV = DummyScannable("FOV"); FOV.setOutputFormat(['%.2f']); FOV.setIncrement(5.0)
    leem_p2alignx = DummyScannable("leem_p2alignx"); leem_p2alignx.setOutputFormat(['%.8f']); leem_p2alignx.setIncrement(6.0)
    mcpScreen = DummyScannable("mcpScreen"); mcpScreen.setOutputFormat(['%.3f']); mcpScreen.setIncrement(0.107)
    mcpPlate = DummyScannable("mcpPlate"); mcpPlate.setOutputFormat(['%.3f']); mcpPlate.setIncrement(0.038098)