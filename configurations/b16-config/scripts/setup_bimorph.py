print "setting up bimorph"
from gdascripts.bimorph.pd_bimorph import EemBimorph #@UnresolvedImport
eembimorph = EemBimorph("eembimorph", 0, 8, "EEM_Bimorph:", sleepInS=0)

#from gdascripts.bimorph.bimorph_mirror_optimising import ScanAborter
#scanAborter = ScanAborter("scanAborter",rc, 100) #@UndefinedVariable

run("gdascripts/bimorph/bimorph_mirror_optimising.py") #@UndefinedVariable
