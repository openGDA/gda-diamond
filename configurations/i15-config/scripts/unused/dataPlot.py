from gda.analysis import ScanFileHolder
def dp():
	"""
	Plot results in plot window.
	"""
	data = ScanFileHolder()
	data.loadSRS()
	data.plot(0,1)
	return

