from gda.epics import LazyPVFactory
from uk.ac.diamond.osgi.services.ServiceProvider import getService
from org.eclipse.scanning.api.event import IEventService
from java.net import URI
from gda.configuration.properties.LocalProperties import getBrokerURI
from uk.ac.diamond.daq.experiment.api.EventConstants import EXPERIMENT_CONTROLLER_TOPIC
from uk.ac.gda.api.io import PathConstructor
from org.eclipse.scanning.api.event.bean import IBeanListener

class ExperimentListener(IBeanListener):
    """
    Writes the visit that an experiment is running in to a PV 
    """
    def __init__(self, pv):
        self.visit_pv = LazyPVFactory.newStringPV(pv)
        self.subscriber = self.create_subscriber(EXPERIMENT_CONTROLLER_TOPIC)
        self.subscriber.addListener(self)
        
    def create_subscriber(self, topic):
        jms_uri = URI(getBrokerURI())
        return getService(IEventService).createSubscriber(jms_uri, topic)
    
    def beanChangePerformed(self, event):
        visit = PathConstructor().getVisitDirectory()
        self.write_visit(visit.split("/")[-1])
    
    def write_visit(self, visit):
        self.visit_pv.putNoWait(visit)
    
    def close(self):
        self.subscriber.removeListeners()
        self.subscriber.disconnect()
