'''
create objects for LEEM control
Created on 21 Feb 2017

@author: fy65
'''
print "-"*100
print "Setup LEEM objects: leem_stv,leem_obj,leem_objStigmA,leem_objStigmB, leem_fov,leem_p2alignx"
from Diamond.Utility.BeamlineFunctions import logger
import sys
# Setup Leem2000 before calling usePeem as leem_fov is needed by it.
try:
    from peem import LEEM2000_tcp
    leem2000=LEEM2000_tcp.leem2000()
    leem_stv=LEEM2000_tcp.leem_scannable("leem_stv","Start voltage", '%.2f' , leem2000)
    leem_obj=LEEM2000_tcp.leem_scannable("leem_obj","Objective", '%.2f' , leem2000)
    leem_objStigmA=LEEM2000_tcp.leem_scannable("leem_objStigmA","Obj.stigm. a", '%.2f' , leem2000)
    leem_objStigmB=LEEM2000_tcp.leem_scannable("leem_objStigmB","Obj.stigm. b", '%.2f' , leem2000)
#     leem_fov=LEEM2000_tcp.leem_readonly("leem_fov", "prl", leem2000)
    FOV=LEEM2000_tcp.leem_readonly("FOV", "prl", leem2000)
    leem_p2alignx = LEEM2000_tcp.leem_scannable("leem_p2alignx","P2 align.x", '%.8f', leem2000)
    #leem_temp = LEEM2000_tcp.leem_scannable("leem_p2alignx","39", '%.2f', leem2000)
    mcpScreen = LEEM2000_tcp.leem_scannable("mcpScreen", "val 104", '%.3', leem2000); mcpScreen.readOnly=True; mcpScreen.setOffset(0.107)
    mcpPlate = LEEM2000_tcp.leem_scannable("mcpPlate", "val 105", '%.3', leem2000); mcpPlate.readOnly=True; mcpPlate.setOffset(0.038098)
except:
    exceptionType, exception, traceback=sys.exc_info();
    logger.dump("Error connecting to LEEM2000 ", exceptionType, exception, traceback, False)
