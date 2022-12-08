robotStatusBits=["Activated", "Homed", "Simulation Mode", "Error", "Paused", "End of block", "End of movement"]
gripperStatusBits=["Gripper Present", "Homed", "Holding part", "Limit reached", "Error", "Overload"]

def interpretBits(word, bitDescription) :
    for bit in range(len(bitDescription)) :
        # print bit, 2**bit
        if word&(2**bit) > 0 :
            print bitDescription[bit]


print "Use showRobotStatus() and showGripperStatus() to show Meca robot and gripper status descriptions"
def showRobotStatus():
    statusWord = int(meca_robot_status.getPosition())
    interpretBits(statusWord, robotStatusBits)
    
def showGripperStatus():
    statusWord = int(meca_gripper_status.getPosition())
    interpretBits(statusWord, gripperStatusBits)