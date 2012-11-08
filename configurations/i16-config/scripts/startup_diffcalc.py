print "<<< Entering: startup_diffcalc.py ..."

import sys
import gda.data.PathConstructor
diffcalc_path = gda.data.PathConstructor.createFromProperty("gda.root").split('/plugins')[0] + '/diffcalc'
sys.path = [diffcalc_path] + sys.path
import diffcalc
from diffcalc.external.GdaDiffcalcObjectFactory import createDiffcalcObjects, addObjectsToNamespace
from scannable.extraNameHider import ExtraNameHider



from EulerianKconversionModes import EulerianKconversionModes
EKCM = EulerianKconversionModes()
mode e2k 1



from diffractometer.scannable.EulerKappa import EulerKappa
euler = EulerKappa('euler',sixckappaDC)
phi = euler.phi; chi = euler.chi; eta = euler.eta; mu  = euler.mu; delta= euler.delta; gam = euler.gam

simple_energy = ExtraNameHider('energy', energy)

demoCommands = []
#demoCommands.append( "newub 'cubic'" )
#demoCommands.append( "setlat 'cubic' 1 1 1 90 90 90" )
#demoCommands.append( "pos wl 1" )
#demoCommands.append( "pos sixc [0 60 0 30 1 0]" )
#demoCommands.append( "addref 1 0 0" )
#demoCommands.append( "pos chi 91" )
#demoCommands.append( "addref 0 0 1" )
#demoCommands.append( "checkub" )
#demoCommands.append( "ub" )
#demoCommands.append( "hklmode" )

diffcalcObjects=createDiffcalcObjects(
                                      
    axesGroupScannable = euler,
    energyScannable = simple_energy,
    energyScannableMultiplierToGetKeV = 1,
    geometryPlugin = 'sixc',
    hklverboseVirtualAnglesToReport=('2theta','alpha','beta','psi'),
    demoCommands = demoCommands
)


diffcalcObjects['diffcalcdemo'].commands = demoCommands;
addObjectsToNamespace( diffcalcObjects, globals() )



hkl.setLevel(6)
print "... Leaving: startup_diffcalc.py >>>"