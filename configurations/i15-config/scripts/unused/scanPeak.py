import os, glob
from time import sleep


from gda.analysis import RCPPlotter
from gda.analysis import ScanFileHolder
from gda.analysis.functions import Step
from gda.data import NumTracker
from gda.jython.commands import InputCommands

from org.eclipse.january.dataset import DatasetFactory

from uk.ac.diamond.scisoft.analysis.fitting import Fitter 
from uk.ac.diamond.scisoft.analysis.optimize import GeneticAlg

from gdascripts.messages.handle_messages import simpleLog

from operationalControl import genericScanChecks

# Optimiser for fitting step function - e.g. MonteCarlo(0.001), GeneticAlg(0.001), GradientDescent(0.001)...
optimiser =  GeneticAlg(0.001)

def getDerivative(fileNo=0):
	"""
	Calculate cscanderivative and optionally fit Gaussian within a given range and calculate FWHM
	"""
	data = getData(fileNo)
	RCPPlotter.plot("Data Vector", data[0], data[1])
	
	derivative = data[1].diff(data[0])
	derivative.setName("derivative of " + str(fileNo) + ".dat")
	RCPPlotter.addPlot("Data Vector", data[0], derivative)
	
	# Save derivative, then optionally fit Gaussian graph and find FWHM
	response = InputCommands.requestInput('Fit Gaussian in range? (e.g. 0.1, 0.2 or q to quit)')
	while (response != 'q'):
		maxMin = response.split(",")
		if (len(maxMin) == 1):
			maxMin = response.split(" ")	 # try and split on space
		if (len(maxMin) != 2):
			simpleLog("Please try again (enter range, e.g. '0.1, 0.2')")
		else:
			# Get derivative values in range
			pointsY = []
			minX = float(maxMin[0].strip())
			maxX = float(maxMin[1].strip())
			for i in range(0, int(len(data[0])), 1):
				if (data[0][i] >= minX and data[0][i] <= maxX):
					pointsY.append(derivative[i])
			
			# fit Gaussian
			fit = Fitter.fit(data[0], derivative, optimiser, 
			 		[Gaussian(minX, maxX, maxX - minX, (maxX - minX) * DatasetFactory.createFromObject(pointsY).max() / 2)])
			RCPPlotter.plot("Data Vector", data[0],fit.display(data[0])[0]);

			
		response = InputCommands.requestInput("Enter another range to fit? (q to quit)")

def cscanPeak(motor, start, step, param1, param2=-1, param3=-1):
	"""
	Do cscan, fit step function and move 
	motor to centre
	e.g. 	cscanPeak(pinx, 0.1, 0.02, d2) 
			cscanPeak(pinx, 0.1, 0.02, w, 0.2, d2)
			
			cscan pinx 0.1 0.02 w 0.2 d2
			cscan bsx 0.1 0.02 dummyDiode 
	"""
	genericScanChecks(False, True, motor, start, -1, step, param1, param2, param3)

	centre = fitStepFunction(0)
	movePeakCentre(centre, motor)
	
def scanPeak(motor, start, stop, step, param1, param2=-1, param3=-1):
	"""
	Do scan, fit step function and move 
	motor to centre
	e.g.		scan pinx 0.1 0.2 0.01 d2
	"""
	genericScanChecks(False, False, motor, start, stop, step, param1, param2, param3) 
	
	centre = fitStepFunction(0)
	movePeakCentre(centre, motor)
		
def fitStepFunction(fileNo=0):
	"""
	Fit step function on latest data and calculate peak centre and FWHM, 
	returning peak centre
	
				   |----|	|--|
				   |	|----|  |
				   |			|
 		-----------|			|------------- 
	"""
	data = getData(fileNo)
	
	topY = data.getMax(data[1].name)
	bottomY = data.getMin(data[1].name)
	
	# 1. Get parameters for step function
	maxY = bottomY + 0.25 * (topY - bottomY)
	minY = bottomY - 0.25 * (topY - bottomY)

	minX1 = data.getMin(data[0].name) 
	maxX1 = (data.getMax(data[0].name) + minX1) / 2
	minX2 = maxX1 
	maxX2 = data.getMax(data[0].name)

	maxH1 = topY - bottomY
	minH1 = 0.1 * maxH1
	minH2 = - maxH1
	maxH2 = maxH1
	minW = 0.05
	maxW = 0.9
	minPos = 0.1 
	maxPos = 0.9
	
	# 2. Fit step function		
	fit = Fitter.fit(data[0], data[1], 
					  optimiser, 
					 [Step(minY, maxY, minX1, maxX1, minX2, maxX2, minH1, maxH1, minH2, maxH2, minW, maxW, minPos, maxPos)])
	RCPPlotter.plot("Data Vector", data[0],fit.display(data[0])[0]);
	
	# 3. Get peak centre value (fit[0...6].value gives each parameter value)
	#simpleLog("Fit vals: " + fit.disp())
	innerPeakWidth = (fit[2].value - fit[1].value) * fit[5].value
	innerPeakStart = fit[1].value + (fit[2].value - fit[1].value - innerPeakWidth) * fit[6].value
	innerPeakCentre = innerPeakStart + (innerPeakWidth / 2)
	simpleLog( "Center: " + str(innerPeakCentre))
	
	# 4. Calculate FWHM of inner peak
	#innerPeakHalfMax = topY - ((fit[0].value + fit[3].value) / 2)
	innerPeakHalfMax = fit[0].value + fit[3].value + (fit[4].value / 2)
	xVals = data.getInterpolatedX(data[0], data[1], innerPeakHalfMax)
	#simpleLog("x vals: " + str(xVals))
	if (len(xVals) == 2):
		simpleLog( "FWHM: " + str(xVals[1] - xVals[0]))
		dsX = DatasetFactory.createFromObject([xVals[0], xVals[1]])
		dsY = DatasetFactory.createFromObject([innerPeakHalfMax, innerPeakHalfMax])
		RCPPlotter.addPlot("Data Vector", dsX, dsY)
	else:
		simpleLog( "Cannot find inner peak FWHM")
	
	return innerPeakCentre
		
def movePeakCentre(centre, motor):
	"""
	Ask user whether to move motor to peak centre
	"""	
	simpleLog(motor.name + " currently at " + str(motor.getPosition()))
	move = InputCommands.requestInput("Move to peak center? (y/n)")
	if (move == 'y'):
		simpleLog("Moving to " + str(centre))
		motor(centre)
		simpleLog("[Done]")
	else:
		simpleLog("Motor not moved")

def getData(fileNo):
	"""
	Returns data given .dat file number. If file number 0, returns last created .dat file
	"""	
	data = ScanFileHolder()
	if (fileNo == 0):
		runs = NumTracker("tmp")
		fileNo = int(runs.getCurrentFileNumber())
	
	from gda.data import PathConstructor
		
	data.loadSRS(PathConstructor.createFromDefaultProperty() +"/"+ str(fileNo) + ".dat");
	
	
	return data
	
## TESTS:
def testStepFuncFitting(folder):
	"""
	Runs through each .dat file in folder, and attempts to fit step function...
	e.g testStepFuncFitting("/dls/i15/data/currentdir/")
	"""	
	for file in glob.glob( os.path.join(folder, '*.dat') ):
			data = ScanFileHolder()
			data.loadSRS(file)
			simpleLog( "Fitting file: " + file)
			pathUpToNumber =  file[len(folder):file.find(".")]
			fitStepFunction(int(pathUpToNumber))
			#sleep(1)
