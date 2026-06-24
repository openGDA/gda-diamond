from xmlrpclib import ServerProxy

class XmlrpcClientClass(object):
    """
    Client class for connecting to device accessed through the beamline laptop.

    See the seabreeze spectrometer for an example of how this should work, basically there needs to be a server script
    which is run on the laptop for this to connect to.  The script can be stored on to the laptop or run directly from
    this folder (/dls_sw/i07/software/gda/config/scripts/BeamlineI07/laptop_devices/) but if it's on the laptop a copy
    should be kept here in case the laptop dies.
    """

    def __init__(self, serverURL, port):
        self.url = serverURL
        self.port = port
        self.server = None

    def connect(self):
        self.server = ServerProxy(self.url + ":" + str(self.port))

    def close(self):
        self.disconnect()

    def disconnect(self):
        self.server.disconnect()
