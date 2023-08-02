from gdaserver import fastshutter, fastshutter_fatt

def setShutterDelay(newDelay):
    groupDelay = [1, newDelay]
    fastshutter.setStartValue(groupDelay)
    fastshutter_fatt.setStartValue(groupDelay)
    
alias("setShutterDelay")

from scannable.emergency_beamstop import StopOnFaultScannable
emergency_stopper = StopOnFaultScannable("emergency_stopper",
        ["BL07I-MO-FLITE-01:BEAMSTOP:Y2.SEVR", "BL07I-MO-FLITE-01:BEAMSTOP:Y1.SEVR"],
        fastshutter, 0)
