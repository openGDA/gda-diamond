from gdascripts.utils import caget, caput
from gda.jython.commands.ScannableCommands import add_default
from gda.device.scannable import ScannableMotionBase

class PilNumRestoreClass(ScannableMotionBase):
    def __init__(self, name):
        self.setName(name)
        self.setInputNames([])
        self.setExtraNames([])
        self.setOutputFormat([])

        # how many Pilatuses we have
        self.pils = 3
        # minimum file number to believe
        self.minfilenumber = 100000
        self.init()

    def init(self):
        self.n = []
        for i in range(0, self.pils):
            nextn = int(caget("BL07I-EA-PILAT-0" + str(i+1) + ":CAM:FileNumber"))
            if nextn < self.minfilenumber:
                print "Warning: pil" + str(i+1) + " file number set to " + str(nextn) + ", please set to correct value in EPICS"
            self.n.append(nextn)

    def isBusy(self):
        return False;

    def asynchronousMoveTo(self,new_position):
        pass

    def getPosition(self):
        pass

    def getPositionString(self):
        return self.positionString;

    def atScanStart(self):
        self.restore()

    def atScanEnd(self):
        self.restore()

    def stop(self):
        self.restore()

    def atCommandFailure(self):
        self.restore()        

    def restore(self):
        for i in range(0, self.pils):
            nextn = int(caget("BL07I-EA-PILAT-0" + str(i+1) + ":CAM:FileNumber"))
            # check if the new image number is too low
            if nextn < self.minfilenumber:
                # if new number is too low and saved number was OK, restore saved number, else give a warning
                if self.n[i] >= self.minfilenumber:
                    caput("BL07I-EA-PILAT-0" + str(i+1) + ":CAM:FileNumber", self.n[i])
                else:
                    print "Warning: pil" + str(i+1) + " file number set to " + str(nextn) + ", could not restore correct value, please set in EPICS"
            else:
                # if new number is OK, save this as the new value
                if nextn > self.n[i]:
                    self.n[i] = nextn

pilNumRestore=PilNumRestoreClass("pilNumRestore")
add_default([pilNumRestore])
