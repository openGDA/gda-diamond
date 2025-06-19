from gda.device.scannable import ProcessingScannable
from gda.data import NumTracker
from gdascripts.utils import caget, caput
from time import sleep
from gda.jython.commands.ScannableCommands import scan
from gdaserver import testMotor1

pv_base = "BL07I-CS-IOC-07"
numTracker = NumTracker("scanbase_numtracker")

def currentscan():
    """
    Returns the current scan number
    """
    return int(numTracker.getCurrentFileNumber())

def mapstart():
    """
    clears scanlist and creates a new process scannable
    """
    ps =  ProcessingScannable('ps')
    scanlist=[]
    return scanlist,ps

def mapend(scanlist,ps,setup_paths):
    """
    takes in scanlist, processing scannable (ps), and yamlpath, then sends of dummy scan to start the processing
    """
    scanlistout= str(scanlist).replace(','," ")
    ps['i07-multirsm']=[{'exp_file':setup_paths[0],'calc_file':setup_paths[1],'scans':scanlistout}]
    scan(testMotor1, 1, 1, 1, ps)

def checkzocalo():
    """
    Check that the ioc is running, if not restart it and wait for it to finish restarting.  Will error if the ioc does
    not start in a reasonable time (15s).
    """
    if caget(pv_base + ":STATUS") == "0" : 
        print("Zocalo connection is running.")
        return
    print("Zocalo connection not running, attempting to restart " + pv_base)
    caput(pv_base + ":START", 1)
    for unused in range(15) :
        sleep(1)
        if caget(pv_base + ":STATUS") == "0" :
            print(pv_base + " successfully restarted.")
            caput(pv_base + ":AUTORESTART", 1)
            return
    raise ValueError("IOC for " + pv_base + " is not running and could not be started.")
