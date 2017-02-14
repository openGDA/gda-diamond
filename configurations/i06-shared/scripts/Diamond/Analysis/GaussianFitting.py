
import math

from Diamond.Analysis.FunctionalDevices import GaussianDevice

import scisoftpy as dnp

gaussianFun = lambda x: 20.+100*dnp.exp(-(10-x)**2/20.)

#Simple Gaussian fitting by calculating the moments of the distribution
#Only useful when the data are suitable
def simpleFitGaussian(data, x=None, plotPanel=None):
	if x is None:
		x=dnp.arange(data.size)

	mu=sum(x*data)/sum(data)
	sigma = math.sqrt(abs(dnp.sum((x-mu)**2*data)/dnp.sum(data)))
	peak=data.max();
	area=sum(data);
    
	if plotPanel is not None:
		print("To plot the fitted data")
		y1=myGaussianFunc(mu, sigma, peak, [x]);
		dnp.plot.line(x, [data, y1] ) # plot line of evaluated function

	return [mu, sigma, peak, area]

#To fit a Gaussian 1d data set
def fineGaussianFitting(data, x=None, plotPanel=None):
	nfactor = data.max(); #The squash factor on the Y axis
	a, b=1, 0;
	n=x.size;
	
	if x is not None:
		a=(x[n-1] - x[0])/(n-1); b=x[0];#The stretch factor along X axis 
		
	xn=dnp.arange(data.size)
	yn = data/nfactor;#Normalize the data
	

	#Rough estimate
	[mu0, sigma0, peak0, area0]=simpleFitGaussian(yn, xn);

	fwhm0=sigma0*(2.0*math.sqrt(2.0*math.log(2)));

	#Fine tune
#	gf = dnp.fit.fit(dnp.fit.function.gaussian, x, data, [1, 1, 1], [(0, 50), (0, 10), (1, 500)], optimizer='global')
	gf = dnp.fit.fit(dnp.fit.function.gaussian, xn, yn, [mu0, fwhm0, area0], [(0, yn.size), (0, 2*fwhm0), (0, 3*area0)], optimizer='global')
	[mu1, fwhm1, area1]=gf.parameters;
	
	sigma1 = fwhm1/(2.0*math.sqrt(2.0*math.log(2)));
	peak1=area1/(sigma1*math.sqrt(2.0*math.pi));
	
	mu=a*mu1+b;
	sigma=a*sigma1;
	peak=peak1*nfactor;

	if plotPanel is not None:
		dnp.plot._PVNAME=plotPanel #To change the plot viewer panel (default is PLOT2)
		gf.plot()

    
	return [mu, sigma, peak, gf];

#To fit the customised Gaussian with Offset function
def fitGaussianWithOffset(data, x=None):
	if x is None:
		x=dnp.arange(data.size)
	
	gf = dnp.fit.fit(myGaussianWithOffsetFunc, x, data, [1, 1, 1, 1], [(0, 50), (0, 10), (1, 500), (0,50)], optimizer='global');

	mu=gf.parameters[0];
	sigma = gf.parameters[1]/(2.0*math.sqrt(2.0*math.log(2)));
	A=gf.parameters[2]/(sigma*math.sqrt(2.0*math.pi));

	return [mu, sigma, A, gf];


def myGaussianFunc(mu, sigma, a, x, *arg):
	'''mu	-- centre parameter
	   sigma -- sigma parameter
	   a	 -- peak parameter
	   x -- list of coordinate datasets
	arg -- tuple of additional arguments
	'''
	return a*dnp.exp( -(x[0]-mu)*(x[0]-mu)/(2*sigma*sigma) );

def testMyGaussianFunc():
	t = dnp.linspace(0, 99, 100)# dataset of 40 coordinate points between 0 and 5
	dnp.plot.line(t, myGaussianFunc(10, 3, 10, [t]) ) # plot line of evaluated function
	

def myGaussianWithOffsetFunc(mu, sigma, a, o, x, *arg):
	'''mu	-- centre parameter
	   sigma -- sigma parameter
	   a	 -- peak parameter
	   x -- list of coordinate datasets
	arg -- tuple of additional arguments
	'''
	return o+a*dnp.exp( -(x[0]-mu)*(x[0]-mu)/(2*sigma*sigma) );

#A GDA scan to generate a Gaussian data set
def GuassianScan():
	gs=GaussianDevice('gs', 0, centre=10, width=2, height=100, offset=20, noise=1)
	#gs.noise=0.3
	scan gs 0 50 0.2
	
	#To load up data with axis name as dictionary key
	data=dnp.io.load(lastscan(), formats=['srs'], asdict=True);
	return data;

def fitdemo():

	#To generate some dataset for fitting
	data1=gaussianFun(dnp.arange(100));
	data2=GuassianScan();
	
	x=data2['x']
	y=data2['y']
	
	#To change the plot viewer panel (default is PLOT2)
	dnp.plot._PVNAME="Plot 2";
	dnp.plot.clear();

#	simpleFitGaussian(data1);
#	simpleFitGaussian(y, x);
	
#	gf=fitGaussian(y, x);
	gf=fitGaussianWithOffset(y, x);
	
	print gf[3];gf[3].plot();
	
def demoRealDataFitting():
	m6Data=dnp.io.load("/dls/i06-1/data/2012/si7816-1/68917.dat", formats=['srs'], asdict=True);
#	m6Data=dnp.io.load("/dls/i06-1/data/2012/si7816-1/68918.dat", formats=['srs'], asdict=True);
	
	x, y=m6Data['m6qg'], m6Data['ca62sr'];
	
#	[mu, sigma, peak, gf] = fineGaussianFitting(y, x, "Plot 2");
	[mu, sigma, peak, gf] = fineGaussianFitting(y, x);
	
#	One vertical line on the peak point:
#	xx, yy=dnp.array([mu-1, mu+1]), dnp.array([0, peak]);
	xx, yy=dnp.array([mu-1, mu, mu+1]), dnp.array([0, peak, 0]);
	xxx, yyy=dnp.array([mu]), dnp.array([peak]);
	
#	To find the closest data point to the peak;
	cPos=(dnp.abs(x-mu)).minpos()[0];
	cX, cY=x[cPos], y[cPos];
	
	print("To plot the fitted data." )
	x1=dnp.linspace(x[0], x[x.size-1], 500);
	y1=myGaussianFunc(mu, sigma, peak, [x1]);
	
	#Line plot does not work, 
	#dnp.plot.line(x, [y, y1] ) # plot line of evaluated function
	#dnp.plot.updateline(xx, yy)
	
	dnp.plot.points(x, y, None, 5);
	sleep(1);
	dnp.plot.addpoints(x1, y1, None, 1)
	sleep(1);
	dnp.plot.addpoints(xxx, yyy, None, 10);
	
	return [mu, sigma, peak, gf];


