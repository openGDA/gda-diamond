from gda.device.scannable import SimpleScannable
from gda.device.scannable.scannablegroup import ScannableGroup
from BeamlineI06.Mainline.xmcd import XMCDScanPositionProvider

imagenum = SimpleScannable()
imagenum.name = "imagenum"
imagenum.moveTo(0)

xmcd = ScannableGroup("xmcd", (imagenum, iddpol, denergy))
xmcd.configure()

xmcd_positions = XMCDScanPositionProvider('xmcd_positions', 10, (pc, nc), (706.7, 702.3))