"""
Simple commands to control the tfg
"""
from gda.factory import Finder
from gda.device.timer import Tfg

def getTfg():
    return Finder.find("tfg")

def stop():
    """
    stops the tfg 
    """
    tfg=getTfg()
    tfg.stop()

def start():
    """
    start the tfg 
    """
    tfg=getTfg()
    tfg.start()
    

def setupAlternateTrigger( adc=0, alternate=0  ):
    """
    setup alternate sources for 8 of the least used triggers - these can be used for Start, pause or continue
    
    Usage :
    setupAlternateTrigger( adc=0, alternate=0  ):
    
    See Programming from da.server section of the TFg2 User Manual available at:
    
    http://confluence.diamond.ac.uk/display/DATAACQ/TFG2+User+Manual 
    
    for details of arguments
    """
    tfg=getTfg()
    tfg.getDaServer().sendCommand("tfg setup-trig start adc" + `adc` + " alternate " + `alternate`)
    
    
def sendSimplyTrigger(cycles=10000, deadTime=1, liveTime=1, deadTimePort=0, livePort=65535, deadPausePort=0, livePausePort=0):
    """
    makes the tfg run a single frame multiple times
    
    Usage :
    sendSimplyTrigger(cycles, deadTime=1, liveTime=1, deadTimePort=0, livePort=65535, deadPausePort=0, livePausePort=0)
    
    Port Val Bits:
    7..0     - User Port 7..0
    15..8    - Extended outputs on VETO/XFER and TFOut3  ( To use as input ports see setupAlternateTrigger)
    
    See Programming from da.server section of the TFg2 User Manual available at:
    
    http://confluence.diamond.ac.uk/display/DATAACQ/TFG2+User+Manual 
    
    for details of arguments
    
    
    
    """
    stop()
    tfg=getTfg()
    tfg.getDaServer().sendCommand("tfg setup-tfout enb-tf3 1") #enable Time Frame Out 3 as output
    tfg.getDaServer().sendCommand("tfg alternate-tf3 lower-mem") #parallel up tf3 output with user output
    # So TF3 bit 3 is memory bit 41 which already drives User Port 1 - port value is 2
    tfg.setAttribute(Tfg.EXT_START_ATTR_NAME, False)
    tfg.setAttribute(Tfg.EXT_INHIBIT_ATTR_NAME, False)
    tfg.setAttribute(Tfg.VME_START_ATTR_NAME, True)
    tfg.setAttribute(Tfg.AUTO_CONTINUE_ATTR_NAME, False)
    tfg.setAttribute(Tfg.AUTO_REARM_ATTR_NAME, False)
    tfg.clearFrameSets()
    tfg.setCycles(cycles)
    tfg.addFrameSet(1, deadTime*1000., liveTime * 1000., deadTimePort, livePort, deadPausePort, livePausePort)
    tfg.loadFrameSets()
    start()


#def sendSimplyTriggerToExcalibur(cycles=10000, deadtime=1, liveTime=1, deadTimePort=0, livePort=127, deadPausePort=0, livePausePort=0):
#    stop()
#    setupAlternateTrigger()