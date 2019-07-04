from gda.analysis import ScanFileHolder;

class KeyPositionClass(object):

	def __init__(self, xAxisName, yAxisName):
		self.xAxisName=xAxisName;
		self.yAxisName=yAxisName;
		self.data=ScanFileHolder();

	def update(self):
		self.data.loadSRS();
#		self.data.loadSRS("/home/xr56/Dev/gdaDev/gda-config/i07/users/data/operation/83.dat");

	def getKeyValues(self, axisName):
		self.update();
		
		ds=self.data.getAxis(axisName)
		mean = ds.mean();
		std  = ds.std();
		sum  = ds.sum();
		
		minval = ds.min();
		minpos = ds.minPos();
		
		maxval = ds.max()
		maxpos = ds.maxPos()

		return [minpos, minval, maxpos, maxval, sum, mean, std];


	def getPeak(self, xAxisName=None, yAxisName=None):
		if xAxisName is None:
			xAxisName = self.xAxisName;
		if yAxisName is None:
			yAxisName = self.yAxisName;
			
		self.update();

		yMax=self.data.getMax(yAxisName);
		yPos = self.data.getMaxPos(yAxisName)[0];
		xVal=self.data.getMaxPos(xAxisName, yAxisName);
		
		return [xVal, yMax];

		
	def getCentreOfMass(self, xAxisName=None, yAxisName=None):
		if xAxisName is None:
			xAxisName = self.xAxisName;
		if yAxisName is None:
			yAxisName = self.yAxisName;

		self.update()
		xDataSet=self.data.getAxis(xAxisName);
		yDataSet=self.data.getAxis(yAxisName);

		com = self.data.centroid(xDataSet, yDataSet)

		xlist = list(xDataSet.getBuffer())
		ylist = list(yDataSet.getBuffer())		
		
		second_moment = 0
		sum = 0
		for x, y in zip(xlist,ylist):
			sum += y
			second_moment += pow(x-com, 2) * y
	
		normalised_second_moment = second_moment/sum
	
		return [com, normalised_second_moment]

#Usage
kp=KeyPositionClass("testMotor1", "pil1stats_sum");

[xValue, yPeak] = kp.getPeak();
[xCom, yNsm] = kp.getCentreOfMass();

