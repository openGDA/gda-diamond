from gdascripts.analysis.datasetprocessor.twod.TwodDataSetProcessor import TwodDataSetProcessor

from gda.analysis import DataSet


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
		yi, xi = ds.maxpos()
		return ( 5, 4, 3, 2);
