from pymodbus.client import ModbusSerialClient
import time

PORT, ID = "COM5", 1

REGS  = {0x0006: 3.4, 0x0028: 3.4, 0x0008: 4.4, 0x000A: 4.4, 0x0010: 3.26, 0x0002: 1.0, 0x0004: 1.0}
COILS = {"forward": 0x0002, "backward": 0x0001}

def create_client_to_hardware():
    c = ModbusSerialClient(port=PORT, framer="rtu", baudrate=9600, bytesize=8, parity="N", stopbits=1)
    if not c.connect(): raise ConnectionError("Modbus connection failed")
    return c

def write_reg(c, addr, val):
    c.write_register(addr, int(round(val * REGS[addr])), device_id=ID)

def coil(c, addr, state):
    c.write_coil(addr, state, device_id=ID)

def stop(c):
    for a in COILS.values(): coil(c, a, False)

def move(c, direction, speed=20.0, accel=100.0, trip=50.0, lead=5.0, subdiv=6000.0):
    for addr, val in zip(REGS, [speed, speed, accel, accel, trip, lead, subdiv]):
        write_reg(c, addr, val)
    stop(c)
    coil(c, COILS[direction], True)

def run_move(direction, trip=50.0, speed=20.0, accel=100.0, **kw):
    wait = trip / speed + speed / accel + 0.1
    c = create_client_to_hardware()
    try :
        move(c, direction, speed=speed, accel=accel, trip=trip, **kw)
        time.sleep(wait)
    finally :
        stop(c)
        c.close()
    return True

def blade_coating(trip=50.0, speed=20.0, accel=100.0, **kw):
    wait = trip / speed + speed / accel - 1.0
    c = create_client_to_hardware()
    try :
        move(c, "forward",  speed=speed, accel=accel, trip=trip, **kw); time.sleep(wait)
        move(c, "backward", speed=speed, accel=accel, trip=trip, **kw); time.sleep(wait)
    finally :
        stop(c); c.close()
    return True


from xmlrpc.server import SimpleXMLRPCServer

class BladeCoaterServerClass(object):
    """
    Server class to allow the GDA client to access the blade_coating method defined above.

    This file should be copied on to the beamline laptop and run there, the client
    will then be able to communicate with it from gda on the beamline workstation.
    """

    def __init__(self, port=8765):
        self.port = port
        self.server = SimpleXMLRPCServer(("0.0.0.0", port))
        self.server.register_function(blade_coating, "blade_coating")
        self.server.register_function(run_move, "run_move")

    def serve(self):
        print("Listening on port " + str(self.port) + "...")
        self.server.serve_forever()


bcserver = BladeCoaterServerClass()
bcserver.serve()
