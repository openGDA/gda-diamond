import math;
import myFun;

y1 = DeviceFunctionClass("y1", "testMotor1","testMotor2", "myFun.testFunY1");

y2 = DeviceFunctionClass("y2", "testMotor1","testMotor2", "myFun.testFunY2");

scan testMotor1 -2*math.pi 2*math.pi 0.1 y1
scan testMotor1 -2*math.pi 2*math.pi 0.1 y2

data=ScanFileHolder();


#load the SRS data set
data.loadSRS()

#load the data set from run 13479
#data.loadSRS(13479)
#data.loadSRS("13479.dat")

#print the axis information about the data set
#data.info()
data.ls()

#plot
#data.plot("y1")

#get one axis from the data set
#data.getAxis("testMotor1")
#data.getDataSet("testMotor1")
#data.getAxis(1)

#To find all peaks which appear to be peaks at the given deltawidth
# i.e. if there are 3 points deltawidth appart and the middle one is 
# highest then this is classed as a peak
#  @param XAxis, The X axis of the graph to fit
#  @param YAxis, The Y Axis ofdir the graph to fit
#  @param deltaWidth The width of the peak information
#  @return A dataset containing the positions of all the peaks found.
x=data.getAxis("testMotor1");
y=data.getAxis("y2");
dm=data.getMax("y2");
dmp=data.getMaxPos("y2");
dmpx=data.getMaxPos("testMotor1", "y2");

print dmp, dmpx, dm
