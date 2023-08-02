from gda.device.detector import NXDetectorDataWithFilepathForSrs
from gda.configuration.properties import LocalProperties
from gdascripts.utils import caget, caput

def ct(ct_time = 0):
	if ct_time == 0 :
		ct_time = ct.defaultTime
	if not ( ct.use_pilatus or ct.use_excalibur) :
		print "No detectors enabled, please set ct.use_pilatus and/or ct.use_excalibur to true."
		return
	if ct.specWarning:
		print "This is not SPEC!"
		
	if ct.use_excalibur and LocalProperties.check("gda.beamline.auto.attenuation"):
		ct_select_atten()
	
	pos(ct.fastshutter, 1)
	if ct.use_excalibur :
		pos(exc_snap, ct_time)
	else :
		#Not needed if using exc as it's slow anyway
		sleep(ct.fsSleep)
	if ct.use_pilatus :
		pos(ct.pilatus_detector, ct_time)
	pos(ct.fastshutter, 0)
	
	if ct.use_excalibur :
		stats = dict(zip(exc_snap.getExtraNames(), exc_snap.readout()))
		print "Excalibur Total: " + str(int(stats['total'])) + "   Max: " + str(int(stats['max_val'])) + " (" + str(int(stats['max_x'])) + ", " + str(int(stats['max_y'])) + ")"
	if ct.use_pilatus :
		detectorReadout = ct.pilatus_detector.readout()
		if isinstance(detectorReadout, NXDetectorDataWithFilepathForSrs):
			detectorReadout = detectorReadout.toString().split('\t')
		print "Pilatus Total: " + str(detectorReadout[10]) + "  Max: " + str(detectorReadout[7]) + " (" + str(detectorReadout[5]) + "," + str(detectorReadout[6]) + ") Filename: " + ct.pilatus_detector.filename

	def ct_select_atten():
		caput("BL07I-EA-EXCBR-01:CAM:PausePolling", "1")
		# set single shot mode	
		caput('BL07I-OP-FILT-01:MODE', 'SINGLESHOT')
		# set timeout to 10s
		caput('BL07I-OP-FILT-01:TIMEOUT', '10')
		# clear error
		caput('BL07I-OP-FILT-01:ERROR:CLEAR', '1')
		# reset
		caput('BL07I-OP-FILT-01:RESET', '1')
		# wait for singleshot waiting
		while int(caget('BL07I-OP-FILT-01:STATE')) != 3:
			sleep(0.1)
		# start single shot
		caput('BL07I-OP-FILT-01:SINGLESHOT:START', '1')
	
		## run fast acquisition
		# set acquisition time
		caput('BL07I-EA-EXCBR-01:CAM:AcquireTime', '0.1')
		# set number of images
		caput('BL07I-EA-EXCBR-01:CAM:NumImages', '30')
		# set multiple Excalibur exposures
		caput('BL07I-EA-EXCBR-01:CAM:ImageMode', 'Multiple')
		# set Excalibur internal trigger
		caput('BL07I-EA-EXCBR-01:CAM:TriggerMode', 'Internal')
		# acquire
		pos(ct.fastshutter, 1)
		caput('BL07I-EA-EXCBR-01:CAM:Acquire', '1')
	
		# wait for the attenuators to be happy
		while int(caget('BL07I-OP-FILT-01:STATE')) != 4:
			sleep(0.1)
		pos(ct.fastshutter, 0)
		# stop detector
		caput('BL07I-EA-EXCBR-01:CAM:Acquire', 0)
	
		sleep(0.2)
	
		final_att = caget('BL07I-OP-FILT-01:ATTENUATION_RBV')
		print "Attenuation: " + final_att

ct.specWarning = False
ct.defaultTime = 1
ct.fsSleep = 0.5
ct.fastshutter = fs

ct.use_pilatus = False
ct.use_excalibur = True
ct.pilatus_detector = pil2stats

alias("ct")
