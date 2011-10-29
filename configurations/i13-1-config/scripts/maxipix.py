import os
from gdascripts.messages import handle_messages
from gdascripts.parameters import beamline_parameters
from highestExistingFileMonitorUtils import configureHighestExistingFileMonitor
import gda.util.VisitPath

def mpx_config_file_monitor():
    """
    configures the detector file monitor to look for images from maxipix
    """
    jms=beamline_parameters.JythonNameSpaceMapping()
    configureHighestExistingFileMonitor(jms.mpx_controller.getSavingDirectory(), jms.mpx_controller.getSavingPrefix() + "%04d" + jms.mpx_limaCCD.getSavingSuffix(),
        jms.mpx_limaCCD.getSavingNextNumber())

def mpx_set_folder(folder, prefix):
    """
    sets the folder and prefix to be use for images taken by the maxipix detector
    """
    
    """
    sets saving folder to $(visit_folder) + folder
    sets saving prefix to prefix
    sets saving next number to 1
    """
    jms=beamline_parameters.JythonNameSpaceMapping()
    mpx_controller = jms.mpx_controller
    mpx_limaCCD = jms.mpx_limaCCD
    required_saving_directory = gda.util.VisitPath.getVisitPath() + "/" + folder + "/"
    first_file = required_saving_directory + prefix + "0001" + mpx_limaCCD.getSavingSuffix()
    if os.path.exists(first_file):
        raise Exception("Unable to set folder and prefix as file %s already exists" % first_file)
    if not mpx_controller.getSavingDirectory() == required_saving_directory:
        mpx_controller.setSavingDirectory(required_saving_directory)
    mpx_controller.setSavingPrefix(prefix)
    
    mpx_config_file_monitor()
    handle_messages.log(None, "Successfully set maxipix folder and prefix to [%s,%s]" % (required_saving_directory, prefix))

