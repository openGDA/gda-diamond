# Allow control of the function that maps energy to zone plate position
import json
from os.path import abspath
from gda.factory import Finder
from gda.configuration.properties import LocalProperties
from gda.jython.commands.GeneralCommands import alias

finder = Finder.getInstance()

# Load values of energy/focus function from stash file
def loadEnergyFocus():
    stashFilePath = LocalProperties.get("gda.var") + "/energyFocusFunction.json"

    try:
        stashFile = open(stashFilePath, 'r')
        stashedValue = json.load(stashFile)
        stashFile.close()

        slopeDividend = stashedValue.get('slopeDividend')
        interception = stashedValue.get('interception')
        slopeDivisor = stashedValue.get('slopeDivisor')
    except:
        print "Cannot load stored energy focus values from " + abspath(stashFilePath) +  ", using defaults"
        slopeDividend = "0.0 um"
        interception = "0.0 um"
        slopeDivisor = "1.0 eV"

    setEnergyFocus(slopeDividend, interception, slopeDivisor)


# Set new parameter values
def setEnergyFocus(slopeDividend, interception, slopeDivisor):
    energyFocusFunction = finder.find("energyFocusFunction")
    energyFocusFunction.slopeDividend = slopeDividend
    energyFocusFunction.interception = interception
    energyFocusFunction.slopeDivisor = slopeDivisor
    print "energyFocusFunction set to: " + str(energyFocusFunction)


# Load values at startup
loadEnergyFocus()
