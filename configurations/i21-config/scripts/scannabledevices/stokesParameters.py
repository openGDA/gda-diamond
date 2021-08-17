'''
a Read-only Scannable that converts i21-specific polarisation modes to Stokes Parameters.

Created on August 09, 2021

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
import math
from calibration.energy_polarisation_class import X_RAY_POLARISATIONS
import numbers

LH, LV, CR, CL, LH3, LV3, LH5, LV5, LAN, LAP = X_RAY_POLARISATIONS
POLPARISATION_DICT = {CR:[1.000, 0.000, 0.000, 1.000],
                      CL:[1.000, 0.000, 0.000, -1.000],
                      LH:[1.000, 1.000, 0.000, 0.000],
                      LH3:[1.000, 1.000, 0.000, 0.000],
                      LH5:[1.000, 1.000, 0.000, 0.000],
                      LV:[1.000, -1.000, 0.000, 0.000],
                      LV3:[1.000, -1.000, 0.000, 0.000],
                      LV5:[1.000, -1.000, 0.000, 0.000]
                      }


class StokesParameters(ScannableMotionBase):
    '''
    class takes polarisation scannable and linear arbitrary angle and return its corresponding Stock parameters for the polarised beam.
    '''
    def __init__(self, name, pol):
        '''
        Constructor
        @param pol: the polarisation scannable
        '''
        self.setName(name)
        self.setInputNames([])
        self.setExtraNames([pol.getName()])
        self.pol = pol

    def getPosition(self):
        pol = self.pol.getPosition()
        if isinstance(pol, numbers.Number):
            try:
                angle = float(pol)
                S1 = round((math.cos(angle * math.pi / 180.0)) ** 2 - (math.sin(angle * math.pi / 180.0)) ** 2, 3)
                S2 = round(2 * math.cos(angle * math.pi / 180.0) * math.sin(angle * math.pi / 180.0), 3)
                return [1.000, S1, S2, 0.000]
            except RuntimeError as e:
                if hasattr(e, 'message'):
                    return e.message
                else:
                    return "Problem encountered while get the linear Arbitrary Angle in current source mode."
        else:
            return POLPARISATION_DICT[pol]

    def asynchronuousMovtTo(self, npos):
        print("%s is read-only scannable!" % (self.getName()))

    def isBusy(self):
        return False

    def toFormattedString(self):
        return "%s : %s" % (self.getName(), self.getPosition())

