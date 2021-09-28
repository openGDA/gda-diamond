from gda.device.scannable import ScannableBase
from gda.epics import LazyPVFactory
from gda.device import DeviceException

"""
Class for controlling the Objective lens turret for the pcoedge detector
"""
class Turret(ScannableBase):
    
    
    POSITIONS = {1: "x4", 2: "x10", 3: "x20"}

    def __init__(self, name, pv_prefix):
        self.setName(name)
        self.setInputNames(["value"])
        self.setExtraNames([])
        self.setOutputFormat(["%s"])
        self.pv_prefix = pv_prefix
        self.position_pvs = {i: LazyPVFactory.newReadOnlyIntegerFromEnumPV(pv_prefix + ":OBJ" + str(i)) for i in Turret.POSITIONS.keys()}
        self.move_left_pv = LazyPVFactory.newIntegerFromEnumPV(pv_prefix + ":TWPOS")
        self.move_right_pv = LazyPVFactory.newIntegerFromEnumPV(pv_prefix + ":TWNEG")
        self.moving_left_pv = LazyPVFactory.newReadOnlyIntegerFromEnumPV(pv_prefix + ":NEG")
        self.moving_right_pv = LazyPVFactory.newReadOnlyIntegerFromEnumPV(pv_prefix + ":POS")


    def getPosition(self):
        return Turret.POSITIONS[self.getCurrentPositionIndex()]

    def getCurrentPositionIndex(self):
        position_values = [i.get() for i in self.position_pvs.values()]
        if sum(position_values) != 2:
            raise DeviceException("Invalid position PVs: " + str(position_values))
        return position_values.index(0) + 1

    def isBusy(self):
        any([self.moving_left_pv.get() == 0, self.moving_right_pv.get() == 0])


    def asynchronousMoveTo(self, position):
        print("aaa")
        if position not in Turret.POSITIONS.values():
            raise DeviceException("Requested position: " + str(position) + " is not a value position (valid values: " + Turret.POSITIONS.values()  + ")")
        requested_index = Turret.POSITIONS.keys()[Turret.POSITIONS.values().index(position)]
        print("bbb")
        current = self.getCurrentPositionIndex()
        if current == 1:
            if requested_index == 2:
                self.move_right_pv.put(1)
                return
            self.move_left_pv.put(1)
            return
        elif current == 2:
            if requested_index == 1:
                self.move_left_pv.put(1)
                return
            self.move_right_pv.put(1)
            return
        else:
            if requested_index == 1:
                self.move_right_pv.put(1)
                return
            self.move_left_pv.put(1)
            return
