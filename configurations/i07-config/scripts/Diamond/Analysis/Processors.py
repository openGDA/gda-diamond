from gdascripts.analysis.datasetprocessor.twod.TwodDataSetProcessor import \
	TwodDataSetProcessor
import scisoftpy as dnp


class DummyTwodPorcessor(TwodDataSetProcessor):
	def __init__(self, name='dummy',
				labelList=('a','b','c', 'd'),
				keyxlabel='a', 
				keyylabel='b', 
				formatString='DummyValue %f,%f (a, b) is %f (c). %f(d)'
				):
		TwodDataSetProcessor.__init__(self, name, labelList, keyxlabel, keyylabel, formatString)

	def _process(self, ds, dsxaxis, dsyaxis):
		#assert(dsyaxis.dimensions[0]==dsysize)		
		#assert(dsxaxis.dimensions[0]==dsxsize)
		#assert(dsyaxis is None)		# STUB
		#assert(dsxaxis is None)		# STUB
# 		sum = ds.sum()
# 		maxval = ds.max()
# 		yi, xi = ds.maxpos() ### Broken since 8.34
		return ( 5, 4, 3, 2);



class MinMaxSumMeanDeviationProcessor(TwodDataSetProcessor):
	def __init__(self, name='MinMaxMeanSumDeviation',
				 labelList=('minx', 'miny', 'minval', 'maxx','maxy','maxval', 'mean', 'std', 'sum'),
				 keyxlabel='maxx', 
				 keyylabel='maxy', 
				 formatString='Min: %f (minval) at %f,%f (minx,miny); Max: %f (maxval) at %f,%f (maxx,maxy); Mean: %f (mean), STD: %f (std), Sum: %f(sum)'
				 ):
		TwodDataSetProcessor.__init__(self, name, labelList, keyxlabel, keyylabel, formatString)
	
	def _process(self, ds, dsxaxis, dsyaxis):
		ds = dnp.array(ds)
		
		mean=ds.mean();
		std=ds.std();
		sum = ds.sum();
		
		minval = ds.min();
		yindexes, xindexes = dnp.nonzero(ds == minval)
		# take the first
		x_minpos = xindexes[0]
		y_minpos = yindexes[0]
		
		
		
		maxval = ds.max()
		yindexes, xindexes = dnp.nonzero(ds == maxval)
		# take the first
		x_maxpos = xindexes[0]
		y_maxpos = yindexes[0]
		# interpolate
#		sfh = ScanFileHolder()
#		dsxi = dnp.arange(dsxsize)
#		dsyi = dnp.arange(dsysize)
#		y = sfh.interpolatedX(dsyaxis, dsyi, yi)
#		y = sfh.interpolatedX(dsxaxis, dsxi, yi)		
#		x = dsyaxis[xi]		
		return (x_minpos, y_minpos, minval, x_maxpos, y_maxpos, maxval, mean, std, sum);


class SumProcessor(TwodDataSetProcessor):
	def __init__(self, name='Sum',
				 labelList=('sum',),
				 keyxlabel='sum', 
				 keyylabel='sum', 
				 formatString='Sum: %f(sum)'
				 ):
		TwodDataSetProcessor.__init__(self, name, labelList, keyxlabel, keyylabel, formatString)
	
	def _process(self, ds, dsxaxis, dsyaxis):
		sum = ds.sum();
		
		return (sum,);
