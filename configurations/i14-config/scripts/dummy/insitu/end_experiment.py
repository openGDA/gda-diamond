from uk.ac.gda.core.tool.spring import SpringApplicationContextFacade
from uk.ac.diamond.daq.experiment.api.structure import ExperimentController

experiment = SpringApplicationContextFacade.getBean(ExperimentController)
experiment.stopExperiment()