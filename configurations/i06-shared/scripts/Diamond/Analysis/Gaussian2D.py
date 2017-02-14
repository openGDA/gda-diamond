
import math
import scisoftpy as dnp


def gaussian2D(height, center_x, center_y, sigma_x, sigma_y):
	"""Returns a gaussian function with the given parameters"""
	sigma_x = float(sigma_x)
	sigma_y = float(sigma_y)
	return lambda x,y: height*dnp.exp( -(((center_x-x)/sigma_x*math)**2 + ((center_y-y)/sigma_y)**2)/2 )

def myGaussian2DFunc(height, center_x, center_y, sigma_x, sigma_y, xy, *arg):
	'''
		height	  --peak parameters
		centre_x,y	-- centre parameters
		sigma_x, y   -- sigma parameter
		x -- list of coordinate datasets
		arg -- tuple of additional arguments
	'''
	x=xy[0]; y=xy[1];
	sigma_x = float(sigma_x)
	sigma_y = float(sigma_y)
	return height*dnp.exp( -(((center_x-x)/sigma_x)**2 + ((center_y-y)/sigma_y)**2)/2 );

def moments(data):
	"""
	Returns (height, x, y, sigma_x, sigma_y)
	the gaussian parameters of a 2D distribution by calculating its moments
	"""
	total = data.sum()
	xyIndices = dnp.indices(data.shape)
	X=xyIndices[1]; Y=xyIndices[0];
	
	x = (X*data).sum()/total
	y = (Y*data).sum()/total

	row = data[int(y), :]
	sigma_x = math.sqrt(dnp.abs((dnp.arange(row.size)-x)**2*row).sum()/row.sum())

	col = data[:, int(x)]
	sigma_y = math.sqrt( dnp.abs((dnp.arange(col.size)-y)**2*col).sum()/col.sum() )
	
	height = data.max()
	return [height, x, y, sigma_x, sigma_y];

def mgrid(x, y):
	y0=[y]*len(x)
	Y=dnp.array(y0);


	x0=[x]*len(y);
	X=dnp.array( zip(*x0) )
	
	return X, Y;


def fitgaussian(data):
	"""
	Returns (height, x, y, sigma_x, sigma_y)
	the gaussian parameters of a 2D distribution found by a fit
	"""
	
	#First to calculate the moments of the data to guess the initial parameters for an optimisation routine
	params = moments(data)
	errorfunction = lambda p: np.ravel(gaussian(*p)(*np.indices(data.shape)) - data)
	
	#Then use the least square method to fit the model
	p, success = sp.optimize.leastsq(errorfunction, params)
	
	return p;


def fitGaussian2D(data, rangeFactor=0.1, xy=None):
	if xy is None:
		xyIndices = dnp.indices(data.shape)
		xy=[ xyIndices[1], xyIndices[0] ] ;

#	h0, xc0, yc0, xw0, yw0 = moments(data);
#	gf=dnp.fit.fit(myGaussian2DFunc, xy, data, [h0, xc0, yc0, xw0, yw0], [(4, 6), (80, 120), (80, 120), (10,30), (30,50)], optimizer='global')

	p0 = moments(data);
	rp=[(p*(1.0-rangeFactor), p*(1.0+rangeFactor)) for p in p0]
	gf=dnp.fit.fit(myGaussian2DFunc, xy, data, p0, rp, optimizer='local')
	print gf;
	
	height, center_x, center_y, sigma_x, sigma_y=gf.parameters;
	
	return [height, center_x, center_y, sigma_x, sigma_y];

def demo():
	#Demo
#	Xin, Yin = mgrid(range(201), range(201));
	Xin, Yin = dnp.meshgrid(range(201), range(201));
	data = gaussian2D(3, 100, 100, 20, 40)(Xin, Yin) + dnp.random.rand(*Xin.shape);
	
	pl.matshow(data, cmap=pl.cm.gist_earth_r)
	
	params = fitgaussian(data)
	fit = gaussian(*params)
	
	pl.contour(fit(*np.indices(data.shape)), cmap=pl.cm.copper)
	ax = pl.gca()
	
	(height, x, y, sigma_x, sigma_y) = params
	
	pl.text(0.95, 0.05, """
						x : %.1f
						y : %.1f
						sigma_x : %.1f
						sigma_y : %.1f""" %(x, y, sigma_x, sigma_y),
			fontsize=16, horizontalalignment='right',
			verticalalignment='bottom', transform=ax.transAxes)
	
	pl.show()


#run "Diamond/Analysis/Gaussian2D"

#Demo
#	Xin, Yin = mgrid(range(201), range(201));
Xin, Yin = dnp.meshgrid(range(101), range(51));
data = gaussian2D(5, 100, 50, 20, 10)(Xin, Yin);
#data = myGaussian2DFunc(5, 100, 50, 20, 10, [Xin, Yin]) + 0.5*dnp.random.rand(*Xin.shape);
dnp.plot.image(data)
#dnp.plot.surface(data)

params = moments(data)
print params;

xy=dnp.meshgrid(range(101), range(51))
ep=fitGaussian2D(data, 0.1, xy);
print ep;


#gf=dnp.fit.fit(myGaussian2DFunc, xy, data, list(params), [(4, 6), (80, 120), (40, 60), (10,30), (5,15)], optimizer='global')
#gf=dnp.fit.fit(myGaussian2DFunc, xy, data, list(params), [(4, 6), (80, 120), (40, 60), (10,30), (5,15)], optimizer='local')
#height, center_x, center_y, sigma_x, sigma_y=gf.parameters;
#print gf.parameters

#height, center_x, center_y, sigma_x, sigma_y = fitGaussian2D(data, xy);

#data1 = myGaussian2DFunc(height, center_x, center_y, sigma_x, sigma_y, [Xin, Yin])

#params = fitgaussian(data)
#fit = gaussian(*params)

#pl.contour(fit(*np.indices(data.shape)), cmap=pl.cm.copper)
#ax = pl.gca()

#(height, x, y, sigma_x, sigma_y) = params


#imageFile="/dls/i06-1/data/2012/cm5702-1/69659_CamPeemImage/campeem00089.png"
#imageFile="/dls/i06-1/data/2012/cm5702-1/69657_CamPeemImage/campeem00080.png"
#imageFile="/dls/i06-1/data/2012/cm5702-1/69658_CamC2Image/camc200015.png"




#im=dnp.io.load(imageFile, formats=['png'], asdict=True);
#dnp.plot.image(im[0]);
#dnp.plot.surface(im[0]);#Need lots of memory!




