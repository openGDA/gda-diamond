
import math

from gda.jython.commands.GeneralCommands import run, alias
from gda.jython.commands.Input import requestInput

import scisoftpy as dnp








def m6qgfitting():
    m6Data=dnp.io.load("/dls/i06-1/data/2012/si7816-1/68918.dat", formats=['srs'], asdict=True);
    
    x, y=m6Data['m6qg'], m6Data['ca62sr'];
    
    #Normalize data
    yn=y/y.max();
    xn=dnp.arange(yn.size);
    
#    [mu, sigma, peak, gf] = fineGaussianFitting(y, "Plot 2");
    [mu, sigma, peak, gf] = fineGaussianFitting(y);

    print("To plot the fitted data." )
    dnp.plot._PVNAME="Plot 2" #To change the plot viewer panel (default is PLOT2)
    gf.plot()
    
#    y1=myGaussianFunc(mu, sigma, peak, [x]);
#    dnp.plot.line(x, [y, y1] ) # plot line of evaluated function

#    cPos=(dnp.abs(x-mu)).minPos()[0];
#    cX=x[cPos]
#    cY=y[cPos];
    
#    print("The centroid is: (%g, %g)" %(cX, cY) );

    return;

#To fit a Gaussian 1d data set
def fineGaussianFitting(data, plotPanel=None):
    nfactor = data.max();
    xn=dnp.arange(data.size)
    yn = data/nfactor;#Normalize the data
    
    #Rough estimate
    [mu0, sigma0, peak0, area0]=simpleFitGaussian(yn, xn);

    fwhm0=sigma0*(2.0*math.sqrt(2.0*math.log(2)));

    #Fine tune
    gf = dnp.fit.fit(dnp.fit.function.gaussian, xn, yn, [mu0, fwhm0, area0], [(0, yn.size), (0, 2*fwhm0), (0, 3*area0)], optimizer='global')
    [mu, fwhm, area]=gf.parameters;
    
    sigma = fwhm/(2.0*math.sqrt(2.0*math.log(2)));
    peak=area/(sigma*math.sqrt(2.0*math.pi));
    peak *=nfactor;

    if plotPanel is not None:
        dnp.plot._PVNAME=plotPanel #To change the plot viewer panel (default is PLOT2)
        gf.plot()
    
    return [mu, sigma, peak, gf];

def fitGaussian(data, x=None):
    if x is None:
        x=dnp.arange(data.size)
    
    gf = dnp.fit.fit(dnp.fit.function.gaussian, x, data, [1, 1, 1], [(0, 50), (0, 10), (1, 500)], optimizer='global')

    mu=gf.parameters[0];
    sigma = gf.parameters[1]/(2.0*math.sqrt(2.0*math.log(2)));
    A=gf.parameters[2]/(sigma*math.sqrt(2.0*math.pi));

    return [mu, sigma, A, gf];

def myGaussianFunc(mu, sigma, a, x, *arg):
    '''mu    -- centre parameter
       sigma -- sigma parameter
       a     -- peak parameter
       x -- list of coordinate datasets
    arg -- tuple of additional arguments
    '''
    return a*dnp.exp( -(x[0]-mu)*(x[0]-mu)/(2*sigma*sigma) );





########################
m6Data=dnp.io.load("/dls/i06-1/data/2012/si7816-1/68917.dat", formats=['srs'], asdict=True);

x, y=m6Data['m6qg'], m6Data['ca62sr'];

#Normalize data
yn=y/y.max();
xn=dnp.arange(yn.size);

#    [mu, sigma, peak, gf] = fineGaussianFitting(y, "Plot 2");
[mu0, sigma0, peak, gf] = fineGaussianFitting(y);

n=x.size;
a=(x[n-1] - x[0])/(n-1); b=x[0];
mu=a*mu0+b;
sigma=a*sigma0;

#One vertical line on the peak point:
#xx, yy=dnp.array([mu-1, mu+1]), dnp.array([0, peak]);
xx, yy=dnp.array([mu-1, mu, mu+1]), dnp.array([0, peak, 0]);
xxx, yyy=dnp.array([mu]), dnp.array([peak]);

#To find the closest data point to the peak;
cPos=(dnp.abs(x-mu)).minPos()[0];
cX, cY=x[cPos], y[cPos];

print("To plot the fitted data." )
x1=dnp.linspace(x[0], x[n-1], 500);
y1=myGaussianFunc(mu, sigma, peak, [x1]);

#Line plot does not work
#dnp.plot.line(x, [y, y1] ) # plot line of evaluated function
#dnp.plot.updateline(xx, yy)

dnp.plot.points(x, y, None, 5);
sleep(1);
dnp.plot.addpoints(x1, y1, None, 1)
sleep(1);
dnp.plot.addpoints(xxx, yyy, None, 10);


########################

