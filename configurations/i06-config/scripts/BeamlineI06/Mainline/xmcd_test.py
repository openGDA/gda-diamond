from xmcd import XMCDScanPositionProvider

import unittest

class XMCDScanPositionProviderTest(unittest.TestCase):

    def setUp(self):
        self.xmcd_positions = XMCDScanPositionProvider('xmcd_positions', numberOfImages=10, pols=('pc', 'nc'), energies=(706.7, 702.3))

    def tearDown(self):
        pass

    def test__repr__(self):
        self.assertEquals(repr(self.xmcd_positions), "XMCDScanPositionProvider(name='xmcd_positions', numberOfImages=10, pols=('pc', 'nc'), energies=(706.7, 702.3))")

    def test__str__(self):
        self.assertEquals(str(self.xmcd_positions), "XMCDScanPositionProvider(name='xmcd_positions', numberOfImages=10, pols=('pc', 'nc'), energies=(706.7, 702.3)): count=40")

    def test_init_order(self):
        xmcd_positions = XMCDScanPositionProvider('xmcd_positions', 10, ('pc', 'nc'), (706.7, 702.3))
        self.assertEquals(str(xmcd_positions), str(self.xmcd_positions))

    def test_tuplifications(self):
        self.assertEquals(str(XMCDScanPositionProvider('xmcd_positions', numberOfImages=10, energies=[706.7, 702.3], pols=('pc', 'nc'))), str(self.xmcd_positions))
        self.assertEquals(str(XMCDScanPositionProvider('xmcd_positions', numberOfImages=10, energies=(706.7, 702.3), pols=['pc', 'nc'])), str(self.xmcd_positions))

    def test_empty_values_before_size_called(self):
        self.assertEqual(self.xmcd_positions.values, [])

    def test_correct_size_default_energies(self):
        self.assertEqual(self.xmcd_positions.size(), 40)

    def test_new_energies(self):
        self.xmcd_positions.energies=(706.7, 702.3, 700.0)
        self.assertEqual(self.xmcd_positions.size(), 60)

    def test_new_pols(self):
        self.xmcd_positions.pols=('pc', 'nc', 'la')
        self.assertEqual(self.xmcd_positions.size(), 60)

    def test_new_numberOfImages(self):
        self.xmcd_positions.numberOfImages=11
        self.assertEqual(self.xmcd_positions.size(), 44)
"""
# Make an image scannable
from gda.device.scannable import SimpleScannable
image = SimpleScannable()
image.name = "image"
image.moveTo(0)

global iddpol, idupol, denergy

# Make a scannablegroup for driving energy & polarisation
from gda.device.scannable.scannablegroup import ScannableGroup
xmcd = ScannableGroup("xmcd", (image, iddpol, denergy))
xmcdu = ScannableGroup("xmcdu", (image, idupol, denergy))
#                        Level   5      7        5
xmcd.configure()

xmcd_positions = XMCDScanPositionProvider('xmcd_positions', 10, ('pc', 'nc'), (706.7, 702.3))

# Instead of 
#
#   from gda.device.scannable import SimpleScannable
#   image = SimpleScannable()
#   image.name = "image"
#   image.moveTo(0)
#   scan iddpol ('pc' 'nc') denergy (706.7 702.3) image 1 10 1 uv 1

# We would do
#
#   from BeamlineI06.Mainline.xmcd import XMCDScanPositionProvider
#   xmcd_positions = XMCDScanPositionProvider('xmcd_positions', 10, ('pc', 'nc'), (706.7, 702.3))
#   scan xmcd xmcd_positions uv 1
"""