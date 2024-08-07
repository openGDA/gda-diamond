import sys;
import gda.factory.Finder as Finder;
from gdascripts.messages import handle_messages
from gda.util.converters import IReloadableQuantitiesConverter

def getHelpTopics():
	return [ reloadLookupTables ]

def reloadLookupTablesEx(logInfo):
	"""version of reloadLookupTables that can be used in tests to only generate output when an error is detected"""
	ok = True
	controller = None
	prefix = "reloadLookupTables:"
	if( logInfo ):
		handle_messages.log(controller, prefix + " - started") 
		converters = Finder.listFindablesOfType(IReloadableQuantitiesConverter)
		for converter in converters:
			try:
				if( logInfo ):
					handle_messages.log(controller, prefix + "..." + converter.getName() )      
					converter.reloadConverter()
			except:
				type, exception, traceback = sys.exc_info()
				handle_messages.log(controller, prefix + " - ", type, exception, traceback, False)
				ok = False
	if( logInfo ):
		handle_messages.log(controller, prefix + " - completed")
	if( not ok):
		print "reloadLookupTables completed with error"
	return ok

def reloadLookupTables():
	"""reloads all lookup tables on the ObjectServer"""
	reloadLookupTablesEx(True)


class InterpolatedArray(object):
	"""An array-like object that provides interpolated values between set points."""
	def __init__(self, points):
		self.points = sorted(points)

	def __getitem__(self, x):
		if x < self.points[0][0] or x > self.points[-1][0]:
			raise ValueError
		lower_point, upper_point = self._GetBoundingPoints(x)
		return self._Interpolate(x, lower_point, upper_point)

	def _GetBoundingPoints(self, x):
		"""Get the lower/upper points that bound x."""
		lower_point = None
		upper_point = self.points[0]
		for point  in self.points[1:]:
			lower_point = upper_point
			upper_point = point
			if x <= upper_point[0]:
				break;
		return lower_point, upper_point

	def _Interpolate(self, x, lower_point, upper_point):
		"""Interpolate a Y value for x given lower & upper bounding points."""
		
		slope = (float(upper_point[1]-lower_point[1]) / (upper_point[0]-lower_point[0]));
		return lower_point[1] + (slope * (x-lower_point[0]));

	def reversePoints(self, points=None):
		if points is None:
			points=self.points;
		r=[];
		for p in points:
			r.append((p[1],p[0]));
		return tuple(r);

	def reverseTable(self):
		r=[];
		for p in self.points:
			r.append((p[1],p[0]));
		
		table = InterpolatedArray( tuple(r) );
		return table;

# Example
#tvPoints = [(0, 0), (2, 0), (4, 1.5), (6, 8.5), (8, 10), (10, 10)]
#tvTable = InterpolatedArray(tvPoints);
#vtTable = tvTable.reverseTable();
#print tvTable[1]
#print vtTable[7]