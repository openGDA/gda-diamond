from xmlrpc.server import SimpleXMLRPCServer

class SeaBreezeServerClass(object):
    """
    Server class to connect to seabreeze spectrometer.  See also seabreeze_client.SeaBreezeClientClass

    This file should be copied on to the laptop on which the seabreeze software is installed and run there, the client
    will then be able to communicate with it from gda on the beamline workstation.
    """

    def __init__(self, name, port=5678):
        self.name = name
        self.port = port
        self.spec = None
        self.integration_time = 1000000
        self.server = SimpleXMLRPCServer(("0.0.0.0", port))
        self.server.register_function(self.connect, "connect")
        self.server.register_function(self.disconnect, "disconnect")
        self.server.register_function(self.integration_time_micros, "integration_time_micros")
        self.server.register_function(self.wavelengths, "wavelengths")
        self.server.register_function(self.intensities, "intensities")

    def serve(self):
        print("Listening on port " + str(self.port) + "...")
        self.server.serve_forever()

    def connect(self, use_live=True):
        if use_live :
            import seabreeze.spectrometers as sb
        else :
            import seatease.spectrometers as sb
        self.spec = sb.Spectrometer.from_first_available()
        self.spec.integration_time_micros(self.integration_time)
        return str(self.spec)

    def disconnect(self):
        self.spec.close()
        return True

    def integration_time_micros(self, time):
        self.integration_time = time
        if self.spec:
            self.spec.integration_time_micros(self.integration_time)
        return True

    def wavelengths(self):
        return self.spec.wavelengths().tolist()

    def intensities(self):
        return self.spec.intensities().tolist()

sbserver = SeaBreezeServerClass("sbserver")
sbserver.serve()
