from gda.configuration.properties import LocalProperties
from gda.device.scannable import ScannableBase
from lookup.SGMLookup import sgmLookup
from lookup.twoKeysLookupTable import loadLookupTable
from scisoftpy.nexus.nxclasses import NXbeam_stop

class SGMKinematicsClass(ScannableBase):
    '''Coupled scannable with one input 'sgmpitch' or sgmalpha but drive 4 additional axis of motions - 
        1. L - detector distance to the sample
        2. sgmr1 - distance between sgm and sample;
        3. H - detector height above the sample height
        4 gamma - detector angle to the horizontal plain.
    
        This class implements SGM kinematics in 2 lookup tables - one for each grating selection - 
        to determine the additional positional parameters from inputs and vice verser.
        
        This algorithm requires the position of 'energy' and grating 'smgx' to determine 
        the correct spectrometer parameters for the additional 4 motions.

        The referenced scannables must exist in jython's root or __main__ namespace prior to 
        any method call of this class instance.
        '''
        
    def __init__(self, name, energy, sgmpitch, sgmgrating, sgmr1, specx,specz, specgamma, sgmalphalimits=[87.4,88.7], gratinglines=["SVLS1","SVLS2"], Llimits=[10321,15521], r1limits=[1500,3000], Hlimits=[900,2510], gammalimits=[9.9,39.5], lut=["SLVS1-SGM.txt","SLVS2-SGM.txt"], dry_run=True):
        '''Constructor - Only succeed if it find the lookupTable table, otherwise raise exception.'''
        self.lut=lut
        self.energy=energy
        self.sgmpitch=sgmpitch
        self.sgmgrating=sgmgrating
        self.sgmr1=sgmr1
        self.specx=specx
        self.specz=specz
        self.specgamma=specgamma
        self.sgmlookup=None
        self.sgmalphaLimits=sgmalphalimits
        self.gratingLines=gratinglines
        self.LLimits=Llimits
        self.r1Limits=r1limits
        self.HLimits=Hlimits
        self.gammaLimits=gammalimits
        self.dry_run=dry_run
        self.setName(name)
        self.setLevel(5)
        self.setOutputFormat(["%10.6f","%10.6f","%10.6f","%10.6f","%10.6f"])
        self.setInputNames([name])
        self.setExtraNames([sgmr1.getName(), specx.getName(), specz.getName(), specgamma.getName()])
        self.GRATING_LINE=None
        self.demandingValues=[None,None,None,None,None]
        
    def setDryRun(self, b):
        self.dry_run=b
    
    def isDryRun(self):
        return self.dry_run
    
    def showLookupTable(self):
        if (self.sgmgrating.getPosition()==self.gratingLines[0]):
            lookup_file=LocalProperties.get("gda.config")+"/lookupTables/"+self.lut[0]
        elif (float(self.sgmgrating.getPosition())-self.gratingLines[1])<self.POSITION_TOLERANCE:
            lookup_file=LocalProperties.get("gda.config")+"/lookupTables/"+self.lut[1]
        else:
            raise ValueError("SGM is not at supported grating lines: %s" % (self.gratingLines))
        load_lookup_table = loadLookupTable(lookup_file)
        formatstring="%12s\t%12s\t%12s\t%12s\t%12s\t%12s"
        print (formatstring % ("energy (eV)", "sgmalpha (deg)", "r1 (mm)", "L (mm)", "H (mm)", "gamma (deg)"))
        for key, value in load_lookup_table.items():
            print (formatstring % (key[0],key[1],value[0],value[1], value[2],value[3]))
    
    def whichGrating(self):
        return self.GRATING_LINE
    
    def updateLookupTable(self):
        if (self.sgmgrating.getPosition()==self.gratingLines[0]):
            lookup_file=LocalProperties.get("gda.config")+"/lookupTables/"+self.lut[0]
            self.GRATING_LINE=self.lut[0]
        elif (float(self.sgmgrating.getPosition())-self.gratingLines[1])<self.POSITION_TOLERANCE:
            lookup_file=LocalProperties.get("gda.config")+"/lookupTables/"+self.lut[1]
            self.GRATING_LINE=self.lut[1]
        else:
            raise ValueError("SGM is not at supported grating lines: %s" % (self.gratingLines))
            self.GRATING_LINE=None
        self.sgmlookup=sgmLookup("sgmlookup", lut=lookup_file, lookupindex=[0,1], returnindex=[2,3,4,5], numberOfHeaderLines=2)
        
    def rawGetPosition(self):
        '''returns the current motor positions.'''
        if not self.dry_run:
            sgmalpha=float(self.sgmpitch.getPosition())
            r1 = float(self.sgmr1.getPosition())
            L = float(self.specx.getPosition())
            H = float(self.specz.getPosition())
            gamma = float(self.sgmgamma.getPosition())
            return [sgmalpha, r1, L, H, gamma]
        else:
            return self.demandingValues
        
    def rawAsynchronousMoveTo(self, new_position):
        '''move spectrometer motion axis to the position determined by the input for new_sgmalpha at current beam energy and grating selection.
        '''
        new_sgmalpha=float(new_position)
        #ensure demand value fall within the lookup table's coverage
        if new_sgmalpha < self.sgmalphaLimits[0] or new_sgmalpha > self.sgmalphaLimits[1]:
            limits=','.join(map(str,self.sgmalphaLimits))
            raise ValueError("Input value: %f is outside the allowable limits [ %s ] in the lookup table." % (new_sgmalpha, limits))
        #get current beam energy    
        beam_energy=float(self.energy.getPosition())
        #enable lookup table or switch the lookup table if Grating lines changed
        if self.sgmlookup == None or self.sgmgrating.getPosition()!= self.GRATING_LINE:
            self.updateLookupTable()
            
        [r1, L, H, gamma]=self.sgmlookup.getLR1HGamma(beam_energy, new_sgmalpha, delta=[5, 0.1], interpolationMethod='linear')
        # ensure values returned from lookup table fall within axis limits before send the motion request down to EPICS
        if r1 < self.r1Limits[0] or r1 > self.r1Limits[1]:
            limits=','.join(map(str,self.r1Limits))
            raise ValueError("r1 = %f falls outside the allowable limits [ %s ]" % (r1, limits))
        if L < self.LLimits[0] or L > self.LLimits[1]:
            limits=','.join(map(str,self.LLimits))
            raise ValueError("L = %f falls outside the allowable limits [ %s ]" % (L, limits))
        if H < self.HLimits[0] or H > self.HLimits[1]:
            limits=','.join(map(str,self.HLimits))
            raise ValueError("H = %f falls outside the allowable limits [ %s ]" % (H, limits))
        if gamma < self.gammaLimits[0] or gamma > self.gammaLimits[1]:
            limits=','.join(map(str,self.gammaLimits))
            raise ValueError("gamma = %f falls outside the allowable limits [ %s ]" % (gamma, limits))
        if not self.dry_run:
            self.specx.asynchronousMoveTo(L)
            self.specz.asynchronousMoveTo(H)
            self.specgamma.asynchronousMoveTo(gamma)
            self.sgmr1.asynchronousMoveTo(r1)
            self.sgmpitch.asynchronousMoveTo(new_sgmalpha)
        else:
            self.demandingValues=[new_sgmalpha, r1, L, H, gamma]
        
    def isBusy(self):
        if not self.dry_run:
            return self.specx.isBusy() or self.specz.isBusy() or self.specgamma.isBusy() or self.sgmr1.isBusy() or self.sgmpitch.isBusy()
        else:
            return False
    
    def atScanStart(self):
        #enable lookup table or switch the lookup table if Grating lines changed
        if self.sgmlookup == None or self.sgmgrating.getPosition()!= self.GRATING_LINE:
            self.updateLookupTable()
        
    def atScanEnd(self):
        pass

import __main__#@UnresolvedImport
__main__.sgmalpha=SGMKinematicsClass("sgmalpha", __main__.energy, __main__.sgmpitch, __main__.sgmGratingSelect, __main__.sgmr1, __main__.specl, __main__.spech, __main__.specgamma, sgmalphalimits=[87.4,88.7], gratinglines=["SVLS1","SVLS2"], Llimits=[10321,15521], r1limits=[1500,3000], Hlimits=[900,2510], gammalimits=[9.9,39.5], lut=["SLVS1-SGM.txt","SLVS2-SGM.txt"])

