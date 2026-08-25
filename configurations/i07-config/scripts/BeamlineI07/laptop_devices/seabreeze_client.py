from BeamlineI07.laptop_devices.xmlrpc_devices import XmlrpcClientClass
from gdascripts import installation
from __main__ import i07
from gda.device.detector import DetectorBase
import scisoftpy as dnp
import os

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

    def get_bins_count(self):
        return self.server.get_bins_count()

def connect_to_seabreeze(serverURL="http://diamrl8056.dc.diamond.ac.uk", useLive=True, verbose=True):
    """
    Connect to the seabreeze spectrometer and return a client to communicate with it.

    This class allows GDA to connect to a windows laptop which can connect to the seabreeze spectrometer.
    To use, first ensure the server class is running on the laptop.  If the seabreeze_server python script is not on the laptop, a copy is at
    /dls_sw/i07/software/gda/config/scripts/BeamlineI07/laptop_devices/seabreeze_server.py.  Copy this file to the laptop and run the scrip inside.
    Then run this method to connect to it.
    """
    sbcc = SeaBreezeClientClass("sbcc", serverURL, port=5678)
    sbcc.connect()
    spec = sbcc.server.connect(useLive)
    if(verbose) : print ("Connected to: " + spec)
    return sbcc

class SeabreezeDetector(DetectorBase):

    def __init__(self, name, live=True):
        self.setLevel(100)
        self.setName(name)
        self.live = live
        self.bin_count = 4096 #Workaround for dummy mode, use get_bins_count in getDataDimensions on live (untested)
        self.is_collecting = False
        self.frame_count = 0

    def atScanStart(self):
        self.frame_count = 0
        if not os.path.exists(i07.getDataPath() + "/spectra"):
                os.mkdir(i07.getDataPath() + "/spectra")

    def createsOwnFiles(self):
        return True

    def collectData(self):
        #Does nowt, collection  is in readout method
        self.frame_count += 1

    def readout(self):
        self.is_collecting = True
        
        sbc = connect_to_seabreeze(useLive=self.live, verbose=not self.live)
        sbc.integration_time_micros(1000000*self.getCollectionTime())
        w = dnp.array(sbc.wavelengths())
        i = dnp.array(sbc.intensities())
        sbc.close()
        
        self.is_collecting = False
        
        dnp.plot.line(w, i, name="Plot 1")
        filename = i07.getDataPath() + '/spectra/' + str(i07.getScanNumber()) + '_' + str(self.frame_count) + '.dat'
        dnp.io.save(filename, dnp.concatenate((w, i)).reshape((2, -1)).transpose(), 'text')
        
        if not self.live:
            print("Total " +str(dnp.sum(i)) +", peak " +str(i.max()) +" at wavelength " +str(w[i.argmax()]))

        return filename

    def getStatus(self):
        return 0 #Never busy

sb = SeabreezeDetector("sb") #To debug with seatease, add False as a parameter here.