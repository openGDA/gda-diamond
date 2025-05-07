from gda.device.scannable import PVScannable
from gda.device.motor import EpicsMotor
from gda.device.scannable import ScannableMotor

print("Running 'cryovac_scannables.py'...")

cryovac_t1 = PVScannable("cryovac_t1",  "BL20I-EA-CRYO-10:IN1")
cryovac_t1.setCanMove(False)
cryovac_t1.configure()

cryovac_t2 = PVScannable("cryovac_t2",  "BL20I-EA-CRYO-10:IN2")
cryovac_t2.setCanMove(False)
cryovac_t2.configure()


# Create scannable motor to control X translation stage
cryovac_x_motor = EpicsMotor()
cryovac_x_motor.setPvName("BL20I-MO-CRYO-01:X")
cryovac_x_motor.configure()

cryovac_x = ScannableMotor()
cryovac_x.setName("cryovac_x")
cryovac_x.setMotor(cryovac_x_motor)
cryovac_x.configure()

names = [s.getName() for s in cryovac_t1, cryovac_t2, cryovac_x]

print("Created cryovac scannables : {}".format(", ".join(names)))
