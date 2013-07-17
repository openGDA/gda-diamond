from uk.ac.gda.exafs.ui.data import EdeScanParameters

energyTable = finder.find("energyTable")

if energyTable != None:
    def getenergies(energyValue):
        return energyTable.getPositionsForEnergy(energyValue)
    alias getenergies
    
from edescan import ede
alias ede

run "roi_control"