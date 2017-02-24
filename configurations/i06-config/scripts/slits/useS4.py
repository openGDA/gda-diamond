from i06shared.slits.exitSlit import slitsMotorClassV2
global s4x, s4y #these objects are defined in spring beans and loaded at GDA server starts.
exec('[news4ygap, news4xgap] = [None, None]')
s4ygap = slitsMotorClassV2('s4ygap','micron',-59.161, -43570, -1, s4x, 0)
s4xgap = slitsMotorClassV2('s4xgap','micron',-301.76, -61214,  1, s4y, 0)