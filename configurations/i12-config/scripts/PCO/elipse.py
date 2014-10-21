# to use 
# execfile("/dls_sw/i12/software/gda/config/scripts/PCO/elipse.py")
# to evaluate the results use
# evaluate(getPointsFromEPICS(36))
# should rotate the bead in a positive direction from 0 to 360 degree

import scisoftpy as dnp
import math
import random
import time
import os
from scisoftpy.jython.jycore import asDataset
from gda.epics.connection import EpicsController
from gda.epics.CAClient import caget
from gda.epics import CAClient

print "Importing elipse"


def elipse(x,y,a,b,angle,numberofpoints) :


	beta = -angle * (math.pi / 180.0)
	sinbeta = math.sin(beta)
	cosbeta = math.cos(beta)

	points = []
	
	step = 360.0 / numberofpoints

	for i in range(numberofpoints) :
		
		alpha = i * step *(math.pi / 180.0)
		sinalpha = math.sin(alpha)
		cosalpha = math.cos(alpha)

		xval = x+(a*cosalpha*cosbeta - b*sinalpha*sinbeta)
		yval = y+(a*cosalpha*sinbeta + b*sinalpha*cosbeta)
		points.append((xval,yval))

	return points

def compare_point(point, points) :

	# simple method to begin with
	minvalue = (point[0]-points[0][0])**2 + (point[1]-points[1][0])**2
	for p in points :
		dist = (point[0]-p[0])**2 + (point[1]-p[1])**2
		if (dist < minvalue) :
			minvalue = dist

	return minvalue 

def compare_points(point_list, points):
	distance = 0.0
	for point in point_list:
		distance += compare_point(point, points)

	return distance


from gda.analysis.utils.optimisation import ProblemDefinition

class ElipseProblem(ProblemDefinition) :
	
	def __init__(self,points,quality) :
		self.points = points
		self.quality = quality

	def getNumberOfParameters(self) :
		return 5

	def eval(self, parameters) :
		value = compare_points(self.points,elipse(parameters[0],parameters[1],parameters[2],parameters[3],parameters[4],self.quality))
		print value
		return value


from uk.ac.diamond.scisoft.analysis.optimize import NelderMead

def get_DataSets(points) :
	xvals = []
	yvals = []

	for p in points :
		xvals.append(p[0])
		yvals.append(p[1])

	#xx = dnp.asDataset(xvals) #was like this
	#yy = dnp.asDataset(yvals)

	xx = asDataset(xvals) # maybe moved to this
	yy = asDataset(yvals)

	return (xx,yy)

def getparamsfrompoints(points) :
	maxx = points[0][0]
	minx = points[0][0]
	maxy = points[0][1]
	miny = points[0][1]
	
	for p in points :
		if(maxx < p[0]) :
			maxx = p[0]
		if(minx > p[0]) :
			minx = p[0]
		if(maxy < p[1]) :
			maxy = p[1]
		if(miny > p[1]) :
			miny = p[1]

	sx = (maxx + minx) / 2.0
	sy = (maxy + miny) / 2.0
	sa = (maxx - minx) / 2.0
	sb = (maxy - miny) / 2.0
	
	return [sx,sy,sa,0.0,0.0]


def fit_elipse(points):

	print "firing up the GA!"

# 	nm = Neldermead()

	problem = ElipseProblem(points, 10)

	inputvals = getparamsfrompoints(points)

	problem.setParameterValues(inputvals) # = parameters
#
#  	result = nm.optimise(inputvals, problem, 0.0001)

	nmd  = NelderMead()   # new guy  used uk.ac.diamond.scisoft.analysis.optimize.NelderMead
	nmd.setAccuracy(0.0001)
	nmd.optimize(None, None, problem)
	result = problem.getParameterValues();

	data = get_DataSets(points)

	initial = elipse(inputvals[0],inputvals[1],inputvals[2],inputvals[3],inputvals[4],100)
	
# 	x,y,a,b,angle,numberofpoints
	vals = elipse(result[0],result[1],result[2],result[3],result[4],100)
	
	init = get_DataSets(initial)
	fit = get_DataSets(vals)

	dnp.plot.points(data[0],data[1])

	dnp.plot.addpoints(fit[0],fit[1])
	dnp.plot.addpoints(init[0],init[1])


	return result


def hunt_param(points, params, huntNumber, pert, steps, elipsePoints) :
	step = (pert*2.0)/steps
	stop = params[huntNumber]+pert
	params[huntNumber] = params[huntNumber]-pert
	minval = compare_points(points,elipse(params[0], params[1], params[2], params[3], params[4],elipsePoints))
	bestpos = params[huntNumber]
	params[huntNumber] += step	
	
	while params[huntNumber] <= stop :
		val = compare_points(points,elipse(params[0], params[1], params[2], params[3], params[4],elipsePoints))
		#print "Position %f value %f" % (params[huntNumber],val)
		if (val < minval) :
			minval = val
			bestpos = params[huntNumber]
		params[huntNumber] += step

	params[huntNumber] = bestpos

	return params


def full_hunt(points, params, huntNumber, elipsePoints, tollerence) :
	pert = tollerence*10.0
	steps = 10.0

	while pert >= tollerence :
		start = params[huntNumber]
		params = hunt_param(points,params,huntNumber,pert,steps,elipsePoints)
		if(abs(start-params[huntNumber]) > 0.99*pert) :
			pert = pert * 10.0
		else :
			pert = pert / 5.0

		#print "pert is %f value is %f" %(pert,params[huntNumber])

	return params
	


def plotelipse(points, params) :

	data = get_DataSets(points)
	
	vals = elipse(params[0],params[1],params[2],params[3],params[4],100)
	
	fit = get_DataSets(vals)

	dnp.plot.points(data[0],data[1],size=5)
	dnp.plot.addpoints(fit[0],fit[1])


def fit_itterate(points,params, elipsePoints,tollerence):
	params = full_hunt(points, params, 4, elipsePoints, tollerence)
	params = full_hunt(points, params, 3, elipsePoints, tollerence)
	params = full_hunt(points, params, 2, elipsePoints, tollerence)
	params = full_hunt(points, params, 1, elipsePoints, tollerence)
	params = full_hunt(points, params, 0, elipsePoints, tollerence)
		
	return params

def fit_full(points, tollerence):
	elipsePoints = 100
	params = getparamsfrompoints(points)
	
	fit = compare_points(points,elipse(params[0],params[1],params[2],params[3],params[4],elipsePoints))
	diff = tollerence*10.0
	
	while (diff > tollerence) :
		params = fit_itterate(points, params, elipsePoints,tollerence)
		newfit = compare_points(points,elipse(params[0],params[1],params[2],params[3],params[4],elipsePoints))
		diff = abs(fit-newfit)
		fit = newfit

	return params
	

def rotationDirection(points):
	maxx = points[0][0]
	minx = points[0][0]
	maxy = points[0][1]
	miny = points[0][1]
	maxxpos = 0
	minxpos = 0
	maxypos = 0
	minypos = 0
	
	for i in range(len(points)) :
		if(maxx < points[i][0]) :
			maxx = points[i][0]
			maxxpos = i
		if(minx > points[i][0]) :
			minx = points[i][0]
			minxpos = i
		if(maxy < points[i][1]) :
			maxy = points[i][1]
			maxypos = i
		if(miny > points[i][1]) :
			miny = points[i][1]
			minypos = i

	#print "maxXpos = ", maxxpos
	#print "minXpos = ", minxpos
	#print "maxYpos = ", maxypos
	#print "minYpos = ", minypos
	
	if (maxxpos > minxpos) :
		if(maxypos > minypos):
			return 1.0
		else :
			return -1.0
	else :
		if(maxypos > minypos):
			return -1.0
		else :
			return 1.0
	

def evaluate(points,tollerence=0.001) :
	result = fit_full(points,tollerence)
	#plotelipse(points, result)
	rotationDir = rotationDirection(points)
	x=result[0]
	rz=result[4]
	rx=(math.atan2(abs(result[3]), abs(result[2]))*(180.0/math.pi))*rotationDir
	print "Centre of rotation = ", x
	print "Z-Angle (ss1.rz)   = ", rz
	print "X-Angle (ss1.rx)   = ", rx
	return [x,rz,rx]

def getPoints(numberOfPoints):
	# get x values
	xcli=CAClient("BL12I-EA-CAM-01:TOMO:SCAN.D01DA")
	if not xcli.isConfigured():
		xcli.configure()
	x = xcli.cagetArrayFloat(numberOfPoints)
	
	#get y values
	ycli=CAClient("BL12I-EA-CAM-01:TOMO:SCAN.D02DA")
	if not ycli.isConfigured():
		ycli.configure()
	y = ycli.cagetArrayFloat(numberOfPoints)
	
	points=zip(x,y)
	
	return points

def getPointsFromEPICS(numberOfPoints):
	# get x values
	fin, fout = os.popen4("caget BL12I-EA-CAM-01:TOMO:SCAN.D01DA")
	result = fout.read()
	x = result.split(" ")[2:numberOfPoints+2]
	
	#get y values
	fin, fout = os.popen4("caget BL12I-EA-CAM-01:TOMO:SCAN.D02DA")
	result = fout.read()
	y = result.split(" ")[2:numberOfPoints+2]
	
	points = []
	for i in range(numberOfPoints):
		points += [(float(x[i]),float(y[i]))]
	
	return points

