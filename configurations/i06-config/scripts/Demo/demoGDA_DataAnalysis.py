import math;
import myFun;

y1 = DeviceFunctionClass("y1", "testMotor1","testMotor2", "myFun.testFunY1");

y2 = DeviceFunctionClass("y2", "testMotor1","testMotor2", "myFun.testFunY2");

scan testMotor1 -2*math.pi 2*math.pi 0.1 y1
scan testMotor1 -2*math.pi 2*math.pi 0.1 y2


#scan testMotor1 0 10 1 testMotor2 100 120 5

#data=ScanFileHolder()

#load the latest SRS data set into GDA
#data.loadSRS() 

#load the data set from run 13479
#data.loadSRS(13479)
#data.loadSRS("13479.dat")

#print the axis information about the data set
#data.info()
#data.ls()

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
#x=data.getAxis("testMotor1")Truet
#x.disp()
#y=data.getAxis("ca11")
#y.disp()
#x.min()
#x.max()
#y.min()
#y.max()

#y1=y
#y1-=10
#yd=y.diff(y1)
#mp=Plotter()
#mp.plot("Data Vector",x, y)
#mp.plotOver("Data Vector", x, yd)
#mp.plot("Data Vector", data1.getAxis("testMotor1"), data1.getAxis("y1"))
#mp.plot("Data Vector", data1.getAxis("testMotor1"), [data1.getAxis("y1"),data2.getAxis("y2")])

#scan testMotor1 -2*math.pi 2*math.pi 0.1 PlotXY("testMotor1",["math.sin(testMotor1)"])
#scan testMotor1 -2*math.pi 2*math.pi 0.1 PlotXY("testMotor1",["testFunY1(testMotor1, 1)"])

#scan testMotor1 -2*math.pi 2*math.pi 0.1 PlotXY("testMotor1",["testFunY1(eval('testMotor1.getPosition()'), 1)"])

#scan testMotor1 -2*math.pi 2*math.pi 0.1 PlotXY("testMotor1",["eval('testFunY1(eval("testMotor1.getPosition()"),1)')"])

scan testMotor1 -2*math.pi 2*math.pi 0.1 PlotXY("testMotor1",["myFun.testFunY1(eval('testMotor1.getPosition()'), 1)"])
