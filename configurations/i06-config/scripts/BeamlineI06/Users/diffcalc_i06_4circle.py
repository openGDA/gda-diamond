# See notes in: http://wiki.diamond.ac.uk/Wiki/Wiki.jsp?page=I06_Diffcalc

try:
    import diffcalc
except ImportError:
    from gda.configuration.properties import LocalProperties
    import sys
    diffcalc_path = LocalProperties.get("gda.install.git.loc") + '/diffcalc.git'
    sys.path = [diffcalc_path] + sys.path
    print diffcalc_path + ' added to GDA Jython path.'
    import diffcalc

from gdascripts.pd.dummy_pds import DummyPD
from diffcalc.gdasupport.factory import create_objects, add_objects_to_namespace

CREATE_DUMMY_AXES = False
if CREATE_DUMMY_AXES:
    print "!!! Staring dummy diffcalc with tth, th, chi, phi and en." 
    tth = DummyPD('tth')
    th = DummyPD('th')
    en = DummyPD('en')
    en(1500)
    diffcalc_energy=en
else:
    print "!!! Staring LIVE diffcalc with th(dd2th), th(ddth), chi(dummy), phi(dummy) and denergy." 
    tth = dd2th
    th = ddth
    diffcalc_energy=denergy

chi = DummyPD('chi')
phi = DummyPD('phi')

diffcalcObjects = create_objects(
    axis_scannable_list = [tth, th, chi, phi],
    energy_scannable = diffcalc_energy,
    energy_scannable_multiplier_to_get_KeV = .001,
    geometry = 'fourc',
    hklverbose_virtual_angles_to_report=('2theta','Bin','Bout','azimuth')
)

#demoCommands = []
#diffcalcObjects['diffcalcdemo'].commands = demoCommands
add_objects_to_namespace(diffcalcObjects, globals())

hkl.level = 6
