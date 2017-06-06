"""
Unit tests for DetectorShield
for use with GDA at Diamond Light Source
"""

import unittest
from gda.jython import InterfaceProvider, MockJythonServerFacade
from gdascripts.scannable.epics.PvManager import PvManagerWithMockCAClients
from scannables.detectorShield import DetectorShield

class DetectorShieldTest(unittest.TestCase):
    def setUp(self):
        InterfaceProvider.setTerminalPrinterForTesting(MockJythonServerFacade())
        self.pvManager = PvManagerWithMockCAClients(pvroot='BL15I-RS-ABSB-06:')
        #self.caClient.pvName.return_value = "X"
        self.ds = DetectorShield('ds', self.pvManager)

    def test__repr__(self):
        self.assertEquals(repr(self.ds),
            "DetectorShield(name=u'ds', pvManager=PvManagerWithMockCAClients(pvnames=[], pvroot='BL15I-RS-ABSB-06:'))")

    # ScannableBase tests

    # Either getPosition or rawGetPosition is required for default implementation of __str__():

    def test__str__(self):
        self.pvManager['STA'].caget.return_value='1'
        self.assertEquals(str(self.ds),
            "ds : 1")

    def test_getPosition(self):
        self.pvManager['STA'].caget.return_value='1'
        self.assertEqual(False, self.ds.isBusy())

    # Test for Scannable being suitable for scan

    # Either rawAsynchronousMoveTo or rawAsynchronousMoveTo is required to scan

    def rawAsynchronousMoveTo(self):
        self.ds.rawAsynchronousMoveTo(0)
        #self.pvManager['CON'].caput.assert_?

    # Test for Scannable being suitable for pos

    # Detector Shield tests

    def test_atScanStart(self):
        self.ds.atScanStart()
        self.pvManager['CON'].caput.assert_called_once_with(1)

    def test_atScanEnd(self):
        self.ds.atScanEnd()
        self.pvManager['CON'].caput.assert_called_once_with(0)

    def test_atCommandFailureWhenOpen(self):
        self.pvManager['STA'].caget.return_value='1'
        self.ds.atCommandFailure()
        self.pvManager['CON'].caput.assert_called_once_with(0)

    def test_isBusy_Open(self):
        self.pvManager['STA'].caget.return_value='1'
        self.assertEqual(False, self.ds.isBusy())

    def test_isBusy_Opening(self):
        self.pvManager['STA'].caget.return_value='2'
        self.assertEqual(True, self.ds.isBusy())

    def test_isBusy_Closed(self):
        self.pvManager['STA'].caget.return_value='3'
        self.assertEqual(False, self.ds.isBusy())

    def test_isBusy_Closing(self):
        self.pvManager['STA'].caget.return_value='4'
        self.assertEqual(True, self.ds.isBusy())

#    def test_isBusy_InError(self): # This passes whether or not an error is raised!
#        self.pvManager['STA'].caget.return_value='Error'
#        self.assertRaises(Exception, self.ds.isBusy())

