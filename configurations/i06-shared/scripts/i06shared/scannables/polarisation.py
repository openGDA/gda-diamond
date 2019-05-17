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
    POLARISATIONS=['pc','nc', 'lh', 'lv', 'la','unknown']
    POLARISATIONS_EPICS={'pc':'PosCirc', 'nc':'NegCirc','lh':'Horizontal','lv':'Vertical','la':'LinArb'}
    
    def __init__(self, name, dpol, drpenergy, dgap, upol, urpenergy, ugap, pgmenergy, smode, offhar, detune=100.0, opengap=100.0, defaultPolarisation='unknown'):
        '''
        Constructor - default polarisation mode is 'pc'
        '''
        self.setName(name)
        self.dpol=dpol
        self.dgap=dgap
        self.upol=upol
        self.ugap=ugap
        self.polarisation=defaultPolarisation
        self.smode=smode
        self.detune=detune
        self.opengap=opengap
        self.drpenergy=drpenergy
        self.urpenergy=urpenergy
        self.pgmenergy=pgmenergy
        self.offhar=offhar
    
    def setOpenGap(self, gap):
        self.opengap=gap
    
    def getOpenGap(self):
        return self.opengap
    
    def setDetune(self, val):
        self.detune=val
        
    def getDetune(self):
        return self.detune
    
    def getPosition(self):
        ''' get current polarisation that has been set last time 
        '''
        mode=str(self.smode.getPosition())
        iddpolarisation=""
        idupolarisation=""
        errmsg=None
        if self.polarisation == Polarisation.POLARISATIONS[5]: #EPICS does not support 'unknown' in polarisation
            return self.polarisation
        if mode == SourceMode.SOURCE_MODES[0]:
            iddpolarisation=str(self.dpol.getPosition())
            if iddpolarisation!=Polarisation.POLARISATIONS_EPICS[self.polarisation]:
                errmsg="demand position %s is different from arrived position for idd %s in mode %s" % (self.polarisation, iddpolarisation, mode)
        elif mode == SourceMode.SOURCE_MODES[1]:
            idupolarisation=str(self.upol.getPosition())
            if idupolarisation!=Polarisation.POLARISATIONS_EPICS[self.polarisation]:
                errmsg="demand position %s is different from arrived position for idu %s in mode %s" % (self.polarisation, idupolarisation, mode)
        elif mode == SourceMode.SOURCE_MODES[2]:
            iddpolarisation=str(self.dpol.getPosition())
            idupolarisation=str(self.upol.getPosition())
            if iddpolarisation!=Polarisation.POLARISATIONS_EPICS[self.polarisation] or idupolarisation!=Polarisation.POLARISATIONS_EPICS[self.polarisation]:
                errmsg="demand position %s is different from arrived positions for idd %s and for idu %s in mode %s" % (self.polarisation, iddpolarisation, idupolarisation, mode)
        elif mode == SourceMode.SOURCE_MODES[3]:
            if self.polarisation == Polarisation.POLARISATIONS[0]:
                iddpolarisation=str(self.dpol.getPosition())
                idupolarisation=str(self.upol.getPosition())
                if iddpolarisation!=Polarisation.POLARISATIONS_EPICS['pc'] or idupolarisation!=Polarisation.POLARISATIONS_EPICS['nc']:
                    errmsg="demand position %s is different from arrived positions for idd %s and for idu %s in mode %s" % (self.polarisation, iddpolarisation, idupolarisation, mode)  
            elif self.polarisation == Polarisation.POLARISATIONS[1]:
                iddpolarisation=str(self.dpol.getPosition())
                idupolarisation=str(self.upol.getPosition())
                if iddpolarisation!=Polarisation.POLARISATIONS_EPICS['pc'] or idupolarisation!=Polarisation.POLARISATIONS_EPICS['nc']:
                    errmsg="demand position %s is different from arrived positions for idd %s and for idu %s in mode %s" % (self.polarisation, iddpolarisation, idupolarisation, mode)  
            elif self.polarisation == Polarisation.POLARISATIONS[2]:
                iddpolarisation=str(self.dpol.getPosition())
                idupolarisation=str(self.upol.getPosition())
                if iddpolarisation!=Polarisation.POLARISATIONS_EPICS['lh'] or idupolarisation!=Polarisation.POLARISATIONS_EPICS['lv']:
                    errmsg="demand position %s is different from arrived positions for idd %s and for idu %s in mode %s" % (self.polarisation, iddpolarisation, idupolarisation, mode)  
            elif self.polarisation == Polarisation.POLARISATIONS[3]:
                iddpolarisation=str(self.dpol.getPosition())
                idupolarisation=str(self.upol.getPosition())
                if iddpolarisation!=Polarisation.POLARISATIONS_EPICS['lh'] or idupolarisation!=Polarisation.POLARISATIONS_EPICS['lv']:
                    errmsg="demand position %s is different from arrived positions for idd %s and for idu %s in mode %s" % (self.polarisation, iddpolarisation, idupolarisation, mode)  
            elif self.polarisation == Polarisation.POLARISATIONS[4]:
                message="Linear Angular Polarisation is not supported in '%s' source mode" % (mode)
                raise RuntimeError(message)
        if errmsg is not None:
            raise RuntimeError(errmsg)
        return self.polarisation
    
    def asynchronousMoveTo(self, newpos):
        '''set polarisation of ID according to source mode.
        '''
        if newpos not in Polarisation.POLARISATIONS:
            message="polarisation string is wrong: legal values are %s" % (Polarisation.POLARISATIONS)
            raise Exception(message)
        mode=self.smode.getPosition()
        offhar=float(self.offhar.getPosition())
        if mode == SourceMode.SOURCE_MODES[0]:
            self.dpol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS[newpos])
            self.ugap.asynchronousMoveTo(self.opengap)
            position = float(self.pgmenergy.getPosition())
            self.drpenergy.asynchronousMoveTo(position+offhar)
        elif mode == SourceMode.SOURCE_MODES[1]:
            self.upol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS[newpos])
            self.dgap.asynchronousMoveTo(self.opengap)
            position = float(self.pgmenergy.getPosition())
            self.urpenergy.asynchronousMoveTo(position+offhar)
        elif mode == SourceMode.SOURCE_MODES[2]:
            self.dpol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS[newpos])
            self.upol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS[newpos])
            position = float(self.pgmenergy.getPosition())
            self.urpenergy.asynchronousMoveTo(position+offhar)
            self.drpenergy.asynchronousMoveTo(position+offhar)
        elif mode == SourceMode.SOURCE_MODES[3]:
            if newpos == Polarisation.POLARISATIONS[0]:
                self.dpol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS['pc'])
                self.upol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS['nc'])
                position = float(self.pgmenergy.getPosition())
                self.drpenergy.asynchronousMoveTo(position+offhar)
                self.urpenergy.asynchronousMoveTo(position+self.detune)
            elif newpos == Polarisation.POLARISATIONS[1]:
                self.upol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS['nc'])
                self.dpol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS['pc'])
                position = float(self.pgmenergy.getPosition())
                self.urpenergy.asynchronousMoveTo(position+offhar)
                self.drpenergy.asynchronousMoveTo(position+self.detune)
            elif newpos == Polarisation.POLARISATIONS[2]:
                self.dpol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS['lh'])
                self.upol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS['lv'])
                position = float(self.pgmenergy.getPosition())
                self.drpenergy.asynchronousMoveTo(position+offhar)
                self.urpenergy.asynchronousMoveTo(position+self.detune)
            elif newpos == Polarisation.POLARISATIONS[3]:
                self.upol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS['lv'])
                self.dpol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS['lh'])
                position = float(self.pgmenergy.getPosition())
                self.urpenergy.asynchronousMoveTo(position+offhar)
                self.drpenergy.asynchronousMoveTo(position+self.detune)
            elif newpos == Polarisation.POLARISATIONS[4]:
                message="Linear Angular Polarisation is not supported in '%s' source mode" % (mode)
                raise RuntimeError(message)
        self.polarisation=newpos
    
    def isBusy(self):
        mode=self.smode.getPosition()
        if mode == SourceMode.SOURCE_MODES[0]:
            return self.dpol.isBusy() or self.ugap.isBusy() or self.drpenergy.isBusy()
        elif mode == SourceMode.SOURCE_MODES[1]:
            return self.upol.isBusy() or self.dgap.isBusy() or self.urpenergy.isBusy()
        elif mode == SourceMode.SOURCE_MODES[2]:
            return self.dpol.isBusy() or self.upol.isBusy() or self.drpenergy.isBusy() or self.urpenergy.isBusy()
        elif mode == SourceMode.SOURCE_MODES[3]:
            #TODO check if need to set both ID or not
            if self.polarisation == Polarisation.POLARISATIONS[0]:
                return self.dpol.isBusy() or self.upol.isBusy() or self.drpenergy.isBusy() or self.urpenergy.isBusy()
            elif self.polarisation == Polarisation.POLARISATIONS[1]:
                return self.upol.isBusy() or self.dpol.isBusy() or self.urpenergy.isBusy() or self.drpenergy.isBusy()
            elif self.polarisation == Polarisation.POLARISATIONS[2]:
                return self.dpol.isBusy() or self.upol.isBusy() or self.drpenergy.isBusy() or self.urpenergy.isBusy()
            elif self.polarisation == Polarisation.POLARISATIONS[3]:
                return self.upol.isBusy() or self.dpol.isBusy() or self.urpenergy.isBusy() or self.drpenergy.isBusy()
            elif self.polarisation == Polarisation.POLARISATIONS[4]:
                message="Linear Angular Polarisation is not supported in '%s' source mode" % (mode)
                raise RuntimeError(message)
        return False

