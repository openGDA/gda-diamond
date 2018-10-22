from i06shared.slits.exitSlit import slitsMotorClassV2
import __main__ #these objects are defined in spring beans and loaded at GDA server starts. @UnresolvedImport
exec('[news4ygap, news4xgap] = [None, None]')
news4ygap = slitsMotorClassV2('news4ygap','micron',-59.161, -43570, -1, __main__.s4x, 0)
news4xgap = slitsMotorClassV2('news4xgap','micron',-301.76, -61214,  1, __main__.s4y, 0)

