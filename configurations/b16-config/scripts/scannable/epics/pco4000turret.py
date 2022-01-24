from gda.device.scannable import ScannableBase
from gda.epics import LazyPVFactory
from gda.device import DeviceException

"""
Class for controlling the Objective lens turret for the pcoedge detector
"""
class Turret(ScannableBase):

    POSITIONS = {1: "x4", 2: "x10", 3: "x20"}
    REVERSE_POSITIONS = {v: k for k, v in POSITIONS.iteritems()}

    """The value of the moving PV corresponding to moving"""
    MOVING = 0

    def __init__(self, name, pv_prefix):
        self.setName(name)
        self.setInputNames(["value"])
        self.setExtraNames([])
        self.setOutputFormat(["%s"])
        self.pv_prefix = pv_prefix

        # Only one turret is "in" at a time
        # zero => turret in, one => turret out
        self.position_pvs = {i: LazyPVFactory.newReadOnlyIntegerFromEnumPV(pv_prefix + ":OBJ" + str(i)) for i in Turret.POSITIONS.keys()}
        
        # Left and right are used here to correspond to the Epics screen
        # The device is revolving
        self.move_left_pv = LazyPVFactory.newIntegerFromEnumPV(pv_prefix + ":TWNEG")
        self.move_right_pv = LazyPVFactory.newIntegerFromEnumPV(pv_prefix + ":TWPOS")
        self.moving_left_pv = LazyPVFactory.newReadOnlyIntegerFromEnumPV(pv_prefix + ":NEG")
        self.moving_right_pv = LazyPVFactory.newReadOnlyIntegerFromEnumPV(pv_prefix + ":POS")


    def getPosition(self):
        index = self.getCurrentPositionIndex()
        return Turret.POSITIONS.get(index, "*moving*")

    def getCurrentPositionIndex(self):
        position_values = [i.get() for i in self.position_pvs.values()]
        if sum(position_values) != 2:
            # Currently moving
            return 0
        return position_values.index(0) + 1

    def isBusy(self):
        # Due to the sequencing both of these have to be checked
        # moving PVs transition before the move is complete
        # position PVs take a while before reaching position after moving PV has changed
        moving = any([self.moving_left_pv.get() == Turret.MOVING, self.moving_right_pv.get() == Turret.MOVING])
        # Check position PVs are consistent for completed move (see comment on self.position_pvs)
        positionSettled = sum([i.get() for i in self.position_pvs.values()]) == 2
        return any([moving, not positionSettled])


    def asynchronousMoveTo(self, position):
        try:
            requested_index = Turret.REVERSE_POSITIONS[position]
        except KeyError:
            raise DeviceException("Requested position: " + str(position) + " is not a valid position (valid values: " + str(Turret.POSITIONS.values())  + ")")
        current = self.getCurrentPositionIndex()
        move = (current - requested_index) % 3
        if move == 1:
            self.move_left_pv.putNoWait(1)
        elif move == 2:
            self.move_right_pv.putNoWait(1)
