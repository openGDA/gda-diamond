from gda.jython.commands.ScannableCommands import createConcurrentScan
from gda.jython.commands.GeneralCommands import alias
from gdascripts.scan.pathscanCommand import pathscan

from gda.device.scannable import DummyScannable

snakeScannable = DummyScannable("snakeScannable")

def snakescan(*args):
	''' A more generalised scan that extends standard GDA scan syntax to support
		snake scan if input is "snscan smx 0 10 1 smy 0 5 1 analyser" is converted
		to a pathscan with a snake-like path.
	'''
	newargs = []
	scan_objects = []

	newargs.append(snakeScannable)

	iter_scan = createConcurrentScan([e for e in args])
	num_points = iter_scan.getNumberPoints()
	for det in iter_scan.getDetectors():
		newargs.append(det)
	# Flat out all scan objects first - order matters!
	while (iter_scan != None):
		for scan_object in iter_scan.getAllScanObjects():
			# avoid duplicates
			if (scan_object.getScannable() in [so.getScannable() for so in scan_objects]):
				continue
			# any scannable that needs to be moved
			if (scan_object.hasStart()):
				scan_objects.append(scan_object)
			# any scannable that is read-only
			else:
				if scan_object.getScannable() not in newargs:
					newargs.append(scan_object.getScannable())
		iter_scan = iter_scan.getChild()

	#Create pathscan points
	positions = [[] for _ in range(num_points)]
	cum_num_points = 1
	k = 0
	while k < len(scan_objects):
		npoints  = scan_objects[k].getNumberPoints()
		if npoints != 0:
			# eg: scan ... m2 0 3 1
			cum_num_points = cum_num_points*npoints
			step_every_n_points = (num_points//cum_num_points)
			# Construct arguments for pathgroup scan
			for i in range(num_points):
				step_for_current_point = (i//step_every_n_points) % npoints
				# Snake scan need to change direction every other cycle
				if ((i//step_every_n_points)//npoints%2==0):
					positions[i].append(scan_objects[k].getStart() + step_for_current_point*(scan_objects[k].getStep()))
				else:
					positions[i].append(scan_objects[k].getStart() + (npoints-step_for_current_point-1)*(scan_objects[k].getStep()))
			m = 1
			while ((k+m)<len(scan_objects) and (scan_objects[k+m].getNumberPoints() == 0)):
				# eg: scan ... m2 0
				# eg: scan ... m2 0 1
				if scan_objects[k+m].getStep() == None:
					step = 0
				else:
					step = scan_objects[k+m].getStep()
				[positions[i].append(scan_objects[k+m].getStart()+(i//step_every_n_points)*(step)) for i in range(num_points)]
				m += 1
			k += m
		else:
			k += 1
	pathscan(([e.getScannable() for e in scan_objects]), tuple(positions), *newargs)

alias("snakescan")