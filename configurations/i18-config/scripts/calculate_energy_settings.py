from gda.util import QuantityFactory 

class DcmEnergyConverters:
    """
    Functions to use lookup tables to get DCM Bragg angle, perp_converter and ID gap settings.
    """
    def __init__(self, bragg_converter, perp_converter, name_prov, auto_id_gap):
        self.bragg_converter = bragg_converter
        self.perp_converter = perp_converter
        self.name_prov = name_prov
        self.id_gap_converter = auto_id_gap
    
    # create 'quantity' object for the value and unit
    def get_quantity(self, val, unit):
        return QuantityFactory.createFromTwoStrings(str(val), unit)

    def get_bragg(self, energy_ev):
        """Return DCM Bragg angle (degrees) for given photon energy (ev) """
        return self.bragg_converter.toTarget(self.get_quantity(energy_ev, "eV")).getValue()

    def get_perp(self, bragg_angle_deg):
        """Return DCM perp (mm) for given Bragg angle (degrees) """
        return self.perp_converter.toTarget(self.get_quantity(bragg_angle_deg, "deg")).getValue()
    
    def get_undulator_gap(self, bragg_angle_deg, enable_autoconversion=True) :
        """Return undulator gap (mm) for given Bragg angle (degrees) """

        # extract the Si111, Si333 part from the end of the converter name
        conv_name = self.id_gap_converter.getName()
        ind = conv_name.find("Si")
        nice_name = conv_name[ind:] if ind > 0 else conv_name
        
        quant = self.get_quantity(bragg_angle_deg, "deg")
        
        #Store current value of autoconversion setting (i.e. harmonic switching setting).
        orig = self.id_gap_converter.isAutoConversion()
        try:
            if enable_autoconversion is not None:
                print("Setting harmonic switching to {}".format(enable_autoconversion))
                self.id_gap_converter.setAutoConversion(enable_autoconversion)
            id_gap = self.id_gap_converter.toTarget(quant).getValue()
        finally:
            # restore original switching continuousParametersbehaviour
            self.id_gap_converter.setAutoConversion(orig)
        
        # Get the name of the table that was used to lookup to ID gap value :    
        converter_name = self.name_prov.getConverterName()
        
        print("\nCrystal cut : %s\nBragg angle : %.5f deg\nLookup table : %s\nId gap : %.5f mm\n"%(nice_name, bragg_angle_deg, converter_name, id_gap))
        return id_gap
    
    def get_energy_values(self, energy_ev, allow_harmonic_switching=True):
        """
        Return DCM Bragg angle (deg), DCM perp_converter (mm) and id gap (mm) for given energy (ev) for Si311
        Parameters :
        energy_ev : energy in eV
        allow_harmonic_switching - set to True to enable switching between harmonics for the energy change,
                                set to false to disable it.
                            (Default is to leave autoconversion setting at its current value on the auto_mDeg_idGap_mm_converter object).
        Returns:
            Bragg angle (deg), DCM perp (mm) and id_gap (mm)
        
        """
        bragg_angle_deg = self.get_bragg(energy_ev)
        perp = self.get_perp(bragg_angle_deg)
        gap = self.get_undulator_gap(bragg_angle_deg, enable_autoconversion=allow_harmonic_switching)
        return bragg_angle_deg, perp, gap

# Lookup converter scannables and create DcmEnergyConverters for Si311 and Si111 :

lookup_name_provider_Si111 = Finder.find("lookup_name_provider_Si111")
auto_mDeg_idGap_mm_converter_Si111=Finder.find("auto_mDeg_idGap_mm_converter_Si111")
Deg_dcm_perp_mm_converter_Si111 = Finder.find("Deg_dcm_perp_mm_converter_Si111")

converters_Si111 = DcmEnergyConverters(eV_Deg_converter_Si111, Deg_dcm_perp_mm_converter_Si111, lookup_name_provider_Si111, auto_mDeg_idGap_mm_converter_Si111) 

lookup_name_provider_Si311 = Finder.find("lookup_name_provider_Si311")
auto_mDeg_idGap_mm_converter_Si311=Finder.find("auto_mDeg_idGap_mm_converter_Si311")
Deg_dcm_perp_mm_converter_Si311 = Finder.find("Deg_dcm_perp_mm_converter_Si311")

converters_Si311 = DcmEnergyConverters(eV_Deg_converter_Si311, Deg_dcm_perp_mm_converter_Si311, lookup_name_provider_Si311, auto_mDeg_idGap_mm_converter_Si311)   
