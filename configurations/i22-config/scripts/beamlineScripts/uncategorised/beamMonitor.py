from gda.device.scannable import PseudoDevice


#This class creates a scannable that can be used to pause scans by being busy.
#example initialisation:
#
#Run this script, then initialise in the jython console with command like below
#
# beamMonitor = simpleBeamMonitor(beamMonitor, d4d2, 100, eh_shutter)


class simpleBeamMonitor(PseudoDevice):
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

    def rawIsBusy(self):
        busy = self.shutter.getPosition() != "Open" or self.diode.getPosition() < self.threshold
        if busy:
            print "no beam or shutter closed"
            sleep(10)
        return busy