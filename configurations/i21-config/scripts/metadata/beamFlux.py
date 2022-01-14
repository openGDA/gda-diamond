'''
Beam flux at sample position for current beam energy and PGM grating selection.

Created on Jan 14, 2022

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.configuration.properties import LocalProperties
from metadata.beamDivergence import load_1key_lookup_table

class BeamFlux(ScannableMotionBase):
    '''
    a scannable provides beam flux values at a specified position down the X-ray beam.
    '''

    def __init__(self, name, energy_scannable, vpg_scannable, lut="flux_polynomial_at_sample.csv"):
        '''
        scannable that provides beam flux value at a specific position down the beam line.
        '''
        self.setName(name)
        self.setInputNames([''])
        self.setExtraNames(['flux'])
        self.energy = energy_scannable
        self.vpg = vpg_scannable
        self.lut,self.header = load_1key_lookup_table(LocalProperties.get("gda.config")+"/lookupTables/"+lut)
        
    def getPosition(self):
        vpg = str(self.vpg.getPosition())
        energy = float(self.energy.getPosition())
        coefs = self.lut[vpg]
        flux = coefs[0] + coefs[1] * energy + coefs[2] * energy ** 2 + coefs[3] * energy ** 3 + coefs[4] * energy ** 4 + coefs[5] * energy ** 5 + coefs[6] * energy ** 6
        return flux
    
    def asynchronousMoveTo(self, new_pos):
        print("%s: is a read-only scannable!" % self.getName())
        
    def isBusy(self):
        return False
    
        

        