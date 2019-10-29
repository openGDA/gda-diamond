print "<<< Entering: startup_diffcalc.py ..."
import diffcalc.hkl.you.geometry
from diffcalc.hkl.you.geometry import YouPosition, YouGeometry
from diffcalc.gdasupport.factory import create_objects, add_objects_to_namespace
from gdascripts.pd.dummy_pds import DummyPD
from scannable.extraNameHider import ExtraNameHider

dummy_energy = DummyPD('dummy_energy')
simple_energy = ExtraNameHider('energy', dummy_energy)  # @UndefinedVariable


class SixCircleI16(YouGeometry):
    def __init__(self):
        diffcalc.hkl.you.geometry.YouGeometry.__init__(self, 'sixc', {})

    def physical_angles_to_internal_position(self, physical_angle_tuple):
        #    i16:   phi, chi, eta, mu, delta, gam
        # H. You:   mu, delta, nu, eta, chi, phi
        phi, chi, eta, mu, delta, gam = physical_angle_tuple     
        return YouPosition(mu, delta, gam, eta, chi, phi)

    def internal_position_to_physical_angles(self, internal_position):
        mu, delta, nu, eta, chi, phi = internal_position.totuple()
        return phi, chi, eta, mu, delta, nu


diffcalcObjects=create_objects(
    axes_group_scannable = euler,  # @UndefinedVariable
    energy_scannable = simple_energy,
    energy_scannable_multiplier_to_get_KeV = 1,
    geometry = SixCircleI16(),
    hklverbose_virtual_angles_to_report=('theta','alpha','beta','psi'),
    demo_commands = [],
    engine_name = 'you'
)

add_objects_to_namespace( diffcalcObjects, globals() ) #@UndefinedVariable
hkl.setLevel(6) #@UndefinedVariable

setmin(chi, -2)
setmax(chi, 100)
setmin(eta, -2)
setmax(eta, 92)
setmin(delta, -2)
setmax(delta, 179)
setmin(gam, -2)
setmax(gam, 179)

setcut(phi, -180)

print "... Leaving: startup_diffcalc.py >>>"