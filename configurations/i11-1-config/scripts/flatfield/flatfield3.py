from java.math import BigDecimal
import time
from localStation import finder
from gda.epics.CAClient import caput

# parameters
acquisition_start_angle = -72
acquisition_end_angle   = -41
motor_name = "delta"
motor_pv="BL11I-MO-DIFF-01:DELTA"
detector_name = "mythen"
target_count = 100000
data=[]

# get objects
motor = finder.find(motor_name)
detector = finder.find(detector_name)

def startAcquisition(duration):
    print "collecting data"
    detector.setCollectionTime(duration)
    detector.collectData()
    print "moving motor from %.2f to %.2f" % (start_angle, end_angle)
    moveMotorTo(end_angle)
    print "data collection complete"
    data = detector.readout()

def moveMotorTo(angle):
    motor.moveTo(angle)
    while (motor.getPosition() != angle):
        print "  waiting - motor is at %.1f" % motor.getPosition()
        time.sleep(1.0)
    print "motor has reached position " + str(angle)
    
def avg(data):
	return sum(data) / len(data)

# calculate start/end angles
start_angle = acquisition_start_angle - motor.getSpeed().getAmount()
end_angle = acquisition_end_angle + motor.getSpeed().getAmount()

print "current motor speed: %.2f %s" % (motor.getSpeed().getAmount(), motor.getSpeed().getUnit())
print "current motor position: %.1f" % motor.getPosition()

# synchronously move motor to start position
print "moving motor to start angle %.2f" % start_angle
moveMotorTo(start_angle)

# calculate required duration
duration = (acquisition_end_angle - acquisition_start_angle) / motor.getSpeed().getAmount() + 2.0
print "estimated duration: %.2f" % duration
startAcquisition(duration)

avg_count = avg(data)
print "count stats: min %d, max %d, average %.1f" % (min(data), max(data), avg_count)

required_speed = motor.getSpeed().getAmount() / (target_count / avg_count)
print "required speed is %.5f" % required_speed

caput(motor_pv+".VELO", required_speed)
duration = (acquisition_end_angle - acquisition_start_angle) / required_speed + 2.0
moveMotorTo(start_angle)
startAcquisition(duration)