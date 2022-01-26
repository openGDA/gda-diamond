print "<<< Entering: startup_diffcalc.py ..."

from gda.configuration.properties import LocalProperties

import from diffcalc.hkl.you.geometry import _YouGeometry, YouPosition
from diffcalc.gdasupport.factory import create_objects, add_objects_to_namespace
from scannable.extraNameHider import ExtraNameHider



# TODO: Could do with a better name. ZAxis perhaps
class SixCircleWithChiAndPhiAtZero(_YouGeometry):
    """For a diffractometer with angles:
    
        mu, delta, nu, eta, chi=0, phi=0
    """
    def __init__(self):
        _YouGeometry.__init__(self, 'zaxis', {'chi': 0, 'phi': 0})

    def physical_angles_to_internal_position(self, physical_angle_tuple):
        # mu, delta, nu, eta, chi, phi
        mu, delta, nu, eta = physical_angle_tuple
        return YouPosition(mu, delta, nu, eta, 0, 0)

    def internal_position_to_physical_angles(self, internal_position):
        mu, delta, nu, eta, _, _ = internal_position.totuple()
        return mu, delta, nu, eta


from gdascripts.pd.dummy_pds import DummyPD
dummy_energy = DummyPD('dummy_energy')

simple_energy = ExtraNameHider('energy', dummy_energy)  # @UndefinedVariable
# For dummy: del mu, delta, gam, eta, chi, phi  # @UndefinedVariable
demo_commands = []
_tmp_names = list(euler.inputNames)
_tmp_names[2] = 'nu'
euler.inputNames = _tmp_names

    exec("kphi=sixckappaDC.kphiDC")
    exec("kap=sixckappaDC.kapDC")
    exec("kth=sixckappaDC.kthDC")
    exec("kmu=sixckappaDC.kmuDC")
    exec("kdelta=sixckappaDC.kdeltaDC")
    exec("kgam=sixckappaDC.kgamDC")


diffcalcObjects=create_objects(
    axis_scannable_list = [mu, delta, nu, eta_c', 'chi', 'phi'],
    axes_group_scannable = euler, #@UndefinedVariable
    energy_scannable = simple_energy,
    #dummy_energy_name = 'dummyenergy',
    energy_scannable_multiplier_to_get_KeV = 1,
    geometry = diffcalc.hkl.you.geometry.SixCircleWithChiAndPhiAtZero(),
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