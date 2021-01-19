import sys
import os # @UnusedImport
import time # @UnusedImport

from gda.configuration.properties import LocalProperties # @UnusedImport
from gda.device import DeviceException # @UnusedImport

from gda.px.model import ExtendedCollectRequestIO # @UnresolvedImport
from gda.px.model import ExtendedCollectRequests # @UnresolvedImport @UnusedImport

from component.DetectorController import detectorController
from component.shutter_control import shutterControl

from datacollection.config import ACTION_ALL, ACTION_EXPOSE, ACTION_PREPARE # @UnusedImport
from datacollection import factory
from datacollection import HandleCollectRequestSupport as hcr_support
from datacollection.CollectionMode import CollectionMode # @UnusedImport
from datacollection.DatasetMetadata import DatasetMetadata # @UnusedImport
from datacollection.RunMetadata import RunMetadata # @UnusedImport

from org.slf4j import LoggerFactory

# from framework import PilatusScripts # @UnresolvedImport mx-config/scripts
# from gdaserver import GONIODET, GONIOOMEGA, GONIOPHI, GONIOCHI


VAR_DIFFRACTION = "/dls_sw/b16/software/var_diffraction/"

DEF_ECR = "ecr.xml"
DEF_ECR_FOLDER = VAR_DIFFRACTION
DEF_ECR_PATH = VAR_DIFFRACTION + DEF_ECR

DEF_SAMPLE = "sample.xml"
DEF_SAMPLE_PATH = VAR_DIFFRACTION + DEF_SAMPLE

DEF_VISIT = "nt27909-2"
DEF_VISIT_FOLDER = "/dls/b16/data/2021/" + DEF_VISIT + "/"


class DiffractionOps():

	def __init__(self):
		self.detector_control = detectorController
		self.shutter_control = shutterControl
		self.scan_control = None
		self.sample_ops = SampleOps()
		self.logger = LoggerFactory.getLogger(__name__)


	def configure(self):
		self.sample_ops = SampleOps()


	def get_sample(self):
		if not self.sample_ops:
			self.sample_ops = SampleOps()
		return self.sample_ops


	def configure_detector(self, request): # and template
		self.detector_control.setupDetectorParameters(request.metadata, request.run_data)


	def configure_zebra(self, request, time_to_velocity=0.5, shutter_delay=0.03):
		self.detector_control.configureScanPosition(request.get_run_data(), time_to_velocity, shutter_delay)


	def run(self, request):
		responses = hcr_support.create_collect_responses(request.get_ecrs())
		crh = factory.create(request, responses, ACTION_EXPOSE)
		crh.run()


	def save_request(self, request, target_path=DEF_ECR_PATH):
		ExtendedCollectRequestIO.saveExtendedCollectRequestsToFile(request.get_ecrs(), target_path)


	def set_b16_defaults(self, request):
		run_data = request.get_run_data()
		run_data.setPhi(0.0)
		ecr = request.get_ecr()
		ecr.setAxisChoice("Omega")


	def stop(self):
		self.detector_control.stop()
		


class SampleOps():

	def __init__(self):
		pass


	def load(self, sam_path=DEF_SAMPLE_PATH):
		pass


	def save(self, sam_path=DEF_SAMPLE_PATH):
		pass


class Request():

	@staticmethod
	def create_request(prefix="test", run_number=1):
		visit_path = DEF_VISIT_FOLDER
		directory = "test"
		ecrs = hcr_support.create_standard_ecrs(visit_path, directory, prefix, run_number)
		return Request.load_ecrs(ecrs, 0)


	@staticmethod
	def load_file(ecr_path=DEF_ECR_PATH, index=0):
		ecrs = ExtendedCollectRequestIO.getExtendedCollectRequestsFromFile(ecr_path)
		return Request.load_ecrs(ecrs, index)


	@staticmethod
	def load_ecrs(ecrs, index=0):
		request = Request()
		request.ecrs = ecrs
		request.index = index
		ecr = Request.read_ecr(ecrs, index)
		request.metadata = hcr_support.prepare_metadata(ecr)
		request.run_data = hcr_support.prepare_run_data(ecr)
		return request


	@staticmethod
	def read_ecr(ecrs, index):
		return ecrs.getExtendedCollectRequests()[index]


	def __init__(self):
		self.ecrs = None
		self.index = 0
		self.ecr = None
		self.metadata = None
		self.run_data = None


	def get_ecr(self):
		return self.ecrs.getExtendedCollectRequests()[self.index]


	def get_ecrs(self):
		return self.ecrs


	def get_index(self):
		return self.index


	def get_metadata(self):
		return self.metadata


	def get_run_data(self):
		return self.run_data


	def set_ecrs(self, ecrs, index=0):
		self.ecrs = ecrs
		self.index = index
		self.ecr = Request.read_ecr(ecrs, index)
		self.metadata = hcr_support.prepare_metadata(self.ecr)
		self.run_data = hcr_support.prepare_run_data(self.ecr)
		return self


	def save(self, ecr_filename=DEF_ECR):
		self.save_by_path(DEF_ECR_FOLDER + ecr_filename)


	def save_by_path(self, ecrs_path=DEF_ECR_PATH):
		ExtendedCollectRequestIO.saveExtendedCollectRequestsToFile(self.get_ecrs(), ecrs_path)


	def show(self):
		print(self.get_ecr().toString())


	
from gda.factory import Finder
g_omega = Finder.find("GONIOO<EGA")
g_omega.motor.setMaxPosition(12000.)
g_omega.motor.setMinPosition(-12000.)

# define global objects
diff = DiffractionOps()
diff.configure()
request = Request.create_request(prefix="test", run_number=1)
diff.set_b16_defaults(request)

