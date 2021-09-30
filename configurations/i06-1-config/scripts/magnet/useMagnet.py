#New version of magnet control

from Diamond.PseudoDevices.SuperconductingMagnet import SuperconductingMagnetClass, ModeMagnetClass;
from Diamond.PseudoDevices.SuperconductingMagnet import CartesianMagnetClass, SphericalMagnetClass, SingleAxisMagnetClass;
from Diamond.PseudoDevices.Flipper import FlipperClass, DichroicFlipperClass
from i06shared import installation

if installation.isLive():
	#The root EPICS PV for the superconducting magnet
	magRootPV = 'BL06J-EA-MAG-01';
	print "-"*100
	print "Note: Use object name 'scm' for the Superconducting Magenet control";
	scm = SuperconductingMagnetClass('scm', magRootPV);
	
	print "Note: Use Pseudo device name 'magmode' for the Superconducting Magenet mode control";
	magmode = ModeMagnetClass('magmode', 'scm');
	
	print "Note: Use Pseudo device name 'magcartesian' for the Superconducting Magenet control in Cartesian coordinate";
	magcartesian = CartesianMagnetClass('magcartesian', 'scm');
	
	print "Note: Use Pseudo device name 'magspherical' for the Superconducting Magenet control in Spherical coordinate";
	magspherical = SphericalMagnetClass('magspherical', 'scm');
	
	print "Note: Use Pseudo device name 'magx, magy, magz, magrho, magth, magphi' for the Superconducting Magenet uniaxial control";
	magx = SingleAxisMagnetClass('magx', 'scm', SingleAxisMagnetClass.X);
	magy = SingleAxisMagnetClass('magy', 'scm', SingleAxisMagnetClass.Y);
	magz = SingleAxisMagnetClass('magz', 'scm', SingleAxisMagnetClass.Z);
	magrho = SingleAxisMagnetClass('magrho', 'scm', SingleAxisMagnetClass.RHO);
	magth  = SingleAxisMagnetClass('magth',  'scm', SingleAxisMagnetClass.THETA);
	magphi = SingleAxisMagnetClass('magphi', 'scm', SingleAxisMagnetClass.PHI);
	magdelay=scm.delay
	magtolerance=scm.tolerance
	magdelay(0.1)    # Tests suggest that with magtolerance set up, only a very short delay is needed.
	magtolerance(6.) # Given that the magnet goes +-6T mag moves will always return the demand position after magdelay.

print "Note: Use object name 'hyst2' for the hysteresis measurement with flipping magnet";
print "Usage: scan hyst2 -1 1 0.1";
print "To change magnet device : hyst2.setMagnet(magnetName='magz')";
print "To change energy setting: hyst2.setEnergy(energyName='rpenergy', startEnergy=700, endEnergy=750)"
print "To change detector:       hyst2.setCounters(counterName1='ca61sr', counterName2='ca62sr', counterName3='ca63sr', integrationTime=1)"


hyst2 = FlipperClass('hyst2', 'magz', 'denergy', 700, 750, 'ca61sr', 'ca62sr', 'ca63sr', 1);
hyst2.setMagnet(magnetName='magz');
hyst2.setEnergy(energyName='denergy', startEnergy=700, endEnergy=750);
hyst2.setCounters(counterName1='ca61sr', counterName2='ca62sr', counterName3='ca63sr', integrationTime=1);


print "Note: Use object name 'dhyst' for the hysteresis measurement with dichroitic flipping magnet";
dhyst = DichroicFlipperClass('dhyst', 'magz', 'denergy', 770, 777, 'iddpol', 'PosCirc', 'NegCirc' , 'ca61sr', 'ca62sr', 'ca63sr', 1);
#dhyst.setMagnet('magnet.magz');
#dhyst.setEnergy('denergy', startEnergy=700, endEnergy=750);
#dhyst.setCounters(counterName1='ca61sr', counterName2='ca62sr', counterName3='ca63sr', integrationTime=1);
#dhyst.setPolarisation('iddpol', pol1='PosCirc', pol2='NegCirc');

#dhyst = DichroicFlipperClass('dhyst2', 'dummyMotor1', 'dummyMotor2', 700, 750, 'dummyPol', 'PosCirc', 'NegCirc' , 'ca61sr', 'ca62sr', 'ca63sr', 1);

from math import exp, log

print "Create logValues, negLogValues and negPosLogValues generators. Help is available, e.g. help logValues"

def logValues(start, end, num, asymptote=1., inclusive=False):
	"""
	This function generates a non-linear sequence of values from start to end
	(optionally including the end value) using a logarithmic algorithm, so the
	gaps between points are much smaller near end than near start.

	Example usage:

	>>>scan motor logValues(start, end, num) detector time
	>>>logValues(6, 0, 5)
	(6.0, 4.192962712629476, 2.9301560515835217, 2.047672511079219, 1.4309690811052553)
	>>>logValues(0, 6, 5)
	(1.0, 1.4309690811052553, 2.047672511079219, 2.9301560515835217, 4.192962712629476)

	Options:

	Note that this algorithm defaults to an asymptote of 1, so with start
	values above 1 the sequence will only have values above 1, while with
	start values below 1 the sequence will only have values below 1.
	
	The 'asymptote' option allows you to change the asymptote. Compare the
	following use cases:
	
	>>>logValues(6, 0, 5, .1)
	(6.0, 2.6455806186651607, 1.1665161349761228, 0.5143520796755042, 0.22679331552660545)
	>>>logValues(6, 0, 5, .0001)
	(6.0, 0.6645398059489742, 0.07360219228178334, 0.008151931096059236, 0.0009028804514474343)

	By default, the list includes the start point, but doesn't include the
	end (which is standard python behaviour). To include the end point use
	inclusive=True. Compare:

	>>>logValues(6, 0, 5, inclusive=True)
	(6.0, 4.192962712629476, 2.9301560515835217, 2.047672511079219, 1.4309690811052553, 1.0)
	>>>logValues(0, 6, 5, inclusive=True)
	(1.0, 1.4309690811052553, 2.047672511079219, 2.9301560515835217, 4.192962712629476, 6.0)

	Usage notes:

		num must be at least 2
	"""
	if type(inclusive) != type(True):
		raise ValueError("inclusive must be a boolean, so either True or False")
	_reversed=(start<end)
	if _reversed:
		start,end=end,start
	# Validate input
	if start < 0:
		raise ValueError("start must be positive")
	# Ensure we generate enough points for a tuple scan
	if num < 2:
		raise ValueError("number of points must be at least 2")
	# Ensure we don't get integer divides
	asymptote=float(asymptote)
	start,end=start/asymptote,end/asymptote
	values=[exp(log(start)-(i*(log(start-end))/num))*asymptote for i in xrange(num+1)]
	# Ensure errors in the above don't result in start values different to the requested start value
	values[0]=start*asymptote
	if _reversed:
		values.reverse()
	if inclusive:
		return tuple(values)
	else:
		return tuple(values[0:-1])

def negLogValues(start, end, num, asymptote=1., inclusive=False):
	"""
	This function returns a negated version of a logValues sequence.

	>>>negLogValues(6, 0, 5)
	(-6.0, -4.192962712629476, -2.9301560515835217, -2.047672511079219, -1.4309690811052553)
	>>>negLogValues(0, 6, 5)
	(-1.0, -1.4309690811052553, -2.047672511079219, -2.9301560515835217, -4.192962712629476)
	>>>negLogValues(6, 0, 5, inclusive=True)
	(-6.0, -4.192962712629476, -2.9301560515835217, -2.047672511079219, -1.4309690811052553, -1.0)
	>>>negLogValues(6, 0, 5, .1, True)
	(-6.0, -2.6455806186651607, -1.1665161349761228, -0.5143520796755042, -0.22679331552660545, -0.1)

	For further information on options and usage, see negLogValues help.
	"""
	return tuple([-i for i in logValues(start, end, num, asymptote, inclusive)])

def negPosLogValues(start, end, numPositive, numNegative, asymptote=1., inclusive=False):
	"""
	This function generates a non-linear sequence of values from start to end
	around zero, using a logarithmic algorithm, so the gaps between points are
	much smaller closer to the asymptote. The start and end values must be either
	side of zero.

	The total number of points in the scan will be numPositive+numNegative+1 if
	inclusive=False otherwise numPositive+numNegative+3.

	Example:

	>>>negPosLogValues(6, -3, 4, 3)
	(6.0, 3.8336586254776353, 2.449489742783178, 1.565084580073287, 0.0, -1.4422495703074083, -2.080083823051904, -3.0)
	>>>negPosLogValues(6, -3, 4, 3, .1, True)
	(6.0, 2.1558246717785043, 0.7745966692414834, 0.2783157683713741, 0.1, 0.0, -0.1, -0.31072325059538597, -0.9654893846056303, -3.0)
	>>>negPosLogValues(-6, 6, 3, 3, inclusive=True)
	(-6.0, -3.301927248894627, -1.8171205928321397, -0.9999999999999998, 0.0, 0.9999999999999998, 1.8171205928321397, 3.301927248894627, 6.0)


	Usage notes:

		start and end must be either side of zero
		numPositive and numNegative must both be at least 2

	For further information on options and usage, see logValues help.
	"""
	# Validate input
	_reversed=(start<end)
	if _reversed:
		start,end,numPositive,numNegative=end,start,numNegative,numPositive
	if end >=0:
		raise ValueError("start and end must be on either side of zero")
	positiveValues=list(logValues(start, 0, numPositive, asymptote, inclusive))
	positiveValues.append(0.)
	negativeValues=list(negLogValues(-end, 0, numNegative, asymptote, inclusive))
	if _reversed:
		positiveValues.reverse()
		return tuple(negativeValues+positiveValues)
	else:
		negativeValues.reverse()
		return tuple(positiveValues+negativeValues)

cwAsymptote=.0001

def cw(start, end, num):
	"""
	This function generates a non-linear sequence of values from start to end
	around zero, using a logarithmic algorithm, so the gaps between points are
	much smaller closer to zero. The start and end values must be either
	side of zero, and num should be odd and must be at least 7.
	"""
	if num < 7:
		raise ValueError("number of points must be at least 7")
	numPosNeg = (num-3)/2
	correctedNum = numPosNeg*2+3
	if num != correctedNum:
		print "Number of points requested (%r) is not odd, rounding to %r points" % (num, correctedNum)
	return negPosLogValues(start, end, numPosNeg, numPosNeg, cwAsymptote, True)
