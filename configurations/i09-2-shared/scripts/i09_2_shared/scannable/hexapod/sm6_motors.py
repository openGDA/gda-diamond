'''
SM6 Haxpod motors for mirror callback earlier before it reaches the target in Java EpicsMotor. These instances are created using position compare to work around the problem.

Created on 1 Aug 2019
add dummy on 19/08/2021 for nxmetadata support

@author: fy65
'''
import sys
from epics.motor.positionCompareMotorClassWithReadbackMonitor import PositionCompareMotorReadbackUpdateClass
from i09shared.utils.ExceptionLogs import localStation_exception
from gdascripts import installation
from gdascripts.pd.dummy_pds import DummyEpicsReadWritePVClass

if installation.isLive():
	try:
		sm6x = PositionCompareMotorReadbackUpdateClass("sm6x", "BL09K-MO-SM-06:X.VAL", "BL09K-MO-SM-06:X.RBV", "BL09K-MO-SM-06:X.STOP", 0.002, "mm", "%.3f")
		sm6y = PositionCompareMotorReadbackUpdateClass("sm6y", "BL09K-MO-SM-06:Y.VAL", "BL09K-MO-SM-06:Y.RBV", "BL09K-MO-SM-06:Y.STOP", 0.002, "mm", "%.3f")
		sm6z = PositionCompareMotorReadbackUpdateClass("sm6z", "BL09K-MO-SM-06:Z.VAL", "BL09K-MO-SM-06:Z.RBV", "BL09K-MO-SM-06:Z.STOP", 0.002, "mm", "%.3f")
		sm6yaw = PositionCompareMotorReadbackUpdateClass("sm6yaw", "BL09K-MO-SM-06:YAW.VAL", "BL09K-MO-SM-06:YAW.RBV", "BL09K-MO-SM-06:YAW.STOP", 0.002, "urad", "%.3f")
		sm6pitch = PositionCompareMotorReadbackUpdateClass("sm6pitch", "BL09K-MO-SM-06:PITCH.VAL", "BL09K-MO-SM-06:PITCH.RBV", "BL09K-MO-SM-06:PITCH.STOP", 0.002, "urad", "%.3f")
		sm6roll = PositionCompareMotorReadbackUpdateClass("sm6roll", "BL09K-MO-SM-06:ROLL.VAL", "BL09K-MO-SM-06:ROLL.RBV", "BL09K-MO-SM-06:ROLL.STOP", 0.002, "urad", "%.3f")
	except:
		localStation_exception(sys.exc_info(), "initialising sm6 hexapod scannables failed")
else:
	import java #@UnresolvedImport
	base_pv = java.net.InetAddress.getLocalHost().getHostName().split(".")[0] + "-MO-SIM-01:"
	sm6x = PositionCompareMotorReadbackUpdateClass("sm6x", base_pv+"M1.VAL", base_pv+"M1.RBV", base_pv+"M1.STOP", 0.01, "mm", "%.3f")
	sm6y = PositionCompareMotorReadbackUpdateClass("sm6y", base_pv+"M2.VAL", base_pv+"M2.RBV", base_pv+"M2.STOP", 0.01, "mm", "%.3f")
	sm6z = PositionCompareMotorReadbackUpdateClass("sm6z", base_pv+"M3.VAL", base_pv+"M3.RBV", base_pv+"M3.STOP", 0.01, "mm", "%.3f")
	sm6yaw = DummyEpicsReadWritePVClass("sm6yaw",  0.0, 5.0, 'V', '%.3f')
	sm6pitch = DummyEpicsReadWritePVClass("sm6pitch",  0.0, 5.0, 'V', '%.3f')
	sm6roll = DummyEpicsReadWritePVClass("sm6roll",  0.0, 5.0, 'V', '%.3f')

