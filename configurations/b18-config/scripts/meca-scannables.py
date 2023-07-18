



# Create MecaRobotMover to move the ScannableGroup containing setpoints to be controlled 
#from gda.device.robot import MecaRobotMover
#meca_move_pose_xy = MecaRobotMover()
#meca_move_pose_xy.setName("meca_move_pose_xy")
#meca_move_pose_xy.setPositionScannable(meca_pose_xy)

## set the other properties to match reference scannable
#refScn = meca_move_pose_x
#meca_move_pose_xy.setCopyPositionsScannable(refScn.getCopyPositionsScannable())
#meca_move_pose_xy.setStartMoveScannable(refScn.getStartMoveScannable())
#meca_move_pose_xy.setStatusChecker(refScn.getStatusChecker())
#meca_move_pose_xy.configure()

# Calculator object : axis is straight line in x-y coordinate system, at user specified angle to x-axis
from gda.device.scannable import CombinedAxisCalculator
calc = CombinedAxisCalculator()
# set the origin - the x y motor positions definine the zero position of the axis
calc.setOrigin(180, 80)
# set the angle of the axis
calc.setAxisAngle(45)

# Scannable to set position based on results from CombinedAxisCalculator 
# Position when moving meca_move_xy is distance along axis defined by CombinedAxisCalculator relative to origin
from uk.ac.gda.core.virtualaxis import CombinedManipulator
meca_move_xy_combined = CombinedManipulator()
meca_move_xy_combined.setName("meca_move_xy_combined")
meca_move_xy_combined.setCalculator(calc)
meca_move_xy_combined.setScannables([meca_move_pose_xy])
meca_move_xy_combined.configure()


# meca_move_xy_combined.moveTo(10) -> position = [origin_x + 10*cos(angle) , origin_y + 10*sin(angle)]
# Scan using e.g. : scan meca_move_xy_combined 0 10 1.0 counterTimer01 1.0




# Scannable for moving sam2x sam2y simultaneously along line in x-y coordinate system
sam2xy_calculator = CombinedAxisCalculator()
sam2xy_calculator.setOrigin(5, 5)
sam2xy_calculator.setAxisAngle(30)

sam2xy_combined = CombinedManipulator()
sam2xy_combined.setName("sam2xy_combined")
sam2xy_combined.setCalculator(sam2xy_calculator)
sam2xy_combined.setScannables([sam2x, sam2y])
sam2xy_combined.configure()


# Create scannable to allow meca pose to be moved in continuous scan
from gda.device.scannable.zebra import ContinuousMotionScannable
cont_move_pose_x = ContinuousMotionScannable()
cont_move_pose_x.setName("cont_move_pose_x")
cont_move_pose_x.setDelegate(meca_move_pose_x)

# Set the robot cartesian linear velocity (mm per sec)
def setRobotLinearVelocity(speedMmPerSec) :
    CAClient.put("BL18B-MO-ROBOT-01:CARTLINVEL:SET", speedMmPerSec)

import math

# Do continuous scan of cont_move_pose_x 
def doRobotScan(startPos, endPos, numPoints, totalTime):
    
    # Move to initial position at fast speed
    setRobotLinearVelocity(150)
    cont_move_pose_x.getDelegate().moveTo(startPos)
    
    # set the speed of the motors to match speed of the scan 
    motorSpeed = math.fabs(endPos-startPos)/totalTime
    setRobotLinearVelocity(motorSpeed)
    
    # create the scan object (ionchambers is added automatically by getCscanUnsyncronized)
    meca_scan=getCscanUnsyncronized(cont_move_pose_x, startPos, endPos, numPoints, totalTime)
    
    # add meca_move_pose_x as an 'extra scannable' - so that readback position is recorded for each point in the scan
    meca_scan.getScannables().add(cont_move_pose_x.getDelegate())
    
    meca_scan.runScan()
    
    # reset the speed
    setRobotLinearVelocity(150)

