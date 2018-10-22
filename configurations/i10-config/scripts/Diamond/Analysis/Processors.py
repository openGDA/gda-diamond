from gdascripts.analysis.datasetprocessor.twod.TwodDataSetProcessor import TwodDataSetProcessor
#from TwodDataSetProcessor import TwodDataSetProcessor
from gda.analysis import ScanFileHolder

class DummyTwodPorcessor(TwodDataSetProcessor):
	def __init__(self, name='dummy',
				labelList=('a','b','c', 'd'),
				keyxlabel='a', 
				keyylabel='b', 
				formatString='DummyValue %f,%f (a, b) is %f (c). %f (d)'
				):
		TwodDataSetProcessor.__init__(self, name, labelList, keyxlabel, keyylabel, formatString)
    
	def _process(self, ds, dsxaxis, dsyaxis):
		dsysize, dsxsize = ds.dimensions
		#assert(dsyaxis.dimensions[0]==dsysize)		
		#assert(dsxaxis.dimensions[0]==dsxsize)
		#assert(dsyaxis is None)		# STUB
		#assert(dsxaxis is None)		# STUB
		sum = ds.sum()
		maxval = ds.max()
		yi, xi = ds.maxPos()
		return ( 5, 4, 3, 2);



class MinMaxSumMeanDeviationProcessor(TwodDataSetProcessor):
	def __init__(self, name='MinMaxMeanSumDeviation',
				 labelList=('minx', 'miny', 'minval', 'maxx','maxy','maxval', 'sum', 'mean', 'std'),
				 keyxlabel='maxx', 
				 keyylabel='maxy', 
				 formatString='Min: %f (minval) at %f,%f (minx,miny); Max: %f (maxval) at %f,%f (maxx,maxy); Sum: %f (sum), Mean: %f (mean), STD: %f (std)'
				 ):
		TwodDataSetProcessor.__init__(self, name, labelList, keyxlabel, keyylabel, formatString)
	
	def _process(self, ds, dsxaxis, dsyaxis):
		dsysize, dsxsize = ds.dimensions
		mean=ds.mean();
		std=ds.std();
		sum = ds.sum();
		
		minval = ds.min();
		y0, x0 = ds.minPos();
		
		maxval = ds.max()
		y1, x1 = ds.maxPos()
		# interpolate
#		sfh = ScanFileHolder()
#		dsxi = DataSet.arange(dsxsize)
#		dsyi = DataSet.arange(dsysize)
#		y = sfh.interpolatedX(dsyaxis, dsyi, yi)
#		y = sfh.interpolatedX(dsxaxis, dsxi, yi)		
#		x = dsyaxis[xi]		
		return (x0, y0, minval, x1, y1, maxval, sum, mean, std);
