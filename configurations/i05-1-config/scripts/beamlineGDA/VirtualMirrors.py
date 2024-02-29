'''
Created on 7 Feb 2014

@author: i05user

Creates 2 virtual mirrors for each branch
'''

'''
Mirrors for nano branch
'''
'''
m1mj6 - moves m1 rotations and mj6 displacements in linear dependence to maintain the beam on mj6 centre
'''
m1mj6_pitch=BindScannables("m1mj6_pitch",m1_pitch,m3mj6_x)
m1mj6_pitch.setSlaveOffset(6.75958)
m1mj6_pitch.setSlaveStep(-0.0104762)
'''
m1mj6_roll=BindScannables("m1mj6_roll",m1_roll,m3mj6_y)
m1mj6_roll.setSlaveOffset(0.75)
m1mj6_roll.setSlaveStep(0.000416667)'''
'''
nano_m1es - moves m1 rotations, mj6 displacements and rotations in linear dependence on m1 to maintain the beam on the exit slit
'''
nano_m1es_pitch=BindScannables("nano_m1es_pitch",m1mj6_pitch,m3mj6_pitch)
nano_m1es_pitch.setSlaveOffset(5005)
nano_m1es_pitch.setSlaveStep(0.27)
'''
nano_m1es_roll=BindScannables("nano_m1es_roll",m1mj6_roll,m3mj6_roll)
nano_m1es_roll.setSlaveOffset(0)
nano_m1es_roll.setSlaveStep(0)
'''

'''
Mirrors for HR branch
'''
'''
m1m3 - moves m1 rotations and mj6 displacements in linear dependence to maintain the beam on mj6 centre
'''
m1m3_pitch=BindScannables("m1m3_pitch",m1_pitch,m3mj6_x)
m1m3_pitch.setSlaveOffset(5.75)
m1m3_pitch.setSlaveStep(-0.0104762)
'''
m1m3_roll=BindScannables("m1m3_roll",m1_roll,m3mj6_y)
m1m3_roll.setSlaveOffset(0.75)
m1m3_roll.setSlaveStep(0.000416667)
'''
'''
hr_m1es - moves m1 rotations, m3 displacements and rotations in linear dependence on m1 to maintain the beam on the exit slit
'''
hr_m1es_pitch=BindScannables("hr_m1es_pitch",m1m3_pitch,m3mj6_pitch)
hr_m1es_pitch.setSlaveOffset(4490)
hr_m1es_pitch.setSlaveStep(0.47)
'''
hr_m1es_roll=BindScannables("hr_m1es_roll",m1m3_roll,m3mj6_roll)
hr_m1es_roll.setSlaveOffset(0)
hr_m1es_roll.setSlaveStep(0)
'''
