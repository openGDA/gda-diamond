
### Choose detector and peak2d processor here
#DETECTOR, PEAK2D = sincdet, sincdetpeak2d
DETECTOR, PEAK2D = ipp, peak2d                # IPP
#DETECTOR, PEAK2D = pil, pilpeak2d             # Pilatus 300k
#DETECTOR, PEAK2D = medipix, medipixpeak2d     # Medipix
#DETECTOR, PEAK2D = pcoedge, pcoedgepeak2d     # PCO.Edge


### Set roi here if required
#PEAK2D.setRoi(0, 0, 0, 0)  # (topleft_x, topleft_y, lowerright_x, lowerright_y) in pixels
#PEAK2D.setRoi(None)  # Use None to clear


### NOTE: Pressing 'Halt current scans/scripts' will halt the current scan early and allow the script to continue
### NOTE: Pressing 'STOP ALL' will stop the scan and the script


def _check_metric_valid(metric):
	supported_metrics = ('fwhmx', 'fwhmy', 'fwhmarea')
	if metric not in supported_metrics:
		raise Exception("metric must be one of: " + ', '.join(supported_metrics))


def go_focus_absolute(parameter, start, stop, step, metric, exposure_time=1):
	_check_metric_valid(metric)
	try:
		scan.yaxis = PEAK2D.name + '_' + metric
		print ">>> scan", parameter.name, start, stop, step, DETECTOR.name, exposure_time, PEAK2D.name
		scan(parameter, start, stop, step, DETECTOR, exposure_time, PEAK2D)
		go(minval)
	finally:
		scan.yaxis = None
		


def go_focus_centred(parameter, halfwidth, step, metric, exposure_time=1):
	_check_metric_valid(metric)
	try:
		cscan.yaxis = PEAK2D.name + '_' + metric
		print ">>> cscan", parameter.name, halfwidth, step, DETECTOR.name, exposure_time, PEAK2D.name
		cscan(parameter, halfwidth, step, DETECTOR, exposure_time, PEAK2D)
		go(minval)
	finally:
		cscan.yaxis = None
		
		

def go_focus_3orders(parameter, start, stop, step, metric, exposure_time=1):
	go_focus_absolute(parameter, start, stop, step, metric, exposure_time)
	go_focus_centred(parameter, step * 1.5, step / 5., metric)
	go_focus_centred(parameter, step * 1.5 / 5., step / 25., metric)


def go_focus_two_param_3orders(parameter1, p1_start, p1_stop, p1_step,
							   parameter2, p2_start, p2_stop, p2_step,
							   metric, exposure_time=1):
	
	go_focus_absolute(parameter1, p1_start, p1_stop, p1_step, metric, exposure_time)
	go_focus_absolute(parameter2, p2_start, p2_stop, p2_step, metric, exposure_time)

	go_focus_centred(parameter1, p1_step * 1.5, p1_step / 5., metric, exposure_time)
	go_focus_centred(parameter2, p2_step, p2_step * 1.5 / 5., metric, exposure_time)

	go_focus_centred(parameter1, p1_step / 10., p1_step * 1.5 / 25., metric, exposure_time)
	go_focus_centred(parameter2, p2_step / 10., p2_step * 1.5 / 25., metric, exposure_time)
	
	
# TODO: Check it keeps going when manually interrupted




