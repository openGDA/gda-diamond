'''
Beam Divergence at the sample position for current beam energy and PGM grating selection.

Created on Jan 14, 2022

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.configuration.properties import LocalProperties
import csv

def load_1key_lookup_table(filename):
    with open(filename) as csv_data:
        reader = csv.reader(csv_data)
        rows = [row for row in reader if row or not row.startswith('#')]
        header = rows[0]

    lookuptable={}
    for row in rows[1:]:
        #print(row)
        lookuptable[row[0]]=[float(item) for item in row[1:]]
    return lookuptable, header


class BeamDivergence(ScannableMotionBase):
    '''
    a scannable provides beam divergence values at a specified position down the X-ray beam.
    '''


    def __init__(self, name, energy_scannable, vpg_scannable, lut="divergence_polynomial_at_sample.csv"):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([''])
        self.setExtraNames(['horizontal', 'vertical'])
        self.energy = energy_scannable
        self.vpg = vpg_scannable
        self.lut,self.header = load_1key_lookup_table(LocalProperties.get("gda.config")+"/lookupTables/"+lut)
        

    def getDivergence(self, energy, coefs):
        return coefs[0] + coefs[1] * energy + coefs[2] * energy ** 2 + coefs[3] * energy ** 3 + coefs[4] * energy ** 4 + coefs[5] * energy ** 5 + coefs[6] * energy ** 6

    def getPosition(self):
        vpg = str(self.vpg.getPosition())
        energy = float(self.energy.getPosition())
        coefs = self.lut[vpg]
        vertical_diversgence = self.getDivergence(energy, coefs)
        h_coefs = self.lut["Horizontal"]
        horizontal_divergence = self.getDivergence(energy, h_coefs)
        return [horizontal_divergence, vertical_diversgence]
    
    def asynchronousMoveTo(self, new_pos):
        print("%s: is a read-only scannable!" % self.getName())
        
    def isBusy(self):
        return False
    
        

        