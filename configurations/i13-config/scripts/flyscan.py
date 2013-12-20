"""
Demo of using ConstantVelocityScanLine and MultiScanRunner

import flyscan
flyscan.flyscan(zebraTestZebraScannableMotor, -90, 90, .5,zebraTestContinuousMoveController, zebraTestDetector, .01 )
"""
from gda.scan import ConstantVelocityScanLine, MultiScanItem, MultiScanRunner
def flyscan(scannableMotor, start, stop, step, continuousMoveController, det, exposureTime):
    sc1=ConstantVelocityScanLine([scannableMotor, start, stop, step,continuousMoveController, det, exposureTime])
#    sc2=ConstantVelocityScanLine([scannableMotor, stop, start, step,continuousMoveController, det, exposureTime])
    items = []
    items.append(MultiScanItem(sc1,None))
#    items.append(MultiScanItem(sc2,None)) 
    MultiScanRunner( items).runScan()