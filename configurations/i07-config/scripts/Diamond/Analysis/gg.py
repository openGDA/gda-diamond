import numpy as np;
import scipy as sp;
import pylab as pl;

from scipy import optimize;

def gaussian(height, center_x, center_y, width_x, width_y):
    """Returns a gaussian function with the given parameters"""
    width_x = float(width_x)
    width_y = float(width_y)
    return lambda x,y: height*np.exp( -(((center_x-x)/width_x)**2 + ((center_y-y)/width_y)**2)/2 )

def moments(data):
    """
    Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution by calculating its moments
    """
    total = data.sum()
    X, Y = np.indices(data.shape)
    x = (X*data).sum()/total
    y = (Y*data).sum()/total
    col = data[:, int(y)]
    width_x = np.sqrt( abs((np.arange(col.size)-y)**2*col).sum()/col.sum() )
    row = data[int(x), :]
    width_y = np.sqrt(abs((np.arange(row.size)-x)**2*row).sum()/row.sum())
    height = data.max()
    return height, x, y, width_x, width_y

def fitgaussian(data):
    """
    Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution found by a fit
    """
    
    #First to calculate the moments of the data to guess the initial parameters for an optimisation routine
    params = moments(data)
    errorfunction = lambda p: np.ravel(gaussian(*p)(*np.indices(data.shape)) - data)
    
    #Then use the least square method to fit the model
    p, success = sp.optimize.leastsq(errorfunction, params)
    
    return p;
   
def demo():
    # Create the gaussian data
    Xin, Yin = np.mgrid[0:201, 0:201]
    data = gaussian(3, 100, 100, 20, 40)(Xin, Yin) + np.random.random(Xin.shape)
    
    pl.matshow(data, cmap=pl.cm.gist_earth_r)
    
    params = fitgaussian(data)
    fit = gaussian(*params)
    
    pl.contour(fit(*np.indices(data.shape)), cmap=pl.cm.copper)
    ax = pl.gca()
    
    (height, x, y, width_x, width_y) = params
    
    pl.text(0.95, 0.05, """
                        x : %.1f
                        y : %.1f
                        width_x : %.1f
                        width_y : %.1f""" %(x, y, width_x, width_y),
            fontsize=16, horizontalalignment='right',
            verticalalignment='bottom', transform=ax.transAxes)
    
    pl.show()

demo()
