
from gda.device.scannable import ScannableBase

import math
import random


class SimpleDummyDevice(ScannableBase):
	def __init__(self, name, initialValue):
		self.name = name
		self.currentposition = initialValue
		self.setInputNames(['x'])
		self.setOutputFormat(['%.4f'])

	def isBusy(self):
		return False

	def getPosition(self):
		return self.currentposition

	def asynchronousMoveTo(self, position):
		self.currentposition = position

class XYFunctionDevice(SimpleDummyDevice):
	"""
	This class is a scannable device which returns the value of a user defined function at each sampled point in the scan.
	
	Example usage: 
	>>>def myFun(x):
	>>>        y=x*x;
	>>>
	>>>sxy = XYFunctionDevice("sxy", myFun)
	
	Constructor: def __init__(self, name, func)    
	"""
	def __init__(self, name, initialValue, func):
		SimpleDummyDevice.__init__(self, name, initialValue);
		
		self.func = func;
		self.setInputNames(['x'])
		self.setExtraNames(['y'])
		self.setOutputFormat(['%.4f', '%.4f'])

	def getPosition(self):
		x = self.currentposition
		y = self.func(x)
		return [ x, y ]


class GaussianDevice(SimpleDummyDevice):
	"""
	This class is a scannable device which returns the value of a Gaussian at each sampled point in the scan.
	
	The user can define 4 optional parameters of the Gaussian
	
	- centre (default=0)
	- width (Full Width at Half Maximum or FWHM, default=1)
	- height (default=1)
	- noise level (fraction of the true value; default=0)
	
	Note: FWHM = 2*sqrt(2*ln(2))*sigma 
	
	Example usage: 
	>>>sg = GaussianDevice("sg", 0.0)
	>>>sg = GaussianDevice("sg", 0.0, centre=3.0)
	>>>sg = GaussianDevice("sg", 0.0, centre=3.0, width=0.5)
	>>>sg = GaussianDevice("sg", 0.0, centre=3.0, width=0.5, height=2)
	>>>sg = GaussianDevice("sg", 0.0, centre=3.0, width=0.5, height=2, noise=0.1)
	
	Constructor: def __init__(self, name, initialValue, centre=0, width=1, height=1, noise=0):    
	"""
	
	def __init__(self, name, initialValue, centre=0, width=1, height=1, offset=0, noise=0):
		SimpleDummyDevice.__init__(self, name, initialValue);
		
		self.setInputNames(['x'])
		self.setExtraNames(['y'])
		self.setOutputFormat(['%.4f', '%.4f'])
		
		# Gaussian-specific parameters
		setattr(self, "centre", centre);
		print "centre: " + str(getattr(self, "centre"));
		
		setattr(self, "width", width);
		print "width: " + str(getattr(self, "width"));
		
		setattr(self, "height", height);
		print "height: " + str(getattr(self, "height"));
		
		setattr(self, "offset", offset);
		print "offset: " + str(getattr(self, "offset"));
		
		setattr(self, "noise", noise);
		print "noise: " + str(getattr(self, "noise"));
		
		setattr(self, "sigma", width*1.0/(2.0*math.sqrt(2.*math.log(2.0))));
		print "sigma: " + str(getattr(self, "sigma"))
		# printParameters(self)

	def printParameters(self):
		print "parameters for Gaussian scannable:"
		print "centre: "+ str(getattr(self, "centre"))
		print "width: " + str(getattr(self, "width"))
		print "sigma: " + str(getattr(self, "sigma")) 
		print "height: "+ str(getattr(self, "height"))
		print "offset: "+ str(getattr(self, "offset"))
		print "noise: " + str(getattr(self, "noise"))


	def getPosition(self):
		x = self.currentposition
		centre = getattr(self, "centre");
		sigma = getattr(self, "sigma");
		height = getattr(self, "height");
		noise = getattr(self, "noise");
		offset = getattr(self, "offset");
		pure_y=offset + math.exp( -(x-centre)**2/(2*sigma**2) ) * height;
		y = (pure_y )* ( 1+(random.random()-0.5)*noise )
		return [x, y]


class GaussianWidthDevice(ScannableBase):
	"""
	This class is a scannable device which takes a reference to a Gaussian device instance,
	and sets the width parameter of the reference Gaussian device to current value
	
	Example usage: 
	>>>sgw = GaussianWidthDevice("sgw", 0.0, sg)
	
	where "sg" is an existing instance of the ScannableGaussian device
	"""
	
	def __init__(self,name,gaussian):
		self.name = name
		self.gaussian = gaussian
		self.setInputNames(['width'])
		self.setExtraNames([])
		self.setOutputFormat(['%.4f'])

	def isBusy(self):
		return False

	def getPosition(self):
		return self.gaussian.getWidth()

	def asynchronousMoveTo(self, new_position):
		self.gaussian.setWidth(new_position)
    

class SineDevice(SimpleDummyDevice):
	"""
	This class is a scannable device which returns the value of a sine at each sampled point in the scan.
	
	The user can optionally define 4 optional parameters of the sine:
	
	- period (default=1.0)
	- phase (default=0.0)
	- y_offset (displacement of the sine wave on the y-axis; default=0.0)
	- noise level (fraction of the true value; default=0.0)
	
	Example usage: 
	>>>ss = SineDevice("ss", 0.0)
	>>>ss = SineDevice("ss", 0.0, period=0.5)
	>>>ss = SineDevice("ss", 0.0, phase=0.2, y_offset=1.5)
	>>>ss = SineDevice("ss", 0.0, period=3.0, noise=0.1)
	>>>ss = SineDevice("ss", 0.0, period=2.0, magnitude=2.0, phase=0.5, y_offset=1.0, noise=0.1)
	
	Constructor: def __init__(self, name, initialValue, period=1.0, magnitude=1.0, phase=0.0, y_offset=0.0, noise=0.0):    
	"""
	
	def __init__(self, name, initialValue, period=1.0, magnitude=1.0, phase=0.0, y_offset=0.0, noise=0.0):
		SimpleDummyDevice.__init__(self, name, initialValue);
		
		self.period = period
		self.phase = phase
		self.y_offset = y_offset
		self.noise = noise
		self.magnitude = magnitude
		
		self.setInputNames(['x'])
		self.setExtraNames(['y'])
		self.setOutputFormat(['%.4f', '%.4f'])
		
		
	def getPosition(self):
		x =  self.currentposition;
		y = self.y_offset + self.magnitude * math.sin((x-self.phase) / self.period) + ((random.random()-0.5)*self.noise)
		return [ x, y ]


class RandomDevice(SimpleDummyDevice):
	"""
	This class is a scannable device which returns a random number at each sampled point in the scan.
	
	Example usage: 
	>>>sr = RandomDevice("sr", 0.0)
	Constructor: def __init__(self, name, initialValue):    
	"""
	def __init__(self, name, initialValue):
		SimpleDummyDevice.__init__(self, name, initialValue);
		
		self.setInputNames(['x'])
		self.setExtraNames(['y'])
		self.setOutputFormat(['%.4f', '%.4f'])
		
		
	def getPosition(self):
		return [ self.currentposition, random.random() ]


class RandomRangeDevice(RandomDevice):
	"""
	This class is a scannable device which randomly return an element from a range at each sampled point in the scan.
	
	Example usage: 
	>>>srr = RandomRangeDevice("sr", 5)
	Constructor: def __init__(self, name, initialValue):    
	"""
	def __init__(self, name, initialValue):
		RandomDevice.__init__(self, name, initialValue);
		self.randomRange = initialValue

	def getPosition(self):
		x = self.currentposition
		y = random.randrange(self.randomRange)
		return [ x, y ]



class RandomGaussianDevice(RandomDevice):
	"""
	This class is a scannable device which returns an random number that follows the Gaussian distribution. 
	
	The user can define two optional parameters: mu is the mean, and sigma is the standard deviation.
	
	- mu (default=0)
	- sigma (default=1)
	
	Example usage: 
	>>>srg = RandomGaussianDevice("srg", 0, 2)
	
	Constructor: def __init__(self, name, initialValue, mu=0, sigma=1):    
	"""
	
	def __init__(self, name, initialValue, mu=0, sigma=1):
		RandomDevice.__init__(self, name, initialValue);
		# GaussianDev-specific values
		self.mu = mu
		self.sigma = sigma

	def getPosition(self):
		x = self.currentposition
		y = random.gauss(self.mu, self.sigma)
		return [ x, y ]


class RandomExponentialDevice(RandomDevice):
	"""
	This class is a scannable device which returns an random number that follows the Exponential distribution. 
	
	The user can an optional nonzero parameter of the lambda called lambd, which is 1.0 divided by the desired mean:
	
	- lambd (default=0.25)
	
	The returned values range from 0 to positive infinity if lambd is positive, and from negative infinity to 0 if 
	lambd is negative.
	
	Example usage: 
	>>>sre = RandomExponentialDevice("sre", 1)
	
	Constructor: def __init__(self, name, initialValue, lambd=0.25):    
	"""
	
	def __init__(self, name, initialValue, lambd=0.25):
		RandomDevice.__init__(self, name, initialValue);
		# ExponentialDev-specific values
		self.lambd = lambd

	def getPosition(self):
		x = self.currentposition
		y = random.expovariate(self.lambd)
		return [ x, y ]




