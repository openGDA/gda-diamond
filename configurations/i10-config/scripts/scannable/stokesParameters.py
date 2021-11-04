'''
a Read-only Scannable that converts i06-specific polarisation modes to Stock Parameters.

Created on May 19, 2021

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from calibrations.energy_polarisation_class import X_RAY_POLARISATIONS
import math

pc,nc,lh,lv,la,lh3,unknown = X_RAY_POLARISATIONS
POLPARISATION_DICT = {pc:[1.000, 0.000, 0.000, 1.000], nc:[1.000, 0.000, 0.000, -1.000], lh:[1.000, 1.000, 0.000, 0.000] , lv:[1.000, -1.000, 0.000, 0.000], lh3:[1.000, 1.000, 0.000, 0.000]}

class StokesParameters(ScannableMotionBase):
    '''
    class takes polarisation scannable and linear arbitrary angle and return its corresponding Stock parameters for the polarised beam.
    '''

    def __init__(self, name, pol, laa):
        '''
        Constructor
        @param pol: the polarisation scannable
        @param laa:  the angle in Linear Arbitrary 'la' mode
        '''
        self.setName(name)
        self.setInputNames([])
        self.setExtraNames([pol.getName()])
        self.pol = pol
        self.laa = laa
        
    def getPosition(self):
        try:
            pol = str(self.pol.getPosition())
        except Exception, e:
            return str(e)
        if pol == 'la' :
            try:
                angle = float(self.laa.getPosition())
                S1 = round((math.cos(angle*math.pi/180.0))**2-(math.sin(angle*math.pi/180.0))**2,3)
                S2 = round(2*math.cos(angle*math.pi/180.0)*math.sin(angle*math.pi/180.0),3)
                return [1.000, S1, S2, 0.000]
            except RuntimeError, e:
                if hasattr(e, 'message'):
                    return e.message
                else:
                    return "Problem encountered while get the linear Arbitrary Angle in current source mode."
        elif pol in POLPARISATION_DICT.keys():
            return POLPARISATION_DICT[pol]
        else:
            return pol
        
    def asynchronuousMovtTo(self, npos):
        print("%s is read-only scannable!" % (self.getName()))
            
    def isBusy(self):
        return False
     
    def toFormattedString(self):
        return "%s : %s" % (self.getName(), self.getPosition())
    
           
        