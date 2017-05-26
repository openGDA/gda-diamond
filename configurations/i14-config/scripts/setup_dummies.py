# Dummy objects for testing

from gda.device.motor import DummyMotor
from gda.device.scannable import ScannableMotor

# dcm_enrg
dcm_enrg_motor = DummyMotor()
dcm_enrg_motor.name = "dcm_enrg_motor"
dcm_enrg_motor.minPosition = 4.8
dcm_enrg_motor.maxPosition = 26.0
dcm_enrg_motor.position = 5.3
dcm_enrg_motor.local = True
dcm_enrg_motor.configure()

dcm_enrg = ScannableMotor()
dcm_enrg.name = "dcm_enrg"
dcm_enrg.motor = dcm_enrg_motor
dcm_enrg.configure()