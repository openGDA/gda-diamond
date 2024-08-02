# Functions to allow easy switching to use Si333 converter in energy scannables
# To replace the manual process described here : https://confluence.diamond.ac.uk/x/gYZGAQ
# 21/5/2024

eV_Deg_converter_Si111=Finder.find("eV_Deg_converter_Si111")
eV_Deg_converter_Si333=Finder.find("eV_Deg_converter_Si333")
eV_Deg_converter_Si311=Finder.find("eV_Deg_converter_Si311")

lookup_name_provider_Si111=Finder.find("lookup_name_provider_Si111")

harmonic1_Si333=Finder.find("harmonic1_Si333")
harmonic1_Si111=Finder.find("harmonic1_Si111")
harmonic3_Si111=Finder.find("harmonic3_Si111")

# [harmonic1 end, harmonic3 start] for each crystal cut
si_333_range=[51.000, 50.999]
si_111_range=[56.187, 56.187]

def get_converter_list(include_333=False) :
    str_format="harmonic%d_Si111"
    si_333="harmonic1_Si333"
    converters = []
    for i in range(1, 24, 2) :
        if include_333 and i == 1 :
            converters.append(si_333)
        else :
            converters.append(str_format%(i))
    return [Finder.find(name) for name in converters]
        
def show_names(findable_list) :
    print [f.getName() for f in findable_list]

def setup_converters(include_333=False) :
    print("Setting up converter list in lookup_name_provider_Si111 :")
    converters_list = get_converter_list(include_333)
    show_names(converters_list)
    lookup_name_provider_Si111.setConverters(converters_list)

def setup_for_Si333() :
    print("Setting up harmonic1 and harmonic13 converters for Si333 :")
    setup_converters(include_333=True)
    adjust_harmonic_range(si_333_range, include_333=True)
    adjust_energy_scannables(eV_Deg_converter_Si333)
    print("Done!\n")
    
def setup_for_Si111() :
    print("Setting up harmonic1 and harmonic1 converters for Si111 :")
    setup_converters(include_333=False)
    adjust_harmonic_range(si_111_range, include_333=False)
    adjust_energy_scannables(eV_Deg_converter_Si111)
    print("Done!\n")

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
def adjust_harmonic_range(end_start_vals, include_333) :
    harm1_end=end_start_vals[0]
    harm3_start=end_start_vals[1]
    harmonic1 = harmonic1_Si333 if include_333 else harmonic1_Si111
    print("\tSetting %s end to %f"%(harmonic1.getName(), harm1_end))
    harmonic1.setRangeStop(harm1_end)
    
    print("\tSetting %s start to %f"%(harmonic3_Si111.getName(), harm3_start))
    harmonic3_Si111.setRangeStart(harm3_start)


