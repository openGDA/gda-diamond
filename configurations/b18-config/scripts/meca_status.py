robotStatusBits=["Activated", "Homed", "Simulation Mode", "Error", "Paused", "End of block", "End of movement"]
gripperStatusBits=["Gripper Present", "Homed", "Holding part", "Limit reached", "Error", "Overload"]

def interpretBits(word, bitDescription) :
    for bit in range(len(bitDescription)) :
        # print bit, 2**bit
        if word&(2**bit) > 0 :
            print bitDescription[bit]


print "Use showRobotStatus() and showGripperStatus() to show Meca robot and gripper status descriptions"
def showRobotStatus():
    print meca_robot_status.getCurrentBitStrings()
    
def showGripperStatus():
    print meca_gripper_status.getCurrentBitStrings()

def resetRobotError() :
    pos meca_pstop_error_reset 1
    pos meca_error_reset 1
    pos meca_motion_resume 1

def moveRobotToCassette() :
    pos meca_copy_readbacks 1
    pos meca_joint_theta_1 49
    pos meca_move_joints 1
    
print "Use checkRobotConnected(), checkRobotActivated(), checkRobotHomed() to connect/activate if necessary and home the robot"

#Connect to robot if not already connected
def checkRobotConnected() :
    print "Checking connection to Robot."
    if int(meca_is_connected.getPosition()) != 1 :
        print "...Connecting to Robot"
        meca_is_connected.moveTo(1)
        sleep(2)
    print "Finished"
        
# Wait for up to timeLimit seconds for robot status bit to contain value 'robotStatusString'
def waitForRobotStatus(statusString, timeLimit=15):
    """
    Wait for up to 'timeLimit' seconds for robot status bit to
    contain value 'robotStatusString'. Throws an exception if time limit is reached
    Parameters :
    statuString - value to wait for
    timeLimit - how long to wait for (optional, default = 15secs)
    """
    count = 0   
    while meca_robot_status.getCurrentBitStrings().count(statusString) == 0 :
        print "...Waiting for Robot status '"+statusString
        sleep(1)
        count +=1
        if count > timeLimit :
            raise Exception("Robot state "+statusString+" not reached after "+str(count)+" seconds")

# 'Activate' the robot if not already activated
def checkRobotActivated() :
    print "Checking Robot is activated."
    activatedString = "Activated"
    if meca_robot_status.getPosition().count(activatedString) == 0 :
        print "...Activating Robot"
        meca_activate.moveTo(1)
    timeLimit=15
    count=0
    waitForStatus(activatedString)
    
    print "Robot activated"
        
def checkRobotHomed():
    print "Checking Robot is homed."
    if meca_robot_status.getPosition().count("Homed") == 0 :
        homeRobot()
        
# Home the robot
def homeRobot(): 
    print "Homing robot..."
    meca_home.moveTo(1)
    waitForStatus("Homed")
    print "Finished"
    
# Connect, activate then home the Robot
def prepareRobot() :
    checkRobotConnected()
    checkRobotActivated()
    checkRobotHomed()
    

if LocalProperties.isDummyModeEnabled() :
    # Set robot status to 'End of Block' + 'End of movement' so scannables are not constantly busy, filling up logs!
    meca_robot_status_word.moveTo(96)