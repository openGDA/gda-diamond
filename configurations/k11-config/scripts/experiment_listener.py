from gda.epics import LazyPVFactory  # @UnresolvedImport
from uk.ac.diamond.osgi.services.ServiceProvider import getService  # @UnresolvedImport
from org.eclipse.scanning.api.event import IEventService  # @UnresolvedImport
from java.net import URI  # @UnresolvedImport
from gda.configuration.properties.LocalProperties import getBrokerURI  # @UnresolvedImport
from uk.ac.diamond.daq.experiment.api.EventConstants import EXPERIMENT_CONTROLLER_TOPIC  # @UnresolvedImport
from org.eclipse.scanning.api.event.bean import IBeanListener  # @UnresolvedImport
from uk.ac.diamond.daq.experiment.api.structure.ExperimentEvent import Transition  # @UnresolvedImport
from uk.ac.diamond.daq.scanning import FilePathService  # @UnresolvedImport
from java.io import File  # @UnresolvedImport
from org.apache.commons.io import FileUtils  # @UnresolvedImport

class ExperimentListener(IBeanListener):
    """
    Triggers actions when experiment starts/ends
    """
    def __init__(self, pv):
        self.visit_pv = LazyPVFactory.newStringPV(pv)
        self.subscriber = self.create_subscriber(EXPERIMENT_CONTROLLER_TOPIC)
        self.subscriber.addListener(self)
        
    def create_subscriber(self, topic):
        jms_uri = URI(getBrokerURI())
        return getService(IEventService).createSubscriber(jms_uri, topic)
    
    def beanChangePerformed(self, event):
        write_visit(self.visit_pv)
        if event.getBean().getTransition() == Transition.STARTED:
            copy_template_files()
    
    def close(self):
        self.subscriber.removeListeners()
        self.subscriber.disconnect()


def write_visit(visit_pv):
    """ Writes the visit that an experiment is running in to a PV """
    visit = FilePathService().getVisit()
    visit_pv.putNoWait(visit)

def copy_template_files():
    """ Copies templates into data config directory """
    file_path_service = FilePathService()
    visit_config = file_path_service.getVisitConfigDir()

    # existence of marker file indicates templates already copied
    templates_copied = File(visit_config, ".templates_copied")
    if templates_copied.exists(): return

    templates_dir = File(file_path_service.getPersistenceDir(), "Standard_XML")
    if templates_dir.exists():
        FileUtils.copyDirectory(templates_dir, File(visit_config), False)
        # write marker file
        FileUtils.touch(templates_copied)
