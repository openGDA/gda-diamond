import os
import sys    
from gdascripts.messages import handle_messages
from gdascripts.parameters import beamline_parameters
from highestExistingFileMonitorUtils import configureHighestExistingFileMonitor
import gda.util.VisitPath
from gda.device.lima import LimaCCD
from gda.device.maxipix2 import MaxiPix2

def mpx_config_file_monitor():
    """
    configures the detector file monitor to look for images from maxipix
    """
    jms=beamline_parameters.JythonNameSpaceMapping()
    mpx_limaCCD = jms.mpx_limaCCD

    configureHighestExistingFileMonitor(mpx_limaCCD.getSavingDirectory(), mpx_limaCCD.getSavingPrefix() + "%04d" + jms.mpx_limaCCD.getSavingSuffix(),
        mpx_limaCCD.getSavingNextNumber())

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

    try:
        if not os.path.exists(required_saving_directory):
            os.umask(2) # required for acls to be inherited
            os.mkdir(required_saving_directory)
    except :
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "Problem creating folder '" + required_saving_directory +"'",exceptionType, exception, traceback,True)
        
    try:
        if not mpx_controller.getSavingDirectory() == required_saving_directory:
            mpx_controller.setSavingDirectory(required_saving_directory)
    except :
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "Problem setting required folder to '" + required_saving_directory + "'",exceptionType, exception, traceback,True)
        
    try:
        mpx_controller.setSavingPrefix(prefix)
    except :
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "Problem setting prefix to '" + prefix +"'",exceptionType, exception, traceback,True)
        
    mpx_config_file_monitor()
    handle_messages.log(None, "Successfully set maxipix folder and prefix to [%s,%s]" % (required_saving_directory, prefix))

def mpx_reset_configure():
    """
    Command to reset maxipix detector to :
    Flllmode = ZERO
    AcquireMode=Accumulation
    AccMAxExpoTime=0.05
    savingFormat=EDF
    
    and configures file monitor
    """
    jms=beamline_parameters.JythonNameSpaceMapping()
    mpx_limaCCD = jms.mpx_limaCCD
    mpx_maxipix = jms.mpx_maxipix
    mpx_maxipix.setFillMode(MaxiPix2.FillMode.ZERO)
    mpx_limaCCD.setAcqMode( LimaCCD.AcqMode.ACCUMULATION)
    mpx_limaCCD.setAccMaxExpoTime(0.05)
    mpx_limaCCD.setSavingFormat( LimaCCD.SavingFormat.EDF)
    mpx_config_file_monitor()
    