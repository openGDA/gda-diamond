# Functions to allow easy switching to use Si333 converter in energy scannables
# To replace the manual process described here : https://confluence.diamond.ac.uk/x/gYZGAQ
# 21/5/2024

eV_Deg_converter_Si111=Finder.find("eV_Deg_converter_Si111")
eV_Deg_converter_Si333=Finder.find("eV_Deg_converter_Si333")
eV_Deg_converter_Si311=Finder.find("eV_Deg_converter_Si311")

harmonic1_Si111=Finder.find("harmonic1_Si111")
harmonic3_Si111=Finder.find("harmonic3_Si111")

# [harmonic1 end, harmonic3 start] for each crystal cut
si_333_range=[51.000, 50.999]
si_111_range=[56.187, 56.187]


def setup_for_Si333() :
    print("Setting up harmonic1, 3 converters for Si333 :")
    adjust_harmonic_range(si_333_range)
    adjust_energy_scannables(eV_Deg_converter_Si333)
    
    
def setup_for_Si111() :
    print("Setting up harmonic1, 3 converters for Si111 :")
    adjust_harmonic_range(si_111_range)
    adjust_energy_scannables(eV_Deg_converter_Si111)
    
## Make the Si111 energy scannables using the given (Si333 or Si111) converter 
def adjust_energy_scannables(converter) :
    print("Setting energy scannables to use %s converter :"%(converter.getName()))
    energy_scannables = [energy_Si111,  energy_nogap_Si111, energy_lut, energy_nogap_lut]
    for scn in energy_scannables :
        print("\t"+scn.getName())
        scn.setConvertor(converter)
    
    print("Using %s for Si111 converter in qexafs energy scannable"%(converter.getName()))
    delegates = {"Si311" : eV_Deg_converter_Si311, "Si111" : converter}
    zebraBraggEnergy.setDelegateConverters(delegates)
    
## Adjust the harmonic energy range (end of harmonic1, start of harmonic3
def adjust_harmonic_range(end_start_vals) :
    harm1_end=end_start_vals[0]
    harm3_start=end_start_vals[1]
    print("\tSetting %s end to %f"%(harmonic1_Si111.getName(), harm1_end))
    harmonic1_Si111.setRangeStop(harm1_end)
    
    print("\tSetting %s start to %f"%(harmonic1_Si111.getName(), harm3_start))
    harmonic1_Si111.setRangeStart(harm3_start)

