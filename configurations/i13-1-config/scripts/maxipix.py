import os
import sys    
from gdascripts.messages import handle_messages
from gdascripts.parameters import beamline_parameters
from highestExistingFileMonitorUtils import configureHighestExistingFileMonitor
import gda.util.VisitPath
from gda.device.lima import LimaCCD
from gda.device.maxipix2 import MaxiPix2
from java.lang import String

def mpx_config_file_monitor():
    """
    configures the detector file monitor to look for images from maxipix
    """
    jms=beamline_parameters.JythonNameSpaceMapping()
    mpx_limaCCD = jms.mpx_limaCCD

    configureHighestExistingFileMonitor(mpx_limaCCD.getSavingDirectory(), mpx_limaCCD.getSavingPrefix() + "%04d" + jms.mpx_limaCCD.getSavingSuffix(),
        mpx_limaCCD.getSavingNextNumber())

def mpx_set_folder(folder, prefix, nextFrameNumber=0):
    """
    sets the folder and prefix to be use for images taken by the maxipix detector
    """
    
    """
    sets saving folder to $(visit_folder) + folder
    sets saving prefix to prefix
    sets saving next number to nextFrameNumber def = 0
    """
    if nextFrameNumber > 9999:
        raise ValueError("nextFrameNumber is too big. Must be less than 9999")
    jms=beamline_parameters.JythonNameSpaceMapping()
    mpx_controller = jms.mpx_controller
    mpx_limaCCD = jms.mpx_limaCCD
    
    required_saving_directory = gda.util.VisitPath.getVisitPath() + "/" + folder + "/"
    
    first_file = required_saving_directory + prefix + String.format("%04d",[nextFrameNumber]) + mpx_limaCCD.getSavingSuffix()
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
        ##in overwrite mode we can cahnge the prefix and number to anything we want
        mpx_limaCCD.setSavingOverwritePolicy( LimaCCD.SavingOverwritePolicy.OVERWRITE)
    
        try:
            if not mpx_controller.getSavingDirectory() == required_saving_directory:
                mpx_controller.setSavingDirectory(required_saving_directory)
        except :
            exceptionType, exception, traceback = sys.exc_info()
            handle_messages.log(None, "Problem setting required folder to '" + required_saving_directory + "'",exceptionType, exception, traceback,True)
            
        try:
            mpx_controller.setSavingPrefix(prefix)
            mpx_limaCCD.setSavingNextNumber(nextFrameNumber)
            mpx_limaCCD.setSavingMode( LimaCCD.SavingMode.AUTO_FRAME)
            if( mpx_limaCCD.getSavingNextNumber() != nextFrameNumber):
                raise IOError("Error setting nextFrameNumber")
            if( mpx_limaCCD.getSavingPrefix() != prefix):
                raise IOError("Error setting prefix")
            if( mpx_limaCCD.getSavingDirectory() != required_saving_directory):
                raise IOError("Error setting directory")
        except :
            exceptionType, exception, traceback = sys.exc_info()
            handle_messages.log(None, "Problem setting prefix to '" + prefix +"'",exceptionType, exception, traceback,True)

    finally:
        ##in overwrite mode we can cahnge the prefix and number to anything we want
        mpx_limaCCD.setSavingOverwritePolicy( LimaCCD.SavingOverwritePolicy.ABORT)
        
    mpx_config_file_monitor()
    handle_messages.log(None, "Successfully set maxipix folder, prefix and nextFrameNumber to  [%s,%s,%d]" % (required_saving_directory, prefix, nextFrameNumber))

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
    
