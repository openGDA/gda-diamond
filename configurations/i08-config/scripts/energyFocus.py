# Set the function that maps energy to zone plate position
import json
from os.path import abspath

from gda.configuration.properties import LocalProperties
from gdaserver import energyFocusFunction

# Load values of energy/focus function from stash file
def loadEnergyFocus():
    print("Loading energy/focus parameters")
    stashFilePath = LocalProperties.get("gda.var") + "/energyFocusFunction.json"

    try:
        stashFile = open(stashFilePath, 'r')
        stashedValue = json.load(stashFile)
        stashFile.close()

        slopeDividend = stashedValue.get('slopeDividend')
        interception = stashedValue.get('interception')
        slopeDivisor = stashedValue.get('slopeDivisor')
    except:
        print("Cannot load stored energy focus values from " + abspath(stashFilePath) + ", using defaults")
        slopeDividend = "0.0 um"
        interception = "0.0 um"
        slopeDivisor = "1.0 eV"

    energyFocusFunction.setSlopeDividend(slopeDividend)
    energyFocusFunction.setInterception(interception)
    energyFocusFunction.setSlopeDivisor(slopeDivisor)
    print("energyFocusFunction set to: " + str(energyFocusFunction))


# Load values at startup
loadEnergyFocus()
