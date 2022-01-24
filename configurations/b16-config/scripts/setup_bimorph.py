print "setting up bimorph"
from pd_bimorph import EemBimorph, SixteenChannelEemBimorph #@UnresolvedImport
eembimorph = EemBimorph("eembimorph", 0, 8, "EEM_Bimorph:", sleepInS=0)
eembimorph16 = SixteenChannelEemBimorph("protobimorph", 0, 16, "EEM_Bimorph:", "Spare_8:", sleepInS=0)

#from gdascripts.bimorph.bimorph_mirror_optimising import ScanAborter
#scanAborter = ScanAborter("scanAborter",rc, 100) #@UndefinedVariable

run("bimorph_mirror_optimising.py") #@UndefinedVariable
