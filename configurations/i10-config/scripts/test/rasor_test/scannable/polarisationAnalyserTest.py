"""
Unit tests for Polarisation Analyser scannable for use with GDA at Diamond Light Source
"""

import unittest
from mock import Mock

""" ============================================================================
This test module suffers from a problem when run as an Eclipse Jython unit-test,
where including Java projects (or maybe mixed Java/Jython projects?) in Jython
projects (sometimes?) causes only Java source paths to be added to the Python
path, but not the paths to the compiled Java code which seems to be needed by
Jython.

This means that importing GDA's Java base classes fails in the module to be
tested.

Note that in order to get this script to be able to import from rasor.scannable.
polarisationAnalyser, I had to add 'i10config/scripts' to the source folders in
i10config, Properties, PyDev - PYTHONPATH.
      
Also, in order to get this to work, I had to add uk.ac.gda.core as a project
reference in i10config.
============================================================================ """
    
''' (1) RobW's original hack, which had to be in polarisationAnalyser.py 
# Create a dummy ScannableMotionBase to 'inherit' from.
try:
    from gda.device.scannable import ScannableMotionBase
except ImportError:
    ScannableMotionBase = object
'''

''' (2) Manual PythonPath hack
import gda  # Fails without uk.gda.core
import gda.device # Fails without one of uk.gda.devices.*
import gda.device.scannable # Fails even with all projects referenced
'''
from gda.device.scannable import ScannableMotionBase
"""
In order to get this to work, I had to add hard coded paths to External
libraries, in i10config, Properties, PyDev - PYTHONPATH:
        '/scratch/gda/i10/trunk/plugins/uk.ac.gda.core/classes/main'
        '/scratch/gda/i10/trunk/plugins/uk.ac.gda.nexus/bin'
    Note:
        When doing this, don't commit these changes to .pydevproject
"""

''' (3) Automatic PythonPath hack
import java
try:
    from gda.device.scannable import ScannableMotionBase

except java.lang.NoClassDefFoundError:
    import sys, pprint
    pprint.pprint(sys.path)
    print "----------------------- Modifying path -----------------------"
    sys.path.insert(1, "/scratch/gda/i10/trunk/plugins/uk.ac.gda.core/classes/main")
    sys.path.insert(1, "/scratch/gda/i10/trunk/plugins/uk.ac.gda.nexus/bin")
    pprint.pprint(sys.path)
    from gda.device.scannable import ScannableMotionBase
'''
"""
This was my attempt at a hack to do (2) by modifying the sys.path at runtime.
This also required uk.ac.gda.nexus as a referenced project. Alas, it kept giving
me a "NoClassDefFoundError: java.lang.NoClassDefFoundError:
gda/data/nexus/INeXusInfoWriteable" so I had to abandon the attempt.
"""

""" ======================================================================== """

from rasor.scannable.polarisationAnalyser import Multilayer, MultilayerSelectorScannable, PolarisationAnalyser

class MultilayerTest(unittest.TestCase):
    
    def setUp(self):
        self.multilayer = Multilayer('a', 1, 10, 20, 1.23, 0, 0)

    def tearDown(self):
        pass

    def testSetup(self):
        multilayer = Multilayer(name='a', d_spacing_A=1, energy_start_eV=10, energy_stop_eV=20, thp_offset_deg=1.23, pos_z_mm=0, pos_y_mm=0)
        self.assertEquals(repr(self.multilayer), repr(multilayer))
        
    def test__str__(self):
        self.assertEquals(str(self.multilayer), "Multilayer(name='a', d_spacing_A=1, energy_start_eV=10, energy_stop_eV=20, thp_offset_deg=1.23, pos_z_mm=0, pos_y_mm=0)")

    def test__repr__(self):
        self.assertEquals(repr(self.multilayer), "Multilayer(name='a', d_spacing_A=1, energy_start_eV=10, energy_stop_eV=20, thp_offset_deg=1.23, pos_z_mm=0, pos_y_mm=0)")

    def testGetTitles(self):
        self.assertEquals(self.multilayer.get_titles(), ('Position', 'D spacing', 'Start Energy', 'Stop Energy', 'THP Offset', 'PZ pos', 'PY pos'))

    def testGetUnits(self):
        self.assertEquals(self.multilayer.get_units(), ('', '(A)', '(eV)', '(eV)', '(deg)', '(mm)', '(mm)'))

    def testGetValues(self):
        self.assertEquals(self.multilayer.get_values(), ('a', 1, 10, 20, 1.23, 0, 0))
        
    ''' We should be able to assert that "ml == eval(repr(ml))", but
        assertEquals seems to compare references, so we have to repr
        again to verify that the eval and repr are equivalent. '''
    def testEvalRepr(self):
        #print repr(self.multilayer)
        #self.assertEquals(self.multilayer, eval(repr(self.multilayer)))
        self.assertEquals(repr(self.multilayer), repr(eval(repr(self.multilayer))))

class MultilayerSelectorScannableTest(unittest.TestCase):
    
    def setUp(self):
        self.positions = ('a', 'b', 'c')
        self.d_spacings = (1, 1.1)
        #self.d_spacings = (1.000000001, 1.1)
        self.start_energys = (10, 11)
        self.stop_energys = (20, 21)
        self.thp_offsets = (2, 2.1)
        self.pos_ys = (-14.5, 14.5, 0)
        self.pos_zs = (0.1, -0.1, 0)
        self.multilayers = [
            Multilayer(self.positions[0], self.d_spacings[0], self.start_energys[0], self.stop_energys[0], self.thp_offsets[0], self.pos_zs[0], self.pos_ys[0]),
            Multilayer(self.positions[1], self.d_spacings[1], self.start_energys[1], self.stop_energys[1], self.thp_offsets[1], self.pos_zs[1], self.pos_ys[1]) ]
        self.posz = Mock()
        self.posz.name = 'posz'
        self.posy = Mock()
        self.posy.name = 'posy'
        self.mls = MultilayerSelectorScannable('mls', self.multilayers, self.posz, self.posy)

    def tearDown(self):
        pass

    def testScannableSetup(self):
        mls = MultilayerSelectorScannable(name='mls', multilayer_list=self.multilayers, pz_scannable=self.posz, py_scannable=self.posy)
        self.assertEquals(repr(self.mls), repr(mls))

        self.assertEqual('mls', self.mls.name)
        self.assertEqual(list(self.mls.inputNames), ['edge'])
        self.assertEqual(list(self.mls.extraNames), ['d_spacing_A'])
        self.assertEqual(list(self.mls.outputFormat), ['%s', '%f'])
    
    def posz_isAt_side_effect(self, posz):
        return posz == self.posz.getPosition.return_value
    
    def posy_isAt_side_effect(self, posy):
        return posy == self.posy.getPosition.return_value
        
    def test__str__PositionXYa(self):
        self.posz.getPosition.return_value = self.pos_zs[0]
        self.posy.getPosition.return_value = self.pos_ys[0]
        self.posz.isAt.side_effect = self.posz_isAt_side_effect
        self.posy.isAt.side_effect = self.posy_isAt_side_effect
        #print             str(self.mls)
        self.assertEquals(str(self.mls), """MultiLayerSelector mls:
Selected Position D spacing Start Energy Stop Energy THP Offset PZ pos PY pos
                        (A)         (eV)        (eV)      (deg)   (mm)   (mm)
-------- -------- --------- ------------ ----------- ---------- ------ ------
       *        a         1           10          20          2    0.1  -14.5
                b       1.1           11          21        2.1   -0.1   14.5
-------- -------- --------- ------------ ----------- ---------- ------ ------""")

    def test__str__PositionXYb(self):
        self.posz.getPosition.return_value = self.pos_zs[1]
        self.posy.getPosition.return_value = self.pos_ys[1]
        self.posz.isAt.side_effect = self.posz_isAt_side_effect
        self.posy.isAt.side_effect = self.posy_isAt_side_effect
        #print             str(self.mls)
        self.assertEquals(str(self.mls), """MultiLayerSelector mls:
Selected Position D spacing Start Energy Stop Energy THP Offset PZ pos PY pos
                        (A)         (eV)        (eV)      (deg)   (mm)   (mm)
-------- -------- --------- ------------ ----------- ---------- ------ ------
                a         1           10          20          2    0.1  -14.5
       *        b       1.1           11          21        2.1   -0.1   14.5
-------- -------- --------- ------------ ----------- ---------- ------ ------""")

    def test__str__PositionXaYb(self):
        self.posz.getPosition.return_value = self.pos_zs[0]
        self.posy.getPosition.return_value = self.pos_ys[1]
        self.posz.isAt.side_effect = self.posz_isAt_side_effect
        self.posy.isAt.side_effect = self.posy_isAt_side_effect
        #print             str(self.mls)
        self.assertEquals(str(self.mls), """MultiLayerSelector mls:
Error! (posz,posy) in unknown position (0.1,14.5)
Selected Position D spacing Start Energy Stop Energy THP Offset PZ pos PY pos
                        (A)         (eV)        (eV)      (deg)   (mm)   (mm)
-------- -------- --------- ------------ ----------- ---------- ------ ------
                a         1           10          20          2    0.1  -14.5
                b       1.1           11          21        2.1   -0.1   14.5
-------- -------- --------- ------------ ----------- ---------- ------ ------""")

    def test__str__PositionXaYz(self):
        self.posz.getPosition.return_value = self.pos_zs[0]
        self.posy.getPosition.return_value = 1.234
        self.posz.isAt.side_effect = self.posz_isAt_side_effect
        self.posy.isAt.side_effect = self.posy_isAt_side_effect
        #print             str(self.mls)
        self.assertEquals(str(self.mls), """MultiLayerSelector mls:
Error! (posz,posy) in unknown position (0.1,1.234)
Selected Position D spacing Start Energy Stop Energy THP Offset PZ pos PY pos
                        (A)         (eV)        (eV)      (deg)   (mm)   (mm)
-------- -------- --------- ------------ ----------- ---------- ------ ------
                a         1           10          20          2    0.1  -14.5
                b       1.1           11          21        2.1   -0.1   14.5
-------- -------- --------- ------------ ----------- ---------- ------ ------""")

    def test__str__PositionXzYa(self):
        self.posz.getPosition.return_value = 2.345
        self.posy.getPosition.return_value = self.pos_ys[0]
        self.posz.isAt.side_effect = self.posz_isAt_side_effect
        self.posy.isAt.side_effect = self.posy_isAt_side_effect
        #print             str(self.mls)
        self.assertEquals(str(self.mls), """MultiLayerSelector mls:
Error! (posz,posy) in unknown position (2.345,-14.5)
Selected Position D spacing Start Energy Stop Energy THP Offset PZ pos PY pos
                        (A)         (eV)        (eV)      (deg)   (mm)   (mm)
-------- -------- --------- ------------ ----------- ---------- ------ ------
                a         1           10          20          2    0.1  -14.5
                b       1.1           11          21        2.1   -0.1   14.5
-------- -------- --------- ------------ ----------- ---------- ------ ------""")

    ''' Since we cannot define the return value from the __repr__ function
        in the Mocked MultilayerPositioner objects, the repr for the
        MultilayerSelectorScannable instead returns the name from
        MultilayerPositioner, allowing us to test this. '''
    def test__repr__(self):
        #print             repr(self.mls)
        self.assertEquals(repr(self.mls), "MultilayerSelectorScannable(u'mls', [Multilayer(name='a', d_spacing_A=1, energy_start_eV=10, energy_stop_eV=20, thp_offset_deg=2, pos_z_mm=0.1, pos_y_mm=-14.5), Multilayer(name='b', d_spacing_A=1.1, energy_start_eV=11, energy_stop_eV=21, thp_offset_deg=2.1, pos_z_mm=-0.1, pos_y_mm=14.5)], 'posz', 'posy')")

    ''' We should be able to assert that "mls == eval(repr(mls))", but
        because we cannot define the return value from the __repr__
        function in the Mocked MultilayerPositioner objects, this test 
        cannot be run. '''
#    def test_EvalRepr(self):
#        print             self.mls
#        self.assertEquals(self.mls, eval(repr(self.mls)))
 
    def testIsBusy(self):
        combinations=dict([((a,b),True) for a in (True,False) for b in (True,False)])
        combinations[(False,False)]=False

        for (bx,by), assertion in combinations.iteritems():
            self.posz.isBusy.return_value = bx
            self.posy.isBusy.return_value = by
            self.assertEqual(((bx,by),self.mls.isBusy()),
                             ((bx,by),assertion))

    def testMoveTo1a(self):
        self.mls.asynchronousMoveTo(0)
        self.posz.asynchronousMoveTo.assert_called_with(self.pos_zs[0])
        self.posy.asynchronousMoveTo.assert_called_with(self.pos_ys[0])

    def testMoveTo1b(self):
        self.mls.asynchronousMoveTo(self.positions[0])
        self.posz.asynchronousMoveTo.assert_called_with(self.pos_zs[0])
        self.posy.asynchronousMoveTo.assert_called_with(self.pos_ys[0])

    def testMoveTo2a(self):
        self.mls.asynchronousMoveTo(1)
        self.posz.asynchronousMoveTo.assert_called_with(self.pos_zs[1])
        self.posy.asynchronousMoveTo.assert_called_with(self.pos_ys[1])

    def testMoveTo2b(self):
        self.mls.asynchronousMoveTo(self.positions[1])
        self.posz.asynchronousMoveTo.assert_called_with(self.pos_zs[1])
        self.posy.asynchronousMoveTo.assert_called_with(self.pos_ys[1])
        
    def testMoveToFails3a(self):
        # Right (Call inside assertRaises, using parameter given):
        self.assertRaises(IndexError, self.mls.asynchronousMoveTo, 2)
        
        # Wrong (Call here, with results passed to assertRaises)
        #self.assertRaises(IndexError, self.mls.asynchronousMoveTo(2))
        
    def testMoveToFails3b(self):
        self.assertRaises(KeyError, self.mls.asynchronousMoveTo, self.positions[2])

   
    def testGetPositionerValue(self):
        self.posz.getPosition.return_value = self.pos_zs[0]
        self.posy.getPosition.return_value = self.pos_ys[0]
        self.posz.isAt.side_effect = self.posz_isAt_side_effect
        self.posy.isAt.side_effect = self.posy_isAt_side_effect
        self.assertEquals(self.positions[0], self.mls._getPositionerValue())
        
    def testGetPositionerValueFails(self):
        self.posz.getPosition.return_value = self.pos_zs[0]
        self.posy.getPosition.return_value = self.pos_ys[1]
        self.posz.isAt.side_effect = self.posz_isAt_side_effect
        self.posy.isAt.side_effect = self.posy_isAt_side_effect
        self.assertRaises(Exception, self.mls._getPositionerValue)
    
    def testGetPosition(self):
        self.posz.getPosition.return_value = self.pos_zs[0]
        self.posy.getPosition.return_value = self.pos_ys[0]
        self.posz.isAt.side_effect = self.posz_isAt_side_effect
        self.posy.isAt.side_effect = self.posy_isAt_side_effect
        self.assertEquals((self.positions[0], self.d_spacings[0]), self.mls.getPosition())

    def testGetPositionFails(self):
        self.posz.getPosition.return_value = self.pos_zs[0]
        self.posy.getPosition.return_value = self.pos_ys[1]
        self.posz.isAt.side_effect = self.posz_isAt_side_effect
        self.posy.isAt.side_effect = self.posy_isAt_side_effect
        self.assertRaises(Exception, self.mls.getPosition)
    
    def testGetDSpacing(self):
        self.posz.getPosition.return_value = self.pos_zs[0]
        self.posy.getPosition.return_value = self.pos_ys[0]
        self.posz.isAt.side_effect = self.posz_isAt_side_effect
        self.posy.isAt.side_effect = self.posy_isAt_side_effect
        self.assertEquals(self.d_spacings[0], self.mls.getDSpacing_A())

    def testGetDSpacingFails(self):
        self.posz.getPosition.return_value = self.pos_zs[1]
        self.posy.getPosition.return_value = self.pos_ys[1]
        self.posz.isAt.side_effect = self.posz_isAt_side_effect
        self.posy.isAt.side_effect = self.posy_isAt_side_effect
        self.assertNotEqual(self.d_spacings[0], self.mls.getDSpacing_A())
        
    def testGetThetaOffset(self):
        self.posz.getPosition.return_value = self.pos_zs[0]
        self.posy.getPosition.return_value = self.pos_ys[0]
        self.posz.isAt.side_effect = self.posz_isAt_side_effect
        self.posy.isAt.side_effect = self.posy_isAt_side_effect
        self.assertEquals(self.thp_offsets[0], self.mls.getThetaOffset_deg())

    def testGetThetaOffsetFails(self):
        self.posz.getPosition.return_value = self.pos_zs[1]
        self.posy.getPosition.return_value = self.pos_ys[1]
        self.posz.isAt.side_effect = self.posz_isAt_side_effect
        self.posy.isAt.side_effect = self.posy_isAt_side_effect
        self.assertNotEquals(self.thp_offsets[0], self.mls.getThetaOffset_deg())
    
    def testGetThetaOffsetFails2(self): # Test for an unknown position
        self.posz.getPosition.return_value = self.pos_zs[2]
        self.posy.getPosition.return_value = self.pos_ys[2]
        self.posz.isAt.side_effect = self.posz_isAt_side_effect
        self.posy.isAt.side_effect = self.posy_isAt_side_effect
        self.assertRaises(Exception, self.mls.getThetaOffset_deg)
    
    def testGetEnergyLimits(self):
        self.posz.getPosition.return_value = self.pos_zs[0]
        self.posy.getPosition.return_value = self.pos_ys[0]
        self.posz.isAt.side_effect = self.posz_isAt_side_effect
        self.posy.isAt.side_effect = self.posy_isAt_side_effect
        self.assertEquals((self.start_energys[0], self.stop_energys[0]), self.mls.getEnergyLimit_eVs())

    def testGetEnergyLimitsFails(self):
        self.posz.getPosition.return_value = self.pos_zs[0]
        self.posy.getPosition.return_value = self.pos_ys[1]
        self.posz.isAt.side_effect = self.posz_isAt_side_effect
        self.posy.isAt.side_effect = self.posy_isAt_side_effect
        self.assertRaises(Exception, self.mls.getEnergyLimit_eVs)

class PolarisationAnalyserTest(unittest.TestCase):

    def setUp(self):
        self.thp_scannable = Mock()
        self.thp_scannable.name = "thp"
        self.ttp_scannable = Mock()
        self.ttp_scannable.name = "ttp"
        self.mls = Mock()
        self.mls.name = "mls"
        self.energy = Mock()
        self.energy.name = "energy"
        self.pa = PolarisationAnalyser('pa', self.thp_scannable, self.ttp_scannable, self.mls, self.energy)
    
    def tearDown(self):
        pass

    def testScannableSetup(self):
        pa = PolarisationAnalyser(name='pa', thp_scannable=self.thp_scannable, ttp_scannable=self.ttp_scannable, multilayer_selector_scannable=self.mls, energy_scannable=self.energy)
        self.assertEquals(repr(self.pa), repr(pa))
        
        self.assertEqual('pa', self.pa.name)
        self.assertEqual(list(self.pa.inputNames), ['energy_keV'])
        self.assertEqual(list(self.pa.extraNames), ['thp', 'ttp', 'mls'])
        self.assertEqual(list(self.pa.outputFormat), ['%f', '%f', '%f', '%s'])
    
    def test__str__(self):
        self.ttp_scannable.getPosition.return_value = 60
        self.thp_scannable.getPosition.return_value = 31.230000000000004
        self.mls.getDSpacing_A.return_value = 1.
        self.mls.getPosition.return_value = ('a', 1)
        #print             str(self.pa)
        self.assertEquals(str(self.pa), 'energy_keV=12.39842, thp=31.23, ttp=60, mls=a')

    def test__repr__(self):
        #print             repr(self.pa)
        self.assertEquals(repr(self.pa), "PolarisationAnalyser(u'pa', 'thp', 'ttp', 'mls', 'energy')")
    
    def testAsynchronousMoveTo(self):
        self.mls.getDSpacing_A.return_value = 1.
        self.mls.getThetaOffset_deg.return_value = 1.23
        self.mls.getEnergyLimit_eVs.return_value = (1., 2000.)
        #self.pa.asynchronousMoveTo(12.39842)
        self.pa.asynchronousMoveTo(12398.42)
        #self.assertAlmostEquals(self.thp_scannable.asynchronousMoveTo.method_call, 31.23)
        self.thp_scannable.asynchronousMoveTo.assert_called_with(31.230000000000004)
        self.ttp_scannable.asynchronousMoveTo.assert_called_with(60.00000000000001)
        
    def testGetPosition(self):
        self.ttp_scannable.getPosition.return_value = 60
        self.thp_scannable.getPosition.return_value = 31.230000000000004
        self.mls.getDSpacing_A.return_value = 1.
        self.mls.getPosition.return_value = ('a', 1)
        #self.assertEqual(list(self.pa.getPosition()), [12.39842, 31.23, 60, 'a'])
        self.assertEqual(list(self.pa.getPosition()), [12.398420000000002, 31.230000000000004, 60, 'a'])

    ''' testIsBusy creates a dictionary of tests as keys and populates the
        expected results as the values '''        
    def testIsBusy(self):
        # Generate combinations, with a default of expecting True
        combinations=dict([((a,b),True) for a in (True,False) for b in (True,False)])
        # Exceptions
        combinations[(False,False)]=False

        for (bthp, bttp), assertion in combinations.iteritems():
            self.thp_scannable.isBusy.return_value = bthp
            self.ttp_scannable.isBusy.return_value = bttp
            # Put the args in the assert, so we get to see which one fails.
            self.assertEqual(((bthp,bttp),self.pa.isBusy()),
                             ((bthp,bttp),assertion))
            
    ''' The alternative, testIsBusy2 generates a list and removes each test as  
        it is performed. More complex overall, but might be a good option for
        more complex tests. '''
    def _testIsBusy2(self, combinations, (bthp, bttp), assertion):
            self.thp_scannable.isBusy.return_value = bthp
            self.ttp_scannable.isBusy.return_value = bttp
            self.assertEqual(((bthp,bttp),self.pa.isBusy()),
                             ((bthp,bttp),assertion))
            combinations.remove((bthp,bttp))

    def testIsBusy2(self):
        # Generate combinations
        combinations=list((a,b) for a in (True,False) for b in (True,False))
        # False expected (special case)
        self._testIsBusy2(combinations, (False,False), False)
        # True expected (all of the rest)
        while len(combinations) > 0:
            self._testIsBusy2(combinations, combinations[0], True)

        ''' Note, the following loop doesn't work, as it seems to iterate
            by removing combinations[0], then combinations[1], and finally
            combinations[3], but by the time [0] & [1] have been removed,
            there is no [3], so it fails.
            I expect this is why you are advised against modifying a mutable
            list while iterating through it. '''
        #for combination in combinations:
        #    self._testIsBusy2(combinations, combination, True)
        #
        #self.assertEqual(combinations, [])
        
#if __name__ == "__main__":
#    #import sys;sys.argv = ['', 'Test.testName']
#    unittest.main()