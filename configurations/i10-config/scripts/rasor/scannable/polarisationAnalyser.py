"""
Polarisation Analyser scannable for use with GDA at Diamond Light Source
"""
from math import sin, asin, pi
from gda.device.scannable import ScannableMotionBase

class Multilayer(object):
    
    def __init__(self, name, d_spacing_A, energy_start_eV, energy_stop_eV, thp_offset_deg, pos_z_mm, pos_y_mm):
        self.name = name
        self.d_spacing_A = d_spacing_A
        self.energy_start_eV = energy_start_eV
        self.energy_stop_eV = energy_stop_eV
        self.thp_offset_deg = thp_offset_deg
        # It would also be useful to have ttp_offset
        self.pos_z_mm = pos_z_mm
        self.pos_y_mm = pos_y_mm

    def get_titles(self):
        return "Position", "D spacing", "Start Energy", "Stop Energy", "THP Offset", "PZ pos", "PY pos"
    
    def get_units(self):
        return "", "(A)", "(eV)", "(eV)", "(deg)", "(mm)", "(mm)"

    def get_values(self):
        return self.name, self.d_spacing_A, self.energy_start_eV, self.energy_stop_eV, self.thp_offset_deg, self.pos_z_mm, self.pos_y_mm
    
    def __repr__(self):
        return "Multilayer(name=%r, d_spacing_A=%r, energy_start_eV=%r, energy_stop_eV=%r, thp_offset_deg=%r, pos_z_mm=%r, pos_y_mm=%r)" % (self.get_values())

class MultilayerSelectorScannable(ScannableMotionBase):
    
    def __init__(self, name, multilayer_list, pz_scannable, py_scannable):
        self.name = name
        self.multilayer_list = multilayer_list
        self.pz_Scannable = pz_scannable
        self.py_Scannable = py_scannable
        
        self.multilayer_dict = {}
        for multilayer in multilayer_list:
            self.multilayer_dict[multilayer.name]=multilayer

        self.inputNames = ['edge']
        self.extraNames = ['d_spacing_A']
        self.outputFormat = ['%s', '%f']

    def __str__(self):
        # Show string form of the object (use for listing all options
        # with the selected one starred)
        d = ["MultiLayerSelector %s:" % self.name]
        try:
            position = self._getPositionerValue()
        except Exception, e:
            position = ''
            d.append("%s" % e)
        #multilayer_sortedlist = list(self.multilayer_list).sort()
        multilayer_sortedlist = self.multilayer_list
        # Build up the table of values as an array of tuples
        t=[("Selected", )+multilayer_sortedlist[0].get_titles()]
        t.append(("", )+multilayer_sortedlist[0].get_units())
        for multilayer in multilayer_sortedlist:
            selected = ("*" if multilayer.name == position else "")
            t.append((selected, )+multilayer.get_values())

        lens=[] # Calculate the width of each column
        for row in t:
            for i in range(len(row)):
                if i >= len(lens):
                    lens.append(0) 
                if lens[i] < len(str(row[i])):
                    lens[i] = len(str(row[i]))
        seperator = tuple('-'*len for len in lens) 
        t.insert(2,seperator)
        t.append(seperator)

        for row in t:
            d.append(" ".join((str(field).rjust(len) for (field,len) in zip(row,lens))))

        return "\n".join(d)
                
    def __repr__(self):
        return "MultilayerSelectorScannable(%r, %r, %r, %r)" % (self.name,
            [multilayer for multilayer in self.multilayer_list],
            #self.pz_Scannable, self.py_Scannable)
            self.pz_Scannable.name, self.py_Scannable.name)
            #repr(self.pz_Scannable.name), repr(self.py_Scannable.name) )

    def isBusy(self):
        return self.pz_Scannable.isBusy() or self.py_Scannable.isBusy()
    
    def asynchronousMoveTo(self, edge):
        if type(edge) == int:
            multilayer=self.multilayer_list[edge]
        else:
            multilayer=self.multilayer_dict[edge]
        self.pz_Scannable.asynchronousMoveTo(multilayer.pos_z_mm)
        self.py_Scannable.asynchronousMoveTo(multilayer.pos_y_mm)
        
    def _getPositionerValue(self):
        for multilayer in self.multilayer_list:
            if self.py_Scannable.isAt(multilayer.pos_y_mm) and self.pz_Scannable.isAt(multilayer.pos_z_mm):
                return multilayer.name

        raise Exception("Error! (%s,%s) in unknown position (%s,%s)" %
            (self.pz_Scannable.name, self.py_Scannable.name,
             self.pz_Scannable.getPosition(), self.py_Scannable.getPosition()))

    def getPosition(self):
        current = self.multilayer_dict[self._getPositionerValue()]
        return current.name, current.d_spacing_A

    def getDSpacing_A(self):
        return self.multilayer_dict[self._getPositionerValue()].d_spacing_A
    
    def getThetaOffset_deg(self):
        return self.multilayer_dict[self._getPositionerValue()].thp_offset_deg
        
    def getEnergyLimit_eVs(self):
        current = self.multilayer_dict[self._getPositionerValue()]
        return current.energy_start_eV, current.energy_stop_eV
 
class PolarisationAnalyser(ScannableMotionBase):
    
    def __init__(self, name, thp_scannable, ttp_scannable, multilayer_selector_scannable, energy_scannable):
        self.name = name
        self.thp_scannable = thp_scannable
        self.ttp_scannable = ttp_scannable
        self.multilayer_selector_scannable = multilayer_selector_scannable
        self.energy_scannable = energy_scannable
        
        self.deg_per_rad = 180/pi
        # hc = h (Planck's constant in keV.s) * c (Speed of light in Angstrom/s)
        #           h =  4.13566733(10) e-18 keV.s
        #           c =  2.99792458 e+18 A/s
        #          hc = 12.3974187(3) KeV.A
        self.hc_keV_A = 12.39842
        
        self.inputNames = ['energy_keV']
        self.extraNames = ['thp', 'ttp', 'mls']
        self.outputFormat = ['%f', '%f', '%f', '%s']
        
    def __str__(self):
        return "energy_keV=%s, thp=%s, ttp=%s, mls=%s" % self.getPosition()

    def __repr__(self):
        return "PolarisationAnalyser(%r, %r, %r, %r, %r)" % (self.name,
            self.thp_scannable.name, self.ttp_scannable.name,
            self.multilayer_selector_scannable.name, self.energy_scannable.name)
    
    def isBusy(self):
        return self.thp_scannable.isBusy() or self.ttp_scannable.isBusy()
    
    def _getDSpacing_A(self):
        return self.multilayer_selector_scannable.getDSpacing_A()
    
    def _getThpOffset_deg(self):
        return self.multilayer_selector_scannable.getThetaOffset_deg()
    
    def _getEnergyLimit_eVs(self):
        return self.multilayer_selector_scannable.getEnergyLimit_eVs()

    def asynchronousMoveTo(self, energy_eV):
        #print type(energy_eV), energy_eV
        
        if energy_eV == 0:
            energy_keV = self.energy_scannable.getPosition()/1000
        else:
            energy_keV = float(energy_eV)/1000
        
        (min_energy_eV, max_energy_eV)=self._getEnergyLimit_eVs()
        
        if min_energy_eV/1000 > energy_keV or energy_keV/1000 > max_energy_eV:
            raise Exception("Error! Energy (%s, %s) is outside limits %s, %s" %
                            (energy_eV, energy_keV, min_energy_eV, max_energy_eV))
             
        # Photon energy:      E = hc / lambda
        #            so: labmda = hc / E 
        wavelength_A = self.hc_keV_A/energy_keV # in Angstroms
        # Braggs law: n.lambda = 2d sin(theta)
        #         so:    theta = arcsin(n.lambda/2d)
        sin_theta = wavelength_A/(2.*self._getDSpacing_A())
        theta_deg = asin(sin_theta) * self.deg_per_rad
        self.thp_scannable.asynchronousMoveTo(theta_deg + self._getThpOffset_deg())
        self.ttp_scannable.asynchronousMoveTo(2.*theta_deg)
        
    def getPosition(self):
        # Braggs law: n.lambda = 2d sin(theta)
        #         so: assume n=1 for getPosition() 
        ttheta_deg = self.ttp_scannable.getPosition()
        #print ttheta_deg, self._getDSpacing_A(), sin((ttheta_deg/2.)/self.deg_per_rad) 
        wavelength_A = 2*self._getDSpacing_A()*sin((ttheta_deg/2.)/self.deg_per_rad)
        # Photon energy:      E = hc / lambda
        energy_keV = self.hc_keV_A / wavelength_A
        #print wavelength_A, energy_keV
        return (energy_keV, self.thp_scannable.getPosition(),
                ttheta_deg, self.multilayer_selector_scannable.getPosition()[0])
