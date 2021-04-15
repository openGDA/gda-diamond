from gda.device.scannable import ScannableMotionBase


#This class creates a scannable that can be used to pause scans by being busy.
#example initialisation:
#
#Run this script, then initialise in the jython console with command like below
#
# beamMonitor = simpleBeamMonitor(beamMonitor, d4d2, 100, eh_shutter)


class simpleBeamMonitor(ScannableMotionBase):
    def __init__(self, name, diode, diodeThreshold, shutter):
        self.name = name
        self.setInputNames([])
        self.setExtraNames([])
        self.setOutputFormat([])
        self.diode = diode
        self.shutter = shutter
        self.threshold = diodeThreshold

    def rawGetPosition(self):
        #return self.shutter.getPosition() != "Open" or self.diode.getPosition() < self.threshold
        return

    def rawAsynchronousMoveTo(self,new_position):
        return

    def isBusy(self):
        busy = self.shutter.getPosition() != "Open" or self.diode.getPosition() < self.threshold
        if busy:
            print "no beam or shutter closed"
            sleep(10)
        return busy