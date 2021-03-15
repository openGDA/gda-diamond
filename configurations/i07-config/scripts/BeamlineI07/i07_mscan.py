from gdascripts.mscanHandler import *

exc = getRunnableDeviceService().getRunnableDevice("BL07I-ML-SCAN-01")
m2 = getRunnableDeviceService().getRunnableDevice("BL07I-ML-SCAN-02")
m3 = getRunnableDeviceService().getRunnableDevice("BL07I-ML-SCAN-03")

#mscan testMotor1 axis 0 20 step 1 malc2 1.0

from BeamlineI07.i07_fscan import fscan, fpscan
alias(fscan)
alias(fpscan)