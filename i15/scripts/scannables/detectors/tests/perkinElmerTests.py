"""
Unit tests for PerkinElmerAxisWrapper & DetectorAxisWrapperNew
for use with GDA at Diamond Light Source
"""

import unittest
from mock import Mock
from scannables.detectors.perkinElmer import PerkinElmer, PerkinElmerInterfaceDummy
from scannables.detectors.perkinElmerAxisWrapper import PerkinElmerAxisWrapper
from gda.jython import InterfaceProvider, MockJythonServerFacade

class PerkinElmerAxisWrapperTestNoAxis(unittest.TestCase):

    def setUp(self):
        InterfaceProvider.setTerminalPrinterForTesting(MockJythonServerFacade())
        self.peid = PerkinElmerInterfaceDummy()
        self.detector=PerkinElmer('pe', self.peid, "X:", "/dls/i15/data",
                                  "2011/cm2062-3", "tmp", "deletemeMBB")
        self.wrappedDetector=PerkinElmerAxisWrapper(self.detector,
            Mock(), Mock(), Mock(), Mock(), exposeDark=True)
        # Without exposeDark=True, PerkinElmer.getStatus() always returns
        # Busy, so the tests never return.

    def tearDown(self):
        pass

    def test__str__(self):
        self.assertEquals(str(self.wrappedDetector),
            "perkin elmer wrapper : Exposure Time: 1.0000 file name: []")

    def test__repr__(self):
        self.assertEquals(repr(self.wrappedDetector),
            "perkin elmer wrapper : Exposure Time: 1.0000 file name: []")

    def testRawAsynchronousMoveTo(self):
        self.peid.darkSummedRbvCA.caput(1)
        self.wrappedDetector.rawAsynchronousMoveTo(0)

#class PerkinElmerAxisWrapperTestMockAxis(unittest.TestCase):
#
#    def setUp(self):
#        InterfaceProvider.setTerminalPrinterForTesting(MockJythonServerFacade())
#        self.peid = PerkinElmerInterfaceDummy()
#        self.detector=PerkinElmer('pe', self.peid, "X:", "/dls/i15/data/2011",
#                                  "cm2062-3", "tmp", "deletemeMBB")
#        self.wrappedDetector=PerkinElmerAxisWrapper(self.detector, Mock(), Mock(), Mock(), Mock(), "", exposureTime=1, axis=Mock(), step=1)
#
#    def tearDown(self):
#        pass
#
#    def test__str__(self):
#        self.assertEquals(str(self.wrappedDetector),
#            "perkin elmer wrapper : Exposure Time: 1.0000 file name: []")
#
#    def test__repr__(self):
#        self.assertEquals(repr(self.wrappedDetector),
#            "perkin elmer wrapper : Exposure Time: 1.0000 file name: []")
#
#    def testRawAsynchronousMoveTo(self):
#        self.wrappedDetector.rawAsynchronousMoveTo(0)

class PerkinElmerTest(unittest.TestCase):

    def setUp(self):
        self.peid = PerkinElmerInterfaceDummy()
        self.detector=PerkinElmer('pe', self.peid, "X:", "/dls/i15/data",
                                  "2011/cm2062-3", "tmp", "deletemeMBB")

    def tearDown(self):
        pass

    def test__str__(self):
        self.assertEquals(str(self.detector),
            "pe : status=IDLE")

    def test__repr__(self):
        self.assertEquals(repr(self.detector),
            "PerkinElmer(name=u'pe', PerkinElmerInterfaceDummy())")

    def testGetStatus(self):
        self.assertEquals(repr(self.detector.getStatus()),
            "0")

    def testReadout(self):
        self.assertEquals(repr(self.detector.readout()),
            "'/dls/i15/data/2011/cm2062-3/tmp/deletemeMBB-00000.tif'")

    def testCollectData(self):
        self.detector.collectData()
        self.assertEquals(repr(self.detector.pe.outputDirCA.returnValue),
            "'X:/2011/cm2062-3/tmp'")