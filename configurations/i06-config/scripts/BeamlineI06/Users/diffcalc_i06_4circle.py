# This file's last known position:
#    /dls_sw/i06-1/software/gda/config/scripts/BeamlineI06/Users/diffcalc_i07_4circle.py

# See notes in: http://wiki.diamond.ac.uk/Wiki/Wiki.jsp?page=I06_Diffcalc

try:
    import diffcalc
except ImportError:
    
    from gda.data.PathConstructor import createFromProperty
    import sys
    diffcalc_path = '/dls_sw/i06-1/software/gda/diffcalc'
    #diffcalc_path = createFromProperty("gda.root").split('/plugins')[0] + '/diffcalc' 
    sys.path = [diffcalc_path] + sys.path
    print diffcalc_path + ' added to GDA Jython path.'
    import diffcalc
#####

from diffcalc.gdasupport.GdaDiffcalcObjectFactory import createDiffcalcObjects, addObjectsToNamespace
from gdascripts.pd.dummy_pds import DummyPD

DUMMY_DIFFCALC = False

chi = DummyPD('chi')
phi = DummyPD('phi')

if DUMMY_DIFFCALC:
    print "!!! Staring dummy diffcalc with tth, th, chi, phi and en." 
    tth = DummyPD('tth')
    th = DummyPD('th')
    en = DummyPD('en')
    en(1500)
    diffcalcObjects = createDiffcalcObjects(
        axisScannableList = [tth, th, chi, phi],
        energyScannable = en,
        energyScannableMultiplierToGetKeV = .001,
        geometryPlugin = 'fourc',
        hklverboseVirtualAnglesToReport=('2theta','Bin','Bout','azimuth')
    )
    diffcalcObjects['diffcalcdemo'].commands = []
    addObjectsToNamespace(diffcalcObjects, globals())

else:
    print "!!! Staring LIVE diffcalc with th(dd2th), th(ddth), chi(dummy), phi(dummy) and denergy." 
    tth = dd2th
    th = ddth
    diffcalcObjects = createDiffcalcObjects(
        axisScannableList = [tth, th, chi, phi],
        energyScannable = denergy,
        energyScannableMultiplierToGetKeV = .001,
        geometryPlugin = 'fourc',
        hklverboseVirtualAnglesToReport=('2theta','Bin','Bout','azimuth')
    )
    diffcalcObjects['diffcalcdemo'].commands = []
    addObjectsToNamespace(diffcalcObjects, globals())

hkl.level = 6
