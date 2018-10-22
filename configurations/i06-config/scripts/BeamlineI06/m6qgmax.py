
import math

from gda.jython.commands.GeneralCommands import run, alias
from gda.jython.commands.Input import requestInput

from gda.scan import PointsScan;

import scisoftpy as dnp
from Diamond.Utility.BeamlineFunctions import logger


run("Diamond/Analysis/GaussianFitting");
	
def queryYesNo(question, default="yes"):
	"""Ask a yes/no question via raw_input() and return their answer.
	
	"question" is a string that is presented to the user.
	"default" is the presumed answer if the user just hits <Enter>.
		It must be "yes" (the default), "no" or None (meaning
		an answer is required of the user).

	The "answer" return value is one of "yes" or "no".
	"""
	valid = {"yes":"yes",   "y":"yes",  "ye":"yes",
			 "no":"no",	 "n":"no"}
	if default == None:
		prompt = " [y/n] "
	elif default == "yes":
		prompt = " [Y/n] "
	elif default == "no":
		prompt = " [y/N] "
	else:
		raise ValueError("invalid default answer: '%s'" % default)

	while True:
		choice = requestInput(question + prompt).lower()
		if default is not None and choice == '':
			return default
		elif choice in valid.keys():
			return valid[choice]
		else:
			print("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")

def m6qgscan(q0):
#	scan m6qg q0-200 q0+200 20 ca62sr 0.5
	try:
		theScan = PointsScan([m6qg, q0-200, q0+200, 20, ca62sr, 0.5]);
		theScan.runScan();
	except:
		exceptionType, exception, traceback=sys.exc_info();
		logger.fullLog(None, "Error occurs when try to scan m6qg", exceptionType, exception, traceback, True);
	
#	To load up data with axis name as dictionary key
	data=dnp.io.load(lastscan(), formats=['srs'], asdict=True)
	return data

def m6qgmax():
	print("Move exit slit s6y to -6.5");
	s6y.moveTo(-6.5);
	
	q0=m6qg.getPosition();
	print("Current m6qg position: " + str(q0) );
	
	print("Scan m6qg ...");
	m6Data=m6qgscan(q0);
#	m6Data=GuassianScan();
	
	x, y=m6Data['m6qg'], m6Data['ca62sr'];
#	x, y=m6Data['x'], m6Data['y'];
	
#	[mu, sigma, peak, gf] = fineGaussianFitting(y, x, "Plot 1");
	[mu, sigma, peak, gf] = fineGaussianFitting(y, x);

#	One vertical line on the peak point:
#	xx, yy=dnp.array([mu-1, mu+1]), dnp.array([0, peak]);
	xx, yy=dnp.array([mu-1, mu, mu+1]), dnp.array([0, peak, 0]);
	xxx, yyy=dnp.array([mu]), dnp.array([peak]);
	
#	To find the closest data point to the peak;
	cPos=(dnp.abs(x-mu)).minPos()[0];
	cX, cY=x[cPos], y[cPos];

#	data according to the model	
	x1=dnp.linspace(x[0], x[x.size-1], 500);
	y1=myGaussianFunc(mu, sigma, peak, [x1]);
	
	print("To plot the fitted data." )
	dnp.plot.points(x, y, None, 5);
	sleep(1);
	dnp.plot.addpoints(x1, y1, None, 1)
	sleep(1);
	dnp.plot.addpoints(xxx, yyy, None, 10);
	
	print("The peak position is: (%g, %g)" %(mu, peak));
	ans = queryYesNo("Do you want to move m6qg to the estimated peak position?", "no")
	if ans is 'yes':
		m6qg.moveTo(mu);
		print "m6qg:" + str( m6qg.getPosition() );

	return;


alias("m6qgmax");



