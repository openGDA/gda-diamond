from contextlib import contextmanager
from gda.configuration.properties import LocalProperties
from gda.data.metadata import GDAMetadataProvider
from gda.factory import Finder
from gda.jython import InterfaceProvider
from gda.jython.commands.GeneralCommands import add_reset_hook
from gda.px.datamodel import ExperimentType
from gda.util.osgi import OsgiJythonHelper
from java.sql import Timestamp
from java.util import Optional
from org.slf4j import LoggerFactory
from re import findall
from time import mktime, localtime
from uk.ac.diamond.ispyb.api import IspybDataCollectionFactoryService, DataCollectionGroup
import os
import scisoftpy as dnp

class IspybDataCollectionApiUtils(object):

	@staticmethod
	def exposeDetectorCheck(expectedDetector): # https://jira.diamond.ac.uk/browse/I15-846
		from localStationScripts.user_commands import _exposeDetector
		try:
			det = _exposeDetector().name
			if det == expectedDetector:
				return
			raise ValueError("exposeDetector {} is not the expected detector {}\n{}\n{}".format(
				det, expectedDetector,
				"Single crystal experiments require cbf data, without it, processing will fail.",
				"To use the expected detector run exposeDetector='{}' and add it to localStationUser.py"))
		except Exception as e:
			logger = LoggerFactory.getLogger("exposeDetectorCheck")
			logger.warn(e.message, e)
			print e.message

	@staticmethod
	def isDummy():
		mode = str(LocalProperties.get(LocalProperties.GDA_MODE))
		if mode not in ("live", "dummy"):
			raise ValueError("gda.mode LocalProperty (perhaps via a System property) must be 'live' or 'dummy' not:", mode)
		return mode=="dummy"

	@staticmethod
	def sqlTime():
		return Timestamp(int(mktime(localtime()))*1000)

	@staticmethod
	def beamlinePrefixedLocalProperty(suffix):
		return LocalProperties.get(LocalProperties.get(LocalProperties.GDA_BEAMLINE_NAME) + "." + suffix)


class IspybDataCollectionApiConnector(IspybDataCollectionApiUtils):
	logger = None
	dbs = None

	# Singleton implementation

	_instance = None

	def __init__(self):
		raise RuntimeError('Call instance() instead')

	@classmethod
	def instance(cls):
		if cls._instance is None:
			cls._instance = cls.__new__(cls)
			# Put any initialization here.
			cls.logger = LoggerFactory.getLogger("IspybDataCollectionApiConnector")
			cls.logger.debug("Singleton instance created")
			cls.dbs = cls._instance.connect()
		return cls._instance

	# Internal functions

	def connect(self):
		_idcfs = OsgiJythonHelper.getService(IspybDataCollectionFactoryService)

		url_property_suffix = "server%s.ispyb.connector.url" % (".development" if self.isDummy() else "")
		self.dbs = _idcfs.buildIspybApi(
			self.beamlinePrefixedLocalProperty(url_property_suffix),
			Optional.of(self.beamlinePrefixedLocalProperty("server.ispyb.connector.user")),
			Optional.of(self.beamlinePrefixedLocalProperty("server.ispyb.connector.password")),
			Optional.of(self.beamlinePrefixedLocalProperty("server.ispyb.connector.database")))
		self.logger.debug("connect() self.dbs = {}", self.dbs)
		self.logger.info("Connected to {} database", LocalProperties.get("gda.mode"))
		# The  ispyb_gda_i15 user has a 5 connection limit, so make sure we close the connection on
		add_reset_hook(self.close_connection) # reset_namespace, so we don't use up a connection each time

	def close_connection(self):
		self.dbs.close()

	# Public functions

	def newDataCollectionGroup(self, experimentType):
		self.logger.debug("newDataCollectionGroup() self.logger={}, self.dbs={}", self.logger, self.dbs)
		visit = GDAMetadataProvider.getInstance().getMetadataValue("visit") or \
				LocalProperties.get('gda.defVisit')

		proposalCode, proposalNumber, sessionNumber = findall(r'(\D+)(\d+)-(\d+)', visit)[0]
		assert len(proposalCode)==2
		proposalNumber = long(proposalNumber)
		sessionNumber = long(sessionNumber)

		dcg = DataCollectionGroup()
		dcg.setProposalCode(proposalCode)
		dcg.setProposalNumber(proposalNumber)
		dcg.setSessionNumber(sessionNumber)
		dcg.setStarttime(self.sqlTime())
		dcg.setComments("visit=%s, since retrieveDataCollectionGroup() doesn't populate proposalCode, proposalNumber & sessionNumber." % visit)
		dcg.setExperimenttype(experimentType)

		try:
			dataCollectionGroupId = self.dbs.upsertDataCollectionGroup(dcg)
		except Exception as e:
			self.logger.error("Error in upsertDataCollectionGroup({})", dcg, e)
			raise e

		self.logger.debug("dataCollectionGroup created with Id {}: {}", dcg.getId(), dcg)
		dcg.setId(dataCollectionGroupId)
		self.logger.debug("dataCollectionGroup updated with Id {}: {}", dataCollectionGroupId, dcg)
		return dcg

	def retrieveDataCollectionGroup(self, dataCollectionGroupId):
		self.logger.debug("retrieveDataCollectionGroup({})", dataCollectionGroupId)
		try:
			dcg = self.dbs.retrieveDataCollectionGroup(dataCollectionGroupId).get()
		except Exception as e:
			self.logger.error("Error in retrieveDataCollectionGroup({})", dataCollectionGroupId, e)
			raise e

		if dcg.getId() != dataCollectionGroupId:
			self.logger.debug("dataCollectionGroup retrieved with Id {} != requested Id {}", dcg.getId(), dataCollectionGroupId)
			dcg.setId(dataCollectionGroupId)
			self.logger.debug("dataCollectionGroup updated with Id {}: {}", dataCollectionGroupId, dcg)
		return dcg

	def upsertDataCollectionGroup(self, dataCollectionGroup):
		self.logger.debug("upsertDataCollectionGroup({})", dataCollectionGroup)
		self.dbs.upsertDataCollectionGroup(dataCollectionGroup)
		return

	def closeDataCollectionGroup(self, dataCollectionGroup):
		self.logger.debug("closeDataCollectionGroup({})", dataCollectionGroup)
		try:
			dataCollectionGroup.setEndtime(self.sqlTime())
			dataCollectionGroupIdConfirmed = self.dbs.upsertDataCollectionGroup(dataCollectionGroup)
			self.logger.debug("upsertDataCollectionGroup returned with Id {} for {}", dataCollectionGroupIdConfirmed, dataCollectionGroup)
			assert dataCollectionGroupIdConfirmed == dataCollectionGroup.getId()
		except Exception as e:
			self.logger.error("Error updating dataCollectionGroup with Id {}", dataCollectionGroup.getId(), e)
			raise e

"""
public interface IspybDataCollectionApi extends Closeable {
	public				Optional<Detector>	retrieveDetector				(String serialNumber)			throws SQLException;
	public							Long	upsertDataCollectionMain		(DataCollectionMain dataCollectionMain);
	public							void	updateDataCollectionExperiment	(DataCollectionExperiment dataCollectionExperiment);
	public							void	updateDataCollectionMachine		(DataCollectionMachine dataCollectionMachine);
	public	Optional<DataCollectionGroup>	retrieveDataCollectionGroup		(Long dcgId)					throws SQLException;
	public							Long	upsertDataCollectionGroup		(DataCollectionGroup dataCollectionGroup);
	public							Long	upsertDataCollectionGroupGrid	(DataCollectionGroupGrid dataCollectionGroupGrid);
	public							void	updateDataCollectionPosition	(Position position);
	public							Long	insertBeamlineAction			(BeamlineAction beamlineAction);
	public							Long	upsertRobotAction				(RobotAction robotAction);
}
"""


@contextmanager
def dataCollectionGroup(dataCollectionGroupId=None,
						experimentTypeDAC=False,
						processingScannable="mimas",
						dataCollectionGroupIdScannable="dataCollectionGroupId"):
	"""

dataCollectionGroup(dataCollectionGroupId=None,
					experimentTypeDAC=False,
					dataCollectionGroupIdScannable="dataCollectionGroupId",
					processingScannable="mimas")

This is a context manager which puts one or more scans in a new or specific
data collection group, to support batch data processing. It returns the mimas
processing scannable, by default, which can then be added to scans if not
already a default scannable.

The default or specified dataCollectionGroupIdScannable is updated with a new
or requested dataCollectionGroupId before the scans are run, and reset to None
after.

If experimentTypeDAC=True when creating a new dataCollectionGroupId, the group
will be created with the "Diamond Anvil High Pressure" experiment type. All
scans in a data collection group must have the same experiment type though, so
if a scan is added to an existing data collection group the experimentTypeDAC
will be ignored and the experiment type will remain unchanged.

For example:

	>>> with dataCollectionGroup():
	...    scan scn start stop step

	>>> with dataCollectionGroup(987654321) as processing:
	...    scan scn start stop step processing

	>>> with dataCollectionGroup(getDataCollectionGroupIdFromScan(12345)):
	...    scan scn start stop step

	>>> with dataCollectionGroup(experimentTypeDAC=True) as processing:
	...    expose(exposeTime, fileNameSuffix, processing)

	>>> with dataCollectionGroup(processingScannable="alt_mimas") as mimas:
	...    expose(exposeTime, fileNameSuffix, mimas)

	>>> with dataCollectionGroup(dataCollectionGroupIdScannable="testDcgId"):
	...    expose(exposeTime, fileNameSuffix)
	"""
	#print "dataCollectionGroup(%r, %r, %r)" % (dataCollectionGroupId, dataCollectionGroupIdScannable, processingScannable)

	IspybDataCollectionApiUtils.exposeDetectorCheck('pil3cbf')

	dbc = IspybDataCollectionApiConnector.instance()

	if not dataCollectionGroupId:
		dcg = dbc.newDataCollectionGroup(ExperimentType.DLS_ANVIL_HP.toString() if experimentTypeDAC else ExperimentType.OSC.toString())
		dataCollectionGroupId = dcg.getId()
		msg = "Created with Id  "
	else:
		msg = "Retrieved with Id"
		dcg = dbc.retrieveDataCollectionGroup(dataCollectionGroupId)

	logger = LoggerFactory.getLogger("dataCollectionGroup:%r" % dataCollectionGroupId)
	logger.debug("{} {}: {}", msg, dataCollectionGroupId, dcg)

	Finder.find(dataCollectionGroupIdScannable).asynchronousMoveTo(int(dataCollectionGroupId))

	yield Finder.find(processingScannable)

	Finder.find(dataCollectionGroupIdScannable).asynchronousMoveTo(None)

	dbc.closeDataCollectionGroup(dcg)

	IspybDataCollectionApiUtils.exposeDetectorCheck('pil3cbf')
	print "The %r metadata scanable used Id %r " % (dataCollectionGroupIdScannable, dataCollectionGroupId)


def getDataCollectionGroupIdFromScan(scan_number, visitPath=None):
	if not visitPath:
		visitPath = InterfaceProvider.getPathConstructor().createFromDefaultProperty()

	try:
		nexusFilePath = os.path.join(visitPath, "{}.nxs".format(scan_number))
		data = dnp.io.load(nexusFilePath, warn=False)
	except Exception as e:
		data = None
		msg = "Could not find `%r.nxs` in folder `%r`" % (scan_number, visitPath)
		LoggerFactory.getLogger('getDataCollectionGroupIdFromScan()').error(msg, e)
	if data:
		try:
			return int(data.entry.instrument.dataCollectionGroupId.value._getdata().data[0])
		except Exception as e:
			LoggerFactory.getLogger('getDataCollectionGroupIdFromScan()').debug(
				"Could not find dataCollectionGroupId in entry/instrument/dataCollectionGroupId/value, "+
				"trying entry1/before_scan/dataCollectionGroupId/value in {}", nexusFilePath, e)
			try:
				return int(data.entry1.before_scan.dataCollectionGroupId.value._getdata().data[0])
			except Exception as e:
				msg = "Could not find dataCollectionGroupId in `%r.nxs`" % scan_number
				LoggerFactory.getLogger('getDataCollectionGroupIdFromScan()').error(msg, e)
	print msg
