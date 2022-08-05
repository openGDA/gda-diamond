'''
A combined energy and polarisation scannable that controls both energy and polarisation of the X-ray beam at the same time.
It moves X-ray energy and polaristion concurrently.

Created on 19 July 2022

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from i06shared.scannables.sourceModes import SourceMode
from i06shared.scannables.polarisation import Polarisation
import numbers

class CombinedEnergyPolarisation(ScannableMotionBase):
    '''
    Scannable to control both energy and polarisation of ID concurrently with off harmonic and detune applied.
    '''
    
    def __init__(self, name, dpol, drpenergy, dgap, upol, urpenergy, ugap, pgmenergy, smode, pol, offhar, detune=100.0, opengap=100.0):
        '''
        Constructor - create a combined energy polarisation scannable'
        '''
        self.setName(name)
        self.setInputNames(['energy', 'pol'])
        self.dpol = dpol
        self.drpenergy = drpenergy
        self.dgap = dgap
        self.upol = upol
        self.urpenergy = urpenergy
        self.ugap = ugap
        self.pgmenergy = pgmenergy
        self.smode = smode
        self.offhar = offhar
        self.detune = detune
        self.opengap = opengap
        self.polarisation = str(pol.getPosition())
    
    def setOpenGap(self, gap):
        self.opengap = gap
    
    def getOpenGap(self):
        return self.opengap
    
    def setDetune(self, val):
        self.detune = val
        
    def getDetune(self):
        return self.detune
    
    def getPosition(self):
        ''' get current energy and polarisation that has been set last time 
        '''
        mode = str(self.smode.getPosition())
        energy = float(self.pgmenergy.getPosition())
        iddpolarisation = ""
        idupolarisation = ""
        errmsg=None
        if self.polarisation == Polarisation.POLARISATIONS[5]: #EPICS does not support 'unknown' in polarisation
            return energy, self.polarisation
        if mode == SourceMode.SOURCE_MODES[0]:
            iddpolarisation = str(self.dpol.getPosition())
            if iddpolarisation != Polarisation.POLARISATIONS_EPICS[self.polarisation]:
                errmsg = "demand position %s is different from arrived position for idd %s in mode %s" % (self.polarisation, iddpolarisation, mode)
        elif mode == SourceMode.SOURCE_MODES[1]:
            idupolarisation = str(self.upol.getPosition())
            if idupolarisation != Polarisation.POLARISATIONS_EPICS[self.polarisation]:
                errmsg = "demand position %s is different from arrived position for idu %s in mode %s" % (self.polarisation, idupolarisation, mode)
        elif mode == SourceMode.SOURCE_MODES[2]:
            iddpolarisation = str(self.dpol.getPosition())
            idupolarisation = str(self.upol.getPosition())
            if iddpolarisation != Polarisation.POLARISATIONS_EPICS[self.polarisation] or idupolarisation!=Polarisation.POLARISATIONS_EPICS[self.polarisation]:
                errmsg = "demand position %s is different from arrived positions for idd %s and for idu %s in mode %s" % (self.polarisation, iddpolarisation, idupolarisation, mode)
        elif mode == SourceMode.SOURCE_MODES[3]:
            iddpolarisation = str(self.dpol.getPosition())
            idupolarisation = str(self.upol.getPosition())
            if self.polarisation in Polarisation.POLARISATIONS[0:2]:
                if iddpolarisation != Polarisation.POLARISATIONS_EPICS['pc'] or idupolarisation != Polarisation.POLARISATIONS_EPICS['nc']:
                    errmsg = "demand position %s is different from arrived positions for idd %s or for idu %s in mode %s" % (self.polarisation, iddpolarisation, idupolarisation, mode)  
            elif self.polarisation in Polarisation.POLARISATIONS[2:4]:
                if iddpolarisation != Polarisation.POLARISATIONS_EPICS['lh'] or idupolarisation != Polarisation.POLARISATIONS_EPICS['lv']:
                    errmsg = "demand position %s is different from arrived positions for idd %s or for idu %s in mode %s" % (self.polarisation, iddpolarisation, idupolarisation, mode)  
            elif self.polarisation == Polarisation.POLARISATIONS[4]:
                errmsg = "Linear Angular Polarisation is not supported in '%s' source mode" % (mode)
        if errmsg is not None:
            raise RuntimeError(errmsg)
        return energy, self.polarisation
    
    def asynchronousMoveTo(self, newpos):
        '''set energy and polarisation of ID according to source mode.
        '''
        args =  list(newpos)
        if len(newpos) != 2:
            raise ValueError("%s: Expect 2 arguments but got %s" % (self.getName(), len(args)))
        if isinstance(args[0], numbers.Number):
            new_energy = float(args[0]) #range validation is done later
        else:
            raise ValueError("1st input for energy must be a number")
        if isinstance(args[1], basestring):
            new_polarisation = str(args[1])
            if not new_polarisation in Polarisation.POLARISATIONS[:-1]:
                raise ValueError("Input value must be one of valid polarisation mode: %s" % str(Polarisation.POLARISATIONS[:-1]) )
        else:
            raise ValueError("2nd input for polarisation must be string")
                   
        mode = self.smode.getPosition()
        offhar = float(self.offhar.getPosition())
        if mode == SourceMode.SOURCE_MODES[0]:
            self.drpenergy.asynchronousMoveTo(new_energy + offhar)
            self.dpol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS[new_polarisation])
            self.ugap.asynchronousMoveTo(self.opengap)
        elif mode == SourceMode.SOURCE_MODES[1]:
            self.urpenergy.asynchronousMoveTo(new_energy + offhar)
            self.upol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS[new_polarisation])
            self.dgap.asynchronousMoveTo(self.opengap)
        elif mode == SourceMode.SOURCE_MODES[2]:
            self.drpenergy.asynchronousMoveTo(new_energy + offhar)
            self.urpenergy.asynchronousMoveTo(new_energy + offhar)
            self.dpol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS[new_polarisation])
            self.upol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS[new_polarisation])
        elif mode == SourceMode.SOURCE_MODES[3]:
            if newpos == Polarisation.POLARISATIONS[0]:
                self.drpenergy.asynchronousMoveTo(new_energy + offhar)
                self.urpenergy.asynchronousMoveTo(new_energy + self.detune)
                self.dpol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS['pc'])
                self.upol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS['nc'])
            elif newpos == Polarisation.POLARISATIONS[1]:
                self.drpenergy.asynchronousMoveTo(new_energy + self.detune)
                self.urpenergy.asynchronousMoveTo(new_energy + offhar)
                self.dpol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS['pc'])
                self.upol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS['nc'])
            elif newpos == Polarisation.POLARISATIONS[2]:
                self.drpenergy.asynchronousMoveTo(new_energy + offhar)
                self.urpenergy.asynchronousMoveTo(new_energy + self.detune)
                self.dpol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS['lh'])
                self.upol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS['lv'])
            elif newpos == Polarisation.POLARISATIONS[3]:
                self.drpenergy.asynchronousMoveTo(new_energy + self.detune)
                self.urpenergy.asynchronousMoveTo(new_energy + offhar)
                self.dpol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS['lh'])
                self.upol.asynchronousMoveTo(Polarisation.POLARISATIONS_EPICS['lv'])
            elif newpos == Polarisation.POLARISATIONS[4]:
                message="Linear Angular Polarisation is not supported in '%s' source mode" % (mode)
                raise RuntimeError(message)
        self.polarisation=newpos
        self.pgmenergy.asynchronousMoveTo(new_energy)
    
    def isBusy(self):
        mode=self.smode.getPosition()
        if mode == SourceMode.SOURCE_MODES[0]:
            return self.dpol.isBusy() or self.ugap.isBusy() or self.drpenergy.isBusy() or self.pgmenergy.isBusy()
        elif mode == SourceMode.SOURCE_MODES[1]:
            return self.upol.isBusy() or self.dgap.isBusy() or self.urpenergy.isBusy() or self.pgmenergy.isBusy()
        elif mode == SourceMode.SOURCE_MODES[2]:
            return self.dpol.isBusy() or self.upol.isBusy() or self.drpenergy.isBusy() or self.urpenergy.isBusy() or self.pgmenergy.isBusy()
        elif mode == SourceMode.SOURCE_MODES[3]:
            return self.dpol.isBusy() or self.upol.isBusy() or self.drpenergy.isBusy() or self.urpenergy.isBusy() or self.pgmenergy.isBusy()
        return False

