from gda.epics import CAClient
from gda.device.scannable import ScannableBase

class EpicsArrayAverageScannable( ScannableBase ):
    def __init__( self, name, pv, typeString = "double" ):
        self.name = name
        self.inputNames = [name]
        self.client = CAClient(pv)
        self.client.configure()
        self.typeString = typeString
        self.arrayGetters = {
            "double":self.client.cagetArrayDouble,
            "unsigned":self.client.cagetArrayUnsigned,
            "byte":self.client.cagetArrayByte}

    def getPosition( self ):
        epicsArray = self.arrayGetters[self.typeString]()
        return sum(epicsArray) / len(epicsArray)
