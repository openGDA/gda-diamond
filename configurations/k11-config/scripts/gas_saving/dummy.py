from gas_saving.valve import ValveController, Valve
from gda.device import EnumPositionerStatus # @UnresolvedImport
import time


class DummyValveController(ValveController):
    def __init__(self, name):
        self.valve_position = Valve.CLOSE
        self.gas_saving_enabled = True
        self.name = name;

    def move(self, position):
        self.valve_position = position
        time.sleep(1)
        print("%s: %s" % (self.name, position))

    def read(self):
        if self.valve_position == Valve.OPEN:
            return "Open"
        elif self.valve_position == Valve.CLOSE:
            return "Closed"
        else:
            return "Unknown"

    def auto_save_gas(self):
        return self.gas_saving_enabled

    def set_gas_saving(self, enabled):
        self.gas_saving_enabled = enabled
    
    def status(self):
        return EnumPositionerStatus.IDLE



class DummyWaiter:
    """ 
    Waits for the specified time. Interruptible
    """
    
    def __init__(self, wait_time):

        """
        wait_time: waiting time, in seconds
        """
        self.wait_time = wait_time
        
        from threading import Event
        self.gas_ready = Event()
    
    def wait(self):
        self.gas_ready.wait(self.wait_time)
        self.gas_ready.clear()
    
    def stop(self):
        self.gas_ready.set()