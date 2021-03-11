from gda.factory import Finder
from gda.factory import FactoryException
# from gda.configuration.properties import LocalProperties
# from gda.configuration.properties.LocalProperties import isDummyModeEnabled
from gda.jython.scriptcontroller import ScriptControllerBase
# from gda.px import MxProperties
# from gda.px.util import ExtendedCollectRequestProcessor

from datacollection.CollectRequestHandler import CollectRequestHandler

# import hutch_helpers.cryojet_check
# import hutch_utilities
# import highestExistingFileMonitorUtils
# import mx_bridges.energy_wavelength
# import mx_bridges.flux_utils
# import mx_bridges.detector_template
# import det_wrapper
# import mx_bridges.mirror_check
# import mx_bridges.sample_control
# import hutch_helpers.beamstop_check

def create(request, responses, action):
	script_controller = ScriptControllerBase()
	script_controller_name = "CollectRequestController" # ExtendedCollectRequestProcessor.SCRIPT_CONTROLLER_NAME
	script_controller.setName(script_controller_name)

	if not script_controller:
		raise FactoryException("Unable to find script_controller named %s" % script_controller_name)
	
	crh = CollectRequestHandler(script_controller, request, responses, action)
	crh.configure()
	
# 	crh.activeDataCollectionScript = Finder.find(LocalProperties.get(MxProperties.GDA_DATACOLLECTION_SCRIPT))
	
# 	beamXYConverter = Finder.find("DetDistToBeamXYConverter")
# 	template_writer = mx_bridges.detector_template.real.CbfTemplateModuleTemplateWriter()
# 	# crh.detector_wrapper = det_wrapper.pilatus.PilatusDataCollectionDetectorWrapper(crh.detector, beamXYConverter, template_writer)
	
# 	crh.camera = Finder.find("PXCamera")
# 	crh.detz = Finder.find("DETZ")
# 	crh.cryojet_check = hutch_helpers.cryojet_check.noop.NoCryojetCheck()
# 	crh.hutch_shutter = None
# 	
# 	crh.skip_file_existence_check = MxProperties.skipFileExistenceCheck()
	crh.store_in_ispyb = False
	
#	crh.samp = Finder.find("samplexyz")
#	crh.gonchi = Finder.find("GONCHI")
	crh.gonphi = Finder.find("GONPHI")
	crh.gonomega = Finder.find("GONOMEGA")
	
# 	crh.highest_existing_file_monitor = highestExistingFileMonitorUtils.MxHighestExistingFileMonitor()
# 	
# 	crh.sample_event_service= Finder.find("sampleEventService")
# 	
# 	crh.beam_size_x_object = Finder.find("beamSizeX")
# 	crh.beam_size_y_object = Finder.find("beamSizeY")
# 	
# 	crh.sample_provider = Finder.find("sampleProvider")
# 	
# 	crh.energy_wavelength_bridge = mx_bridges.energy_wavelength.blwr.EnergyWavelengthBridge()
# 	
# 	crh.detector_flux_provider = mx_bridges.flux_utils.noop.NoOpFluxBridge()
# 	crh.ispyb_flux_provider = mx_bridges.flux_utils.flux_utils_module.FluxUtilsBridge()
	
# 	crh.energy_controller = None
	
# 	crh.auto_run_number_utils = Finder.find("autoRunNumberUtils")
	
# 	crh.mirror_check = mx_bridges.mirror_check.noop.NoOpMirrorCheck()
# 	
# 	crh.oscillation_axis = hutch_utilities.get_oscillation_axis()
# 	
# 	crh.gonio_rotation_vector = hutch_utilities.get_gonio_rotation_vector()
	
# 	crh.dummy_mode = isDummyModeEnabled()
	
# 	crh.sample_control_bridge = mx_bridges.sample_control.sc_module.SampleControlBridge()
# 	crh.sample_control_state = Finder.find("sample_control_state")
# 	
# 	crh.detector_shutter = None # hutch_helpers.det_shutter.noop.NoDetectorShutter()
# 	
# 	crh.pre_data_collection_prep = None # hutch_helpers.pre_dc_prep.noop.NoPreDataCollectionPrep()
# 	crh.post_data_collection_cleanup = None # hutch_helpers.post_dc_cleanup.b16.PostDataCollectionCleanup()

# 	crh.beamstop_check = hutch_helpers.beamstop_check.noop.NoBeamstopCheck()
	
# 	crh.in_plate_screen_mode = False
# 	crh.activate_hutch = None
# 	crh.spectrum_taker = None
# 	crh.user_options = None
# 	crh.use_zebra = True
	
	return crh
