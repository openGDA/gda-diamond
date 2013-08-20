
# Plotting Features:

data = ScanFileHolder()

#scan testMotor1 0 10 1 testMotor2 PlotXY("testMotor1",["testMotor2*testMotor1"])

#scan testMotor1 0 10 1 testMotor2 PlotOverXY("testMotor1",["testMotor2*testMotor1*2"])

#scan testMotor1 10 20 1 testMotor2 PlotOverXY("testMotor1",["testMotor2*testMotor1*2"])

#scan testMotor1 0 10 1 testMotor2 100 1 PlotXY("testMotor1",["testMotor1*testMotor1"])

#scan testMotor1 20 30 1 testMotor2 100 1 PlotOverXY("testMotor1",["testMotor1*testMotor1"])

#scan testMotor1 0 10 1 testMotor2 PlotXY("testMotor1",["testMotor2*testMotor1"])

#scan testMotor1 -2*math.pi 2*math.pi 0.1 PlotXY("testMotor1",["math.sin(testMotor1)"])

data.loadSRS(13837)

x1=data.getAxis("u1j")
y1=data.getAxis("ca62sr")

#list x1 data
x1.disp()

data.loadSRS(13838)
x2=data.getAxis("u1j")
y2=data.getAxis("ca62sr")

dvp=Plotter()
dvp.plot("DV Plotter", x1, y1)

dvp.plotOver("DV Plotter", x2, y2)

#create another data set y3 for demo

yi=y1.getIndexDataSet()
y3=y1+yi.sin()*10000+yi*1000+50000

dvp.plotOver("DV Plotter", x1, y3)

dvp.plot("Data Vector", x1, y3-y1)
