#BESTEC calibration
from i06shared.slits.exitSlit import slitsMotorClassV2
global s6x, s6y #these are the object defined in Spring beans which loaded at GDA server start already 
exec('[news6ygap, news6xgap] = [None, None]')
s6ygap = slitsMotorClassV2('s6ygap','micron',-29.832, -83625, 1, s6x, 0)
s6xgap = slitsMotorClassV2('s6xgap','micron',-80.036, -61951, 1, s6y, 0)

#tests6ygap = slitsMotorClassV2('news6ygap','micron',-29.832, -81539, 1, testMotor1, 0)