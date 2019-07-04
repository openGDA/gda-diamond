from gda.device.scannable import SimpleScannable
from gda.device.scannable.scannablegroup import ScannableGroup
from BeamlineI06.Mainline.xmcd import XMCDScanPositionProvider

imagenum = SimpleScannable()
imagenum.name = "imagenum"
imagenum.moveTo(0)

print "Creating energy scannable groups...\n"

print "  dxmcd uses iddpol & denergy"
dxmcd = ScannableGroup("dxmcd", (imagenum, iddpol, denergy))
dxmcd.configure()

print "  uxmcd uses idupol & uenergy"
uxmcd = ScannableGroup("uxmcd", (imagenum, idupol, uenergy))
uxmcd.configure()

print "  xxmcd uses xpol & xenergy"
xxmcd = ScannableGroup("xxmcd", (imagenum, xpol, xenergy))
xxmcd.configure()

print "\nCreating xmcd_positions...\n"
xmcd_positions = XMCDScanPositionProvider(name='xmcd_positions',
    numberOfImages=10, pols=('PosCirc', 'NegCirc'), energies=(706.7, 702.3))

print "  xmcd_positions.numberOfImages = %r" % xmcd_positions.numberOfImages
print "  xmcd_positions.pols = %r" % (xmcd_positions.pols,)
print "  xmcd_positions.energies = %r" % (xmcd_positions.energies,)

print "\nExamples\n"
print ">>> scan dxmcd xmcd_positions uv 1"
print ">>> scan dxmcd xmcd_positions pco 1"
print ">>> scan xxmcd xmcd_positions timer"
print ">>> xmcd_positions.numberOfImages=11"
print ">>> xmcd_positions.pols=(pc, nc, nc, pc)"
print ">>> xmcd_positions.energies=(706.7, 702.3, 702.3, 706.7)\n"

