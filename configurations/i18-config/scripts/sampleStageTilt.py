from org.jscience.physics.quantities import Quantity
from org.jscience.physics.units import SI

def setOffset(axis, offset):
    offset_quantity = Quantity.valueOf(offset, SI.MILLI(SI.METER))
    MicroFocusSampleStage.setPositionOffset(axis.dofname, offset_quantity)
    
def getOffset(axis):
    return MicroFocusSampleStage.getPositionOffset(axis.dofname)

def showStage():
    y1_motor = finder.find("sample_y1_motor")
    y2_motor = finder.find("sample_y2_motor")
    y3_motor = finder.find("sample_y3_motor")
    print "Stage Status:"
    print "\t (X,Y) = (%s, %s) " % (MicroFocusSampleX.getPosition(), MicroFocusSampleY.getPosition())
    print "\t (Y1,Y2,Y3) = (%s, %s, %s)" % (sample_y1.getPosition(), sample_y2.getPosition(), sample_y3.getPosition())
    print "\t Actual (Y1,Y2,Y3) = (%s, %s, %s)" % (y1_motor.getPosition(), y2_motor.getPosition(), y3_motor.getPosition())

def resetOffsets():
    setOffset(sample_y1, 0.0)
    setOffset(sample_y2, 0.0)
    setOffset(sample_y3, 0.0)
    
def listOffsets():
    print "Stage Offsets:"
    print "\t Y1 Offset :%s" % MicroFocusSampleStage.getPositionOffset("sample_y1")
    print "\t Y2 Offset :%s" % MicroFocusSampleStage.getPositionOffset("sample_y2")
    print "\t Y3 Offset :%s" % MicroFocusSampleStage.getPositionOffset("sample_y3")

def helpTilt():
    print "The available commands are:"
    print "\t showStage()"
    print "\t listOffsets()"
    print "\t setOffset(axis,offset)"
    print "\t \t e.g. setOffset(sample_y1, 0.24)"
    print "\t resetOffsets()"
