from time import sleep
"""
    Purpose: read BL05I-DI-PHDGN-07:DET:IAV, i.e. averaged over 50 ms current of amplifier d7current
"""

    
class DcurrentAV(ScannableMotionBase):

    def __init__(self, name):
        self.setName(name)
        self.setInputNames([name])
        self.setOutputFormat(["%5.5g"])
        self.setLevel(7)
        self.caD7IAV = CAClient("BL05I-DI-PHDGN-07:DET:IAV")
        self.caD7IAV.configure()

    def isBusy(self):
        return False

    def getPosition(self):
        return self.caD7IAV.caget()

    def asynchronousMoveTo(self,newPosition):
        return 0

d7current_iav = DcurrentAV("d7current_iav")
