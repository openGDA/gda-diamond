from gda.device.scannable import TwoDScanPlotter
from gda.jython.commands.ScannableCommands import scan

def mapscan(
		outer_scannable, outer_start, outer_stop, outer_step,
		inner_scannable, inner_start, inner_stop, inner_step,
		detector, exposure):
	
	"""
	Starts a 2D scan with given parameters, creating/updating a plot view
	named after the detector in the scan.
	
	@param outer_scannable: The outer (or slow) axis
	@param outer_start: initial position of the outer axis
	@param outer_stop: final position of the outer axis
	@param outer_step: step size of the outer axis
			Always positive, even if the final position is more negative than the initial.
	@param inner_scannable: The inner (or fast) axis
	@param inner_start: initial position of the inner axis
	@param inner_stop: final position of the inner axis
	@param inner_step: step size of the inner axis
	@param detector: detector to expose at every scan point
	@param exposure: duration in seconds for which to exposure the detector at each scan point
	"""

	det_name = detector.getName()
	
	plotter = TwoDScanPlotter(name=det_name + "plotter",
							   plotViewname=det_name,
							   z_colName=det_name)
	
	if inner_stop < inner_start:
		inner_step *= -1
	
	if outer_stop < outer_start:
		outer_step *= -1

	plotter.setXArgs(inner_start, inner_stop, inner_step)
	plotter.setYArgs(outer_start, outer_stop, outer_step)
	
	scan(
		outer_scannable, outer_start, outer_stop, outer_step,
		inner_scannable, inner_start, inner_stop, inner_step,
		detector, exposure, plotter)
