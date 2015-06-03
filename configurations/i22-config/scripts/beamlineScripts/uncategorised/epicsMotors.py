# This script gives a selection of examples of how to create a GDA variable from a moveable EPICS PV.
# To use remove the # and edit as approporiate
# Note you need to include the GDA variable name twice, once at the beginning of the line and again in the parentheses
# for use in GDA
# "pos d13motor ##" uses BL22I-DI-PHDGN-13:P:SETVALUE2.VAL
# "pos d13motor" uses BL22I-DI-PHDGN-13:POSN.RBV
# "d13motor.stop()" uses BL22I-DI-PHDGN-13:POSN.STOP
# BL22I-DI-PHDGN-13:POSN.DMOV is used during scans to tell GDA if the motor is moving

#fs_motor=SingleEpicsPositionerClass('fs_motor', 'BL22I-EA-SHTR-01:Y.VAL', 'BL22I-EA-SHTR-01:Y.RBV' , 'BL22I-EA-SHTR-01:Y.DMOV' , 'BL22I-EA-SHTR-01:Y.STOP','mm', '%.5f')
d13_motor=SingleEpicsPositionerClass('d13_motor', 'BL22I-DI-PHDGN-13:P:SETVALUE2.VAL', 'BL22I-DI-PHDGN-13:POSN.RBV' , 'BL22I-DI-PHDGN-13:POSN.DMOV' , 'BL22I-DI-PHDGN-13:POSN.STOP','mm', '%.5f')
#hexapod_x=SingleEpicsPositionerClass('hexapod_x', 'BL22I-MO-HEX-01:X.VAL' , 'BL22I-MO-HEX-01:X.RBV' , 'BL22I-MO-HEX-01:X.DMOV' , 'BL22I-MO-HEX-01:X.STOP' , 'mm', '%.5f')
#hexapod_y=SingleEpicsPositionerClass('hexapod_y', 'BL22I-MO-HEX-01:Y.VAL' , 'BL22I-MO-HEX-01:Y.RBV' , 'BL22I-MO-HEX-01:Y.DMOV' , 'BL22I-MO-HEX-01:Y.STOP' , 'mm', '%.5f')
#bioy=SingleEpicsPositionerClass('bioy', 'BL22I-EA-BSAX-01:Y.VAL' , 'BL22I-EA-BSAX-01:Y.RBV' , 'BL22I-EA-BSAX-01:Y.DMOV' , 'BL22I-EA-BSAX-01:Y.STOP' , 'mm', '%.5f')
#prot=SingleEpicsPositionerClass('prot', 'BL22I-MO-TABLE-08:ROT.VAL' , 'BL22I-MO-TABLE-08:ROT.RBV' , 'BL22I-MO-TABLE-08:ROT.DMOV' , 'BL22I-MO-TABLE-08:ROT.STOP' , 'deg', '%.5f')
# For epics device without status nor stop. It also set a tolerance
# In the example above, if the temperature is 0.5C around the set temperature, GDA considers the position is reached. 
# laudabath=SingleEpicsPositionerNoStatusClassDeadband('laudabath','BL22I-EA-TEMPC-03:SET_TEMP','BL22I-EA-TEMPC-03:TEMP','dummystring','dummystring','C','%.3f',0.5)
# integral=SingleEpicsPositionerNoStatusClassDeadband('integral','BL22I-EA-TEMPC-04:SET_TEMP','BL22I-EA-TEMPC-04:TEMP','dummystring','dummystring','C','%.3f',0.5)  