from gda.device.scannable import ScannableMotionBase
from gda.jython.commands import ScannableCommands
from gda.jython.commands.ScannableCommands import pos 
from gda.jython.commands.GeneralCommands import alias, vararg_alias
from gdascripts.utils import caput, caget
from time import sleep
from gdascripts.parameters import beamline_parameters
from gda.factory import Finder



finder = Finder.getInstance()

pixium10_hdf=finder.find("pixium10_hdf")


def pixium10_changeExposure(exposure):
    pixium10_hdf.stop()
    sleep(2)
    pixium10_hdf.setBaseExposure(exposure)
    pixium10_hdf.setBaseAcquirePeriod(exposure)
    pixium10_hdf.calibrate()
    print "pixium10 exposure changed, detector calibrated. Shutter closed"
alias("pixium10_changeExposure")


print "finished loading 'pixium10_changeExposure'"