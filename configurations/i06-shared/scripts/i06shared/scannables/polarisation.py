'''
A single polarisation scannable that controls the polarisation of the X-ray beam.
It defines X-ray polaristion modes ['pc','nc', 'lh', 'lv', 'la'] in GDA only, and 
converts polarisation name between GDA and EPICS control system.

Created on 20 Apr 2017

@author: fy65
'''
from gda.device.scannable import ScannableBase
from i06shared.scannables.sourceModes import SourceMode

class Polarisation(ScannableBase):
    '''
    Scannable to control the polarisation of ID. It provides new simple polarisation names that map onto
    EPICS polarisation names for the ID. 
    '''
    POLARISATIONS=['pc','nc', 'lh', 'lv', 'la']
    POLARISATIONS_EPICS={'pc':'PosCirc', 'nc':'NegCirc','lh':'Horizontal','lv':'Vertical','la':'LinArb'}
    
    def __init__(self, name, dpol, dgap, upol, ugap, smode, detune=3.0, gap=100.0, defaultPolarisation='pc'):
        '''
        Constructor - default polarisation mode is 'pc'
        '''
        self.setName(name)
        self.dpol=dpol
        self.dgap=dgap
        self.upol=upol
        self.ugap=ugap
        self.polaristaion=defaultPolarisation
        self.smode=smode
        self.detune=detune
        self.opengap=gap
        
    def getPosition(self):
        ''' get current polarisation of ID from EPICS driver and 
        return its corresponding GDA polarisation name
        '''
        mode=self.smode.getPosition()
        currentpol=self.polaristaion
        if mode == SourceMode.SOURCE_MODES[0] :
            currentpol=self.dpol.getPosition()
        elif mode == SourceMode.SOURCE_MODES[1]:
            currentpol=self.upol.getPosition()
        elif mode == SourceMode.SOURCE_MODES[2]:
            currentpol=self.dpol.getPosition()
        elif mode == SourceMode.SOURCE_MODES[3]:
            currentpol=self.dpol.getPosition()
            if currentpol==Polarisation.POLARISATIONS_EPICS['la']:
                message="Wrong Polarisation: Linear Angular Polarisation is not supported in '%s' source mode" % (mode)
                raise RuntimeError(message)
        
        self.polaristaion=[key for key, value in Polarisation.POLARISATIONS_EPICS.iteritems() if value == currentpol][0]
        return self.polaristaion
    
    def asynchronousMoveTo(self, newpos):
        '''set polarisation of ID according to source mode.
        '''
        if newpos not in Polarisation.POLARISATIONS:
            message="polarisation string is wrong: legal values are %s" % (Polarisation.POLARISATIONS)
            raise Exception(message)
        mode=self.smode.getPosition()
        if mode == SourceMode.SOURCE_MODES[0]:
            self.dpol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS[newpos])
            self.ugap.asynchronousMoveTo(self.opengap)
        elif mode == SourceMode.SOURCE_MODES[1]:
            self.upol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS[newpos])
            self.dgap.asynchronousMoveTo(self.opengap)
        elif mode == SourceMode.SOURCE_MODES[2]:
            self.dpol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS[newpos])
            self.upol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS[newpos])
        elif mode == SourceMode.SOURCE_MODES[3]:
            #TODO check if need to set both ID or not
            if newpos == Polarisation.POLARISATIONS[0] or newpos == Polarisation.POLARISATIONS[2]:
                self.dpol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS[newpos])
                position = float(self.ugap.getPosition())
                self.ugap.asynchronousMoveTo(position+self.detune)
            elif newpos == Polarisation.POLARISATIONS[1] or newpos == Polarisation.POLARISATIONS[3]:
                self.upol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS[newpos])
                position = float(self.dgap.getPosition())
                self.dgap.asynchronousMoveTo(position+self.detune)
            elif newpos == Polarisation.POLARISATIONS[4]:
                message="Linear Angular Polarisation is not supported in '%s' source mode" % (mode)
                raise RuntimeError(message)
        self.polaristaion=newpos
    
    def isBusy(self):
        return self.dpol.isBusy() or self.dgap.isBusy() or self.upol.isBusy() or self.ugap.isBusy()

