from contextlib import contextmanager
from gda.configuration.properties import LocalProperties
from gda.data.metadata import GDAMetadataProvider
from gda.device import DeviceException
from gda.device.scannable import ScannableBase
from gda.factory import Finder
from gda.jython import InterfaceProvider
from gda.jython.commands.GeneralCommands import add_reset_hook
from gda.util.osgi import OsgiJythonHelper
from java.sql import Timestamp
from java.util import Optional
from org.slf4j import LoggerFactory
from re import findall
from time import mktime, localtime
from uk.ac.diamond.ispyb.api import IspybDataCollectionFactoryService, DataCollectionGroup
import os
import scisoftpy as dnp
from magicmodule import debug

class IspybDataCollectionApiUtils(object):

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

	def newDataCollectionGroup(self):
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
						dataCollectionGroupIdScannable="dataCollectionGroupId",
						processingScannable="mimas"):
	"""
This is a context manager which puts one or more scans in a new or specific
data collection group, to support batch data processing. For example:

	>>> with dataCollectionGroup() as processing:
	...    scan scn start stop step processing

	>>> with dataCollectionGroup(987654321) as processing:
	...    scan scn start stop step processing
	"""
	#print "dataCollectionGroup(%r, %r, %r)" % (dataCollectionGroupId, dataCollectionGroupIdScannable, processingScannable)

	dbc = IspybDataCollectionApiConnector.instance()

	if not dataCollectionGroupId:
		dcg = dbc.newDataCollectionGroup()
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

	print "The %r metadata scanable used Id %r " % (dataCollectionGroupIdScannable, dataCollectionGroupId)


def getDataCollectionGroupIdFromScan(scan_number, visitPath=None):
	if not visitPath:
		visitPath = InterfaceProvider.getPathConstructor().createFromDefaultProperty()

	try:
		nexusFilePath = os.path.join(visitPath, "{}.nxs".format(scan_number))
		data = dnp.io.load(nexusFilePath)
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



class DataCollectionGroupScannable (ScannableBase, IspybDataCollectionApiUtils):
	"""
In addition to being a normal scannable, this scannable can also be used as
a context manager to create a new data collection group, or use a specific
data collection group id, for one or more scans. For example:

	>>> with DataCollectionGroupScannable() as dcg:
	...	scan scn start stop step dcg

	>>> with DataCollectionGroupScannable(987654321) as dcg:
	...	scan scn start stop step dcg
	"""
	def __init__(self, dcg_id=None):
		self.setName('dcg')
		self.dcg_id = dcg_id
		self.dcg = None
		self.logger = self.getLogger()

		self.extraNames = self.inputNames
		self.inputNames = []

		self.dbc = IspybDataCollectionApiConnector.instance()

	# Class functions

	def getLogger(self):
		return LoggerFactory.getLogger("DataCollectionGroupScannable:%r" % self.dcg_id)

	def retrieveDataCollectionGroup(self):
		if self.dcg_id:
			self.dcg = self.dbc.retrieveDataCollectionGroup(self.dcg_id)
			self.logger.debug("dataCollectionGroup Id {} reused atScanStart: {}", self.dcg_id, self.dcg)
		else: 
			self.dcg = self.dbc.newDataCollectionGroup()
			self.dcg_id = self.dcg.getId()
			# Update logger as dcg_id has changed
			self.logger = self.getLogger()

	# Context interface method implementation

	def __enter__(self):
		self.logger.debug("__enter__() self.dcg_id = {} self.dbc = {}, self.dcg = {}", self.dcg_id, self.dbc, self.dcg)
		self.retrieveDataCollectionGroup()
		#return self

	def __exit__(self, *_):
		self.logger.debug("__exit__() self.dcg_id = {} self.dbc = {}, self.dcg = {}", self.dcg_id, self.dbc, self.dcg)

	# Optional Scannable interface method implementations

	def atScanStart(self):
		self.logger.debug("atScanStart() self.dcg_id = {} self.dbc = {}, self.dcg = {}", self.dcg_id, self.dbc, self.dcg)
		self.retrieveDataCollectionGroup()

	def atScanEnd(self):
		self.logger.debug("atScanEnd() self.dcg_id = {} self.dbc = {}, self.dcg = {}", self.dcg_id, self.dbc, self.dcg)
		if not self.dcg:
			self.logger.warn("dataCollectionGroup not set for scan!")
			raise DeviceException("self.dcg not set!")
		self.dbc.closeDataCollectionGroup(self.dcg)
		self.dcg = None

	# Required Scannable interface method implementations

	def rawGetPosition(self):
		try:
			return int(self.dcg.getId())
		except:
			return None

	def isBusy(self):
		return False
