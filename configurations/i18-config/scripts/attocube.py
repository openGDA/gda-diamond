from gda.device.motor import EpicsMotor
from gda.device.scannable import ScannableMotor

# Create ScannableMotor based on EpicsMotor record
def create_epics_scannablemotor(name, base_pv):
    motor = EpicsMotor()
    motor.setPvName(base_pv)
    motor.configure()
    
    scn_motor = ScannableMotor()
    scn_motor.setName(name)
    scn_motor.setMotor(motor)
    scn_motor.configure()
    
    return scn_motor

    
attocube_rot = create_epics_scannablemotor("attocube_rot", "BL18I-TS-ECC-01:ACT2") #ECC-01, axis2
attocube_x = create_epics_scannablemotor("attocube_x", "BL18I-TS-ECC-04:ACT0") #ECC-04, axis0
attocube_y = create_epics_scannablemotor("attocube_y", "BL18I-TS-ECC-04:ACT1") #ECC-04, axis1
attocube_z = create_epics_scannablemotor("attocube_z", "BL18I-TS-ECC-04:ACT2") #ECC-04, axis2
