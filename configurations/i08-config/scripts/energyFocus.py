# Set the function that maps energy to zone plate position
import json
from os.path import abspath

from gda.configuration.properties import LocalProperties
from gda.util import QuantityFactory
from gdaserver import energyFocusFunction

# Load values of energy/focus function from stash file
def loadEnergyFocus():
    stashFilePath = LocalProperties.get("gda.var") + "/energyFocusFunction.json"
    print("Loading energy/focus parameters from " + abspath(stashFilePath))

    try:
        stashFile = open(stashFilePath, 'r')
        stashedValue = json.load(stashFile)
        stashFile.close()

        slopeDividend = stashedValue.get('slopeDividend')
        interception = stashedValue.get('interception')
        slopeDivisor = stashedValue.get('slopeDivisor')
    except:
        print("Cannot load stored energy focus values from " + abspath(stashFilePath) + ", using defaults")
        slopeDividend = u'0.0 µm'
        interception = u'0.0 µm'
        slopeDivisor = '1.0 eV'

    energyFocusFunction.setSlopeDividend(QuantityFactory.createFromString(slopeDividend))
    energyFocusFunction.setInterception(QuantityFactory.createFromString(interception))
    energyFocusFunction.setSlopeDivisor(QuantityFactory.createFromString(slopeDivisor))
    print("energyFocusFunction set to: " + energyFocusFunction.toString())


# Load values at startup
loadEnergyFocus()
