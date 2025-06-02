from gda.device.detector import NXDetectorDataWithFilepathForSrs
from gda.configuration.properties import LocalProperties
from gdascripts.utils import caget, caput
from gdascripts.installation import isLive
from gdaserver import exc_pva, eig_pva, excalibur_stats_verbose, eiger_stats_verbose, ex_mask, ei_mask
from threading import Timer

# PVA snapper
try:
	from odin_detector_snapper import ExcPvaSnapper, EigPvaSnapper
	ex_snap = ExcPvaSnapper("ex_snap", exc_pva.getCollectionStrategy(),exc_pva.getAdditionalPluginList()[0].getNdPva(), excalibur_stats_verbose, "Excalibur", ex_mask)
	ei_snap = EigPvaSnapper("ei_snap", eig_pva.getCollectionStrategy(),eig_pva.getAdditionalPluginList()[0].getNdPva(), eiger_stats_verbose, "Eiger", ei_mask)
	from ad_detector_snapper import p2_snap, p3_snap
except Exception as e:
	print("Error setting up detector snappers", e)

def ct(ct_time = 0):

	def readout_det(detector, name):
		stats = dict(zip(detector.getExtraNames(), detector.readout()))
		print name +" Total: " + str(int(stats['total'])) + "   Max: " + str(int(stats['max_val'])) + " (" + str(int(stats['max_x'])) + ", " + str(int(stats['max_y'])) + ")"

	def ct_select_atten():
		caput("BL07I-EA-EXCBR-01:CAM:PausePolling", "1")
		# set single shot mode	
		caput('BL07I-OP-FILT-01:MODE', 'MANUAL')
		sleep(0.2)
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

	def check_shutter_closed() :
		if ct.fastshutter.getPosition() > 0.5 :
			print "Closing fastshutter as ct scan has not finished in a reasonable time."
			pos(ct.fastshutter, 0)

	if ct_time == 0 :
		ct_time = ct.defaultTime
	if not ( ct.p2 or ct.ex or ct.p3 or ct.ei ) :
		print "No detectors enabled, please set ct.p2, ct.p3, ct.ex and/or ct.ei to True."
		return
	if ct.specWarning:
		print "This is not SPEC!"

	panic_timer = Timer(ct_time + ct.fsSleep + 10, check_shutter_closed)
	panic_timer.start()

	if ct.ex and LocalProperties.check("gda.beamline.auto.attenuation"):
		ct_select_atten()

	pos(ct.fastshutter, 1)
	if ct.ex :
		pos(ex_snap, ct_time)
	else :
		#Not needed if using exc as it's slow anyway
		sleep(ct.fsSleep)
	if ct.ei :
		pos(ei_snap, ct_time)
	if ct.p2 :
		pos(p2_snap, ct_time)
	if ct.p3 :
		pos(p3_snap, ct_time)
	pos(ct.fastshutter, 0)
	panic_timer.cancel()

	if ct.ex :
		readout_det(ex_snap, "Excalibur")
	if ct.ei :
		readout_det(ei_snap, "Eiger")
	if ct.p2 :
		readout_det(p2_snap, "Pilatus 2")
	if ct.p3 :
		readout_det(p3_snap, "Pilatus 3")

ct.p2, ct.p3, ct.ex, ct.ei = False, False, True, False

def ct_detectors(*detector_list):	#Need to make it interpret this as a list however many entries there are.
	def print_detectors() :
		printout = "Detectors enabled for ct: "
		if ct.p2 : printout += "pilatus 2, "
		if ct.p3 : printout += "pilatus 3, "
		if ct.ex : printout += "excalibur, "
		if ct.ei : printout += "eiger"
		if not (ct.p2 or ct.p3 or ct.ex or ct.ei) : printout += "none"
		print printout

	if len(detector_list) == 0 :
		print_detectors()
		return

	available_detectors = ["p2", "p3", "ex", "ei", "p2_snap", "p3_snap", "ex_snap", "ei_snap"]
	found=False

	for det in detector_list :
		if det in available_detectors :
			found=True
			break

	if found :
		ct.p2 = "p2" in detector_list or  "p2_snap" in detector_list
		ct.p3 = "p3" in detector_list or  "p3_snap" in detector_list
		ct.ex = "ex" in detector_list or  "ex_snap" in detector_list
		ct.ei = "ei" in detector_list or  "ei_snap" in detector_list
		print_detectors()
	else :
		print "Only ex (ex_snap), ei (ei_snap), p2 (p2_snap) and p3 (p3_snap) are compatible with ct command."

alias("ct")
alias("ct_detectors")

ct.specWarning = False
ct.defaultTime = 1
ct.fsSleep = 0.5
ct.fastshutter = fs

if isLive() and LocalProperties.get("gda.active.diffractometer.mode") == "eh2" :
	ct.p3=True
	ct.ex=False