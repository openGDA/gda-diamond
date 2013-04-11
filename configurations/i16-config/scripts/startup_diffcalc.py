from gda.configuration.properties import LocalProperties
print "<<< Entering: startup_diffcalc.py ..."

import sys
diffcalc_path = LocalProperties.get("gda.install.git.loc") + '/diffcalc.git'
sys.path = [diffcalc_path] + sys.path

import diffcalc.hkl.you.geometry
from diffcalc.gdasupport.factory import create_objects, add_objects_to_namespace
from scannable.extraNameHider import ExtraNameHider



from gdascripts.pd.dummy_pds import DummyPD
dummy_energy = DummyPD('dummy_energy')

simple_energy = ExtraNameHider('energy', dummy_energy)  # @UndefinedVariable
# For dummy: del mu, delta, gam, eta, chi, phi  # @UndefinedVariable
demo_commands = []
_tmp_names = list(euler.inputNames)
_tmp_names[2] = 'nu'
euler.inputNames = _tmp_names

diffcalcObjects=create_objects(
    #dummy_axis_names = ['mu', 'delta', 'gam', 'eta', 'chi', 'phi'],
    axes_group_scannable = euler, #@UndefinedVariable
    energy_scannable = simple_energy,
    #dummy_energy_name = 'dummyenergy',
    energy_scannable_multiplier_to_get_KeV = 1,
    geometry = diffcalc.hkl.you.geometry.SixCircle(),
    hklverbose_virtual_angles_to_report=('theta','alpha','beta','psi'),
    demo_commands = demo_commands,
    engine_name = 'you'
    
)

#diffcalcObjects['diffcalcdemo'].commands = demo_commands;
add_objects_to_namespace( diffcalcObjects, globals() )

hkl.setLevel(6) #@UndefinedVariable

#demo_commands.append( "newub 'cubic'" )
#demo_commands.append( "setlat 'cubic' 1 1 1 90 90 90" )
#demo_commands.append( "pos wl 1" )
#demo_commands.append( "pos sixc [0 60 0 30 1 0]" )
#demo_commands.append( "addref 1 0 0" )
#demo_commands.append( "pos chi 91" )
#demo_commands.append( "addref 0 0 1" )
#demo_commands.append( "checkub" )
#demo_commands.append( "ub" )
#demo_commands.append( "hklmode" )

print "... Leaving: startup_diffcalc.py >>>"