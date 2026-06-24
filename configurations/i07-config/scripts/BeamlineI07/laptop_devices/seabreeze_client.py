from BeamlineI07.laptop_devices.xmlrpc_devices import XmlrpcClientClass

class SeaBreezeClientClass(XmlrpcClientClass):
    """
    Client class for connecting to the seabreeze spectrometer.
    """

    def __init__(self, name, serverURL, port):
        XmlrpcClientClass.__init__(self, serverURL, port)
        self.name = name

    def integration_time_micros(self, time):
        self.server.integration_time_micros(time)

    def wavelengths(self):
        return self.server.wavelengths()

    def intensities(self):
        return self.server.intensities()

def connect_to_seabreeze(serverURL="http://diamrl8056.dc.diamond.ac.uk", useLive=True):
    """
    Connect to the seabreeze spectrometer and return a client to communicate with it.

    This class allows GDA to connect to a windows laptop which can connect to the seabreeze spectrometer.
    To use, first ensure the server class is running on the laptop.  If the seabreeze_server python script is not on the laptop, a copy is at
    /dls_sw/i07/software/gda/config/scripts/BeamlineI07/laptop_devices/seabreeze_server.py.  Copy this file to the laptop and run the scrip inside.
    Then run this method to connect to it.
    """
    sb = SeaBreezeClientClass("sb", serverURL, port=5678)
    sb.connect()
    spec = sb.server.connect(useLive)
    print ("Connected to: " + spec)
    return sb
