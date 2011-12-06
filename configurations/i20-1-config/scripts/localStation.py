energyTable = finder.find("energyTable")

if energyTable != None:
    def getenergies(energyValue):
        return energyTable.getPositionsForEnergy(energyValue)
    alias getenergies