from xmlrpclib import ServerProxy

class SeaBreezeClientClass(object):
    """
    Client class for connecting to the seabreeze spectrometer.
    """

    def __init__(self, name, serverURL):
        self.name = name
        self.url = serverURL
        self.server = None

    def connect(self, use_live=True):
        self.server = ServerProxy(self.url)
        spec = self.server.connect(use_live)
        print ("Connected to: " + spec)

    def close(self):
        self.disconnect()

    def disconnect(self):
        self.server.disconnect()

    def integration_time_micros(self, time):
        self.server.integration_time_micros(time)

    def wavelengths(self):
        return self.server.wavelengths()

    def intensities(self):
        return self.server.intensities()

def connect_to_seabreeze(serverURL="http://diamrl8056.dc.diamond.ac.uk:5678", useLive=True):
    """
    Connect to the seabreeze spectrometer and return a client to communicate with it.

    This class allows GDA to connect to a windows laptop which can connect to the seabreeze spectrometer.
    To use, first ensure the server class is running on the laptop.  If the seabreeze_server python script is not on the laptop, a copy is at
    /dls_sw/i07/software/gda/config/scripts/BeamlineI07/devices/seabreeze_server.py.  Copy this file to the laptop and run the scrip inside.  Then
    run this method to connect to it.
    """
    sb = SeaBreezeClientClass("sb", serverURL )
    sb.connect(useLive)
    return sb
