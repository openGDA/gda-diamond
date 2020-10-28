from gdascripts.utils import caget
from org.slf4j import LoggerFactory
from org.eclipse.dawnsci.analysis.api.tree import TreeUtils
from org.eclipse.dawnsci.nexus import NexusNodeFactory
from org.eclipse.scanning.sequencer import AbstractRunnableDeviceDelegate

import scisoftpy as dnp

class JythonRunnableDeviceDelegate (AbstractRunnableDeviceDelegate):
    logger = LoggerFactory.getLogger("JythonRunnableDeviceDelegate");

    # Delegated AbstractRunnableDevice<T> methods

    def configure(self, model):
        self.logger.info("configure({})", model)
        AbstractRunnableDeviceDelegate.configure(self, model)

    # Delegated interface IRunnableDevice<T> methods

    def run(self, position):
        self.logger.info("run({})", position);
        AbstractRunnableDeviceDelegate.run(self, position)

    # Delegated interface IWritableDetector<T> methods

    def write(self, position):
        self.logger.info("write({})", position);
        return AbstractRunnableDeviceDelegate.write(self, position);

    # Delegated interface INexusDevice<NXobject> methods

    def getNexusProvider(self, info):
        self.logger.info("getNexusProvider({})", info);
        return AbstractRunnableDeviceDelegate.getNexusProvider(self, info)

    # Delegated interface IMultipleNexusDevice methods

    def getNexusProviders(self, info):
        self.logger.info("getNexusProviders({})", info);
        #return AbstractRunnableDeviceDelegate.getNexusProviders(self, info)
        nexusObjectWrapperList = AbstractRunnableDeviceDelegate.getNexusProviders(self, info)  # Do this first

        nxSource = self.getNxSource()
        self.logger.info("getNexusProviders() nxSource={}", nxSource)

        nexusObjectWrapper = self.getNexusObjectWrapper('source', nxSource)
        self.logger.info("getNexusProviders() nexusObjectWrapper={}", nexusObjectWrapper)

        nexusObjectWrapper.setPrimaryDataFieldName(nxSource.NX_ENERGY)
        self.logger.info("getNexusProviders() nexusObjectWrapper={}", nexusObjectWrapper)

        nexusObjectWrapperList.add(nexusObjectWrapper)

        self.logger.info("getNexusProviders() returning {}", nexusObjectWrapperList)
        return nexusObjectWrapperList

    def getNxSource(self):
        nxSource = NexusNodeFactory.createNXsource()
        nxSource.setName(dnp.array(['Diamond Light Source'])._jdataset())
        nxSource.setType(dnp.array(['Synchrotron X-ray Source'])._jdataset())
        nxSource.setProbe(dnp.array(['x-ray'])._jdataset())
        nxSource.setEnergy(dnp.array([0.])._jdataset())
        nxSource.setAttribute(nxSource.NX_ENERGY, 'units', 'GeV')
        nxSource.setCurrent(dnp.array([0.])._jdataset())
        nxSource.setAttribute(nxSource.NX_CURRENT, 'units', 'mA')
        nxSource.setTop_up(dnp.array([0.])._jdataset())
        nxSource.setDistance(dnp.array([-35.6])._jdataset())
        nxSource.setAttribute(nxSource.NX_DISTANCE, 'units', 'm')
        TreeUtils.recursivelyLoadDataNodes(nxSource)
        return nxSource

    # Delegated annotated methods

    def preConfigure(self, scanModel, scanBean, publisher):
        self.logger.info("preConfigure({}, {}, {})", scanModel, scanBean, publisher)
        AbstractRunnableDeviceDelegate.preConfigure(self, scanModel, scanBean, publisher);

    def postConfigure(self, scanModel, scanBean, publisher):
        self.logger.info("postConfigure({}, {}, {})", scanModel, scanBean, publisher)
        AbstractRunnableDeviceDelegate.postConfigure(self, scanModel, scanBean, publisher);

    def levelStart(self, info):
        self.logger.info("levelStart({})", info)
        AbstractRunnableDeviceDelegate.levelStart(self, info);

    def levelEnd(self, info):
        self.logger.info("levelEnd({})", info)
        AbstractRunnableDeviceDelegate.levelEnd(self, info);

    def pointStart(self, point):
        self.logger.info("pointStart({})", point)
        AbstractRunnableDeviceDelegate.pointStart(self, point);

    def pointEnd(self, point):
        self.logger.info("pointEnd({})", point)
        AbstractRunnableDeviceDelegate.pointEnd(self, point);

    def scanStart(self, info):
        self.logger.info("scanStart({})", info)
        AbstractRunnableDeviceDelegate.scanStart(self, info);

    def scanEnd(self, info):
        self.logger.info("scanEnd({})", info)
        AbstractRunnableDeviceDelegate.scanEnd(self, info);

    def scanAbort(self, info):
        self.logger.info("scanAbort({})", info)
        AbstractRunnableDeviceDelegate.scanAbort(self, info);

    def scanFault(self, info):
        self.logger.info("scanFault({})", info)
        AbstractRunnableDeviceDelegate.scanFault(self, info);

    def scanFinally(self, info):
        self.logger.info("scanFinally({})", info)
        AbstractRunnableDeviceDelegate.scanFinally(self, info);

    def scanPause(self):
        self.logger.info("scanPause()")
        AbstractRunnableDeviceDelegate.scanPause(self);

    def scanResume(self):
        self.logger.info("scanResume()")
        AbstractRunnableDeviceDelegate.scanResume(self);
