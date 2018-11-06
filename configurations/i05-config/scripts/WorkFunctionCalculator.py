"""Script to create a work function calculator and insert it into the
namespace"""

from uk.ac.gda.devices.vgscienta import WorkFunctionProvider
import csv
from gda.device import Scannable
from gda.device.scannable.scannablegroup import ScannableGroup


class WorkFunctionCalculator(WorkFunctionProvider):
    """
    Class to calculate a work function when given a photon energy.
    The function is then added to the Jython namespace to be used
    on the beamline and is also used to provide the value to the 
    uk.ac.gda.devices.vgscienta.VGScientaAnalyserCamOnly class
    """

    def __init__(self):
        """
        Read in the parameters from the csv file on object instantiation
        """
        self.read_parameters()


    def read_parameters(self):
        """
        Reads in parameters from a lookup table.
        """
        self.p =[]
        try:
            csvfile = open('/dls_sw/i05/scripts/beamline/work_function_lookup.csv', 'rb')
        except OSError as e:
            print "Opening csv file failed.", e
            raise
        else:
            with csvfile:
                reader = csv.reader(csvfile)
                self.p = [float(i) for i in list(reader)[1]]

    def getWorkFunction(self, energy):
        """Returns the work function when given an energy"""
        if (isinstance(energy, Scannable)
            and not isinstance(energy, ScannableGroup)):
            energy = energy.getPosition()

        return self.p[0]+self.p[1]*energy+self.p[2]*energy**2+self.p[3]*energy**3+self.p[4]*energy**4
