import sys
from time import sleep
from gda.device.scannable import ScannableMotionBase
#import gda.factory.Finder as Finder
from gda.device.scannable.scannablegroup import ScannableGroup
from gda.configuration.properties import LocalProperties


class BeamEnergy(ScannableMotionBase):
    
    def __init__(self, name, qcmharmonic, qcmenergy, qcmbragg1, qcmdummygap, idgap):
        self.setName(name)
        self.inputNames=[name]
        self.setOutputFormat(["%10.6f"])    # precision?
        self.setLevel(3)    #?
        
        self.qcmharmonic_delegate = qcmharmonic
        self.qcmenergy_delegate = qcmenergy
        self.qcmbragg1_delegate = qcmbragg1
        self.qcmdummygap_delegate = qcmdummygap     # that's EPICS dummy, not GDA!
        self.idgap_delegate = idgap
        
        self._qcmenergy_demand_keV = None
        self._busy = False
        
        self._configure()
    
    def _configure(self):
        self.qcmenergy_min_keV = 6.48   # exc
        self.qcmenergy_max_keV = 43.4   # exc 
        
        self.idgap_min = 6.15   # inc ?
        self.idgap_max = 29.0   # inc ?
        
        self._delegate_lst = []
        self._delegate_lst.append(("qcmharmonic", self.qcmharmonic_delegate))   # add min max?
        self._delegate_lst.append(("qcmenergy", self.qcmenergy_delegate))
        self._delegate_lst.append(("qcmbragg1", self.qcmbragg1_delegate))
        self._delegate_lst.append(("qcmdummygap", self.qcmdummygap_delegate))
        self._delegate_lst.append(("idgap", self.idgap_delegate))
        
        self._qcmenergy_table_lst = []
        # self._qcmenergy_table_lst.append((lo_lim, hi_lim, harmonic))
        self._qcmenergy_table_lst.append((16.8, 43.4, 13))
        self._qcmenergy_table_lst.append((14.3, 36.7, 11))
        self._qcmenergy_table_lst.append((11.7, 30.1, 9))
        self._qcmenergy_table_lst.append((9.07, 23.4, 7))
        self._qcmenergy_table_lst.append((6.48, 16.7, 5))
    
    def report_harmonic_energy_ranges(self):
        print("%s\t%s\t%s" %("Min Energy (keV)", "Max Energy (keV)", "Harmonic"))
        #keys=[int(key) for key in self.lut.keys()]
        #for key in sorted(keys):
        #    print ("%8.0d\t%10.2f\t%10.2f" % (key,self.lut[key][2],self.lut[key][3]))
        for each in self._qcmenergy_table_lst:
            lo_lim = each[0]
            hi_lim = each[1]
            h = each[2]
            print("%.3f\t%.3f\t%d" %(lo_lim, hi_lim, h))
    
    def rawGetPosition(self):
        energy_keV = self.qcmenergy_delegate.getPosition()
        return energy_keV;

    def get_harmonic_from_energy(self, energy_keV):
        h = caget('BL13J-OP-BEAM-01:ENERGY:HARMONIC')
        if energy_keV > self.qcmenergy_min_keV and energy_keV < self.qcmenergy_max_keV:
            if energy_keV > 16.8 and energy_keV < 43.4:
                h = 13
            elif energy_keV > 14.3 and energy_keV < 36.7:
                h = 11
            elif energy_keV > 11.7 and energy_keV < 30.1:
                h = 9
            elif energy_keV > 9.07 and energy_keV < 23.4:
                h = 7
            elif energy_keV > 6.48 and energy_keV < 16.7:
                h = 5
        else:
            print "FAILED - requested energy %.3f (keV) is outside the allowable interval [%.3f, %.3f] keV!" %(self.energy_keV, self.qcmenergy_min_keV, self.qcmenergy_max_keV)
        return h

    def rawAsynchronousMoveTo(self, new_position):
        self._qcmenergy_demand_keV = float(new_position)
        if (self._qcmenergy_demand_keV > self.qcmenergy_min_keV) and (self._qcmenergy_demand_keV < self.qcmenergy_max_keV):
            print("Getting harmonic for energy %.3f (keV)..." %(self._qcmenergy_demand_keV))
            self.harmonic_val = self.get_harmonic_from_energy(self._qcmenergy_demand_keV)
            print("Got harmonic %d" %(self.harmonic_val))
            
            print("Moving harmonic to %d..." %(self.harmonic_val))
            self.qcmharmonic_delegate.moveTo(self.harmonic_val)
            
            print("Moving qcm_energy to %.3f..." %(self._qcmenergy_demand_keV))
            self.qcmenergy_delegate.moveTo(self._qcmenergy_demand_keV)
            
            print("Reading the new value of qcm_bragg1...")
            self.bragg1_val = self.qcmbragg1_delegate.getPosition()
            print("qcm_bragg1 found at position %.3f (deg)" %(self.bragg1_val))
            
            print("Reading the new value of qcm_dummy_gap...")
            self.dummygap_val = self.qcmdummygap_delegate.getPosition()
            print("qcm_dummy_gap found at position %d" %(self.dummygap_val))
            
            print("Moving id_gap to the new gap value %.3f..." %(self.dummygap_val))
            if (self.dummygap_val >= self.idgap_min) and (self.dummygap_val <= self.idgap_max):
                self.idgap_delegate.moveTo(self.dummygap_val)
                print("Finished moving id_gap to the new gap value %.3f!" %(self.dummygap_val))
                print("Current id_gap positioned at %.3f" %(self.idgap_delegate.getPosition()))
            else:
                if self.dummygap_val < self.idgap_min:
                    print "FAILED - required value of ID gap, %.3f, is smaller than the MIN allowable value %.3f!" %(self.dummygap_val, self.idgap_min)
                if self.dummygap_val > self.id_gap_max:
                    print "FAILED - required value of ID gap, %.3f, is larger than the MAX allowable value %.3f!" %(self.dummygap_val, self.idgap_max)
        else:
            print "FAILED - requested energy %.3f (keV) is outside the allowable interval [%.3f, %.3f] keV!" %(self.energy_reqd_keV, self.qcmenergy_min_keV, self.qcmenergy_max_keV)
    
               
    def isBusy(self):    # what dtype?
        self._busy = False
        for each in self._delegate_lst:
            try:
                self._busy |= each.isBusy()     # is dtype compatible for this binary op?
            except:
                print each.getName() + " isBusy() throws exception ", sys.exc_info()
                raise
        return self._busy
    

    def toString(self):
        '''formats what to print to the terminal console.'''
        out = self.name + " : " + str(self.rawGetPosition()) # add more?
        return out
    
   

