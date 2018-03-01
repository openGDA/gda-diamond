"""
Demo of using ConstantVelocityScanLine and MultiScanRunner

import flyscan
flyscan.flyscan(zebraTestZebraScannableMotor, -90, 90, .5,zebraTestContinuousMoveController, zebraTestDetector, .01 )

Copied from gda-dls-beamlines-i13x.git/i13-config/scripts/flyscan.py @136034c  (8.36)

Doesn't work in 8.34 even after switching run() for runScan()!
"""
from gda.scan import ConstantVelocityScanLine, MultiScanItem, MultiScanRunner
def flyscan(scannableMotor, start, stop, step, continuousMoveController, det, exposureTime):
    sc1=ConstantVelocityScanLine([scannableMotor, start, stop, step,continuousMoveController, det, exposureTime])
    items = []
    items.append(MultiScanItem(sc1,None))
    MultiScanRunner(items).run()