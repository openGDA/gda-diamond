from BeamlineI07.laptop_devices.xmlrpc_devices import XmlrpcClientClass

class BladeCoaterClientClass(XmlrpcClientClass):
    """
    Client class for connecting to the blade coater motors.
    """

    def run_move(self, direction, trip=50.0, speed=20.0, accel=100.0, **kw):
        self.server.run_move(direction, trip, speed, accel, **kw)

    def blade_coating(self, trip=50.0, speed=20.0, accel=100.0, **kw):
        self.server.blade_coating(trip, speed, accel, **kw)

def connect_to_blade_coater(serverURL="http://diamrl8056.dc.diamond.ac.uk"):
    """
    Connect to the blade coater script and return a client to communicate with it.

    This class allows GDA to connect to a windows laptop which can control the blade coaters.
    To use, first ensure the server class is running on the laptop.  A copy is at
    /dls_sw/i07/software/gda/config/scripts/BeamlineI07/laptop_devices/blade_coater_server.py.  Copy this file to the laptop and run the script 
    inside.  Then run this method to connect to it.
    """
    bc_client = BladeCoaterClientClass(serverURL, port=8765)
    bc_client.connect()
    return bc_client