from gda.device.monitor import EpicsMonitor
from gda.factory import Finder

class photoDiode1Inverted(EpicsMonitor):
    def __init__(self,name):
        self.name = name
        photoDiode1Position= Finder.find("photoDiode1")
        new_position = (photoDiode1Position.getPosition())[0]*(-1)
        print "New position",new_position
        self.currentposition = [new_position]
        
    def getPosition(self):
        #return photoDiode1Position.getPosition()*(-1)
        pass
    