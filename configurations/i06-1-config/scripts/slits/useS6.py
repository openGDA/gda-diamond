#BESTEC calibration
from i06shared.slits.exitSlit import slitsMotorClassV2
import __main__ #these are the object defined in Spring beans which loaded at GDA server start already @UnresolvedImport
exec('[news6ygap, news6xgap] = [None, None]')
news6ygap = slitsMotorClassV2('news6ygap','micron',-29.832, -83625, 1, __main__.s6x, 0)
news6xgap = slitsMotorClassV2('news6xgap','micron',-80.036, -61951, 1, __main__.s6y, 0)

#tests6ygap = slitsMotorClassV2('news6ygap','micron',-29.832, -81539, 1, testMotor1, 0)