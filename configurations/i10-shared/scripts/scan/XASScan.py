'''
A Scan wrapper command or function for XAS experiments. It loads NXxas Nexus template before scan starts and remove it after scan completed or aborted/failed.

Created on Dec 2, 2024

@author: fy65
'''
from gda.jython.commands.ScannableCommands import scan
from gda.device import Scannable
import time
from scan.miscan import parse_other_arguments, parse_tuple_arguments
from types import TupleType
from gdascripts.metadata.nexus_metadata_class import meta
from gda.jython import InterfaceProvider
from gda.device.scannable import ScannableMotionBase
from functions.nexusYamlTemplateProcessor import apply_template_to_nexus_file

from uk.ac.diamond.osgi.services import ServiceProvider # @UnresolvedImport
from uk.ac.diamond.daq.configuration import BeamlineConfiguration
from gda.configuration.properties import LocalProperties
spring_profiles = ServiceProvider.getService(BeamlineConfiguration).profiles.toList()
beamline_name = LocalProperties.get(LocalProperties.GDA_BEAMLINE_NAME, "i10")

PRINTTIME = False

if beamline_name == "i10":
    NEXUS_TEMPLATE_YAML_FILE_NAME = "NXxas_template_slowscan.yaml"
elif beamline_name == "i10-1":
    if "hfm" in spring_profiles:
        NEXUS_TEMPLATE_YAML_FILE_NAME = "NXxas_template_hfm_slowscan.yaml"
    if "em" in spring_profiles:
        NEXUS_TEMPLATE_YAML_FILE_NAME = "NXxas_template_em_slowscan.yaml"

def xasscan(*args):
    '''a wrapper scan parser for XAS experiments which apply NXxas Application Definition template after data collection completed.
    For example (i06 GDA):
        xasscan energy start stop step ca51sr 1 ca52sr 1 ca53sr 1 ca54sr 1 xasmode_slow TEY
    '''
    if len(args) == False:
        raise SyntaxError("No argument is given to scan command!")
    if not isinstance(args[0], Scannable):
        raise SyntaxError("First argument to scan command must be a scannable")
    command = "xasscan "
    original_mode = None
    starttime = time.ctime()
    start = time.time()
    if PRINTTIME: print("=== Scan started: " + starttime)
    newargs = []
    i = 0;
    while i < len(args):
        arg = args[i]
        if type(arg) == TupleType:
            command, newargs = parse_tuple_arguments(command, newargs, arg)
        elif isinstance(arg, ScannableMotionBase) and arg.getName() == 'xasmode_slow':
            if arg.getPosition() != args[i+1]: #XAS mode changed
                original_mode = arg.getPosition()
                xas_mode_scannable = arg
            arg.asynchronousMoveTo(args[i+1])
            command += arg.getName() + " " + args[i+1]
            i = i + 1
        else:
            newargs.append(arg)
            command = parse_other_arguments(command, arg)
        i = i + 1

    meta.addScalar("user_input", "command", command)
    try:
        scan([e for e in newargs])
        print("creating NXxas subentry ...")
        current_filename = InterfaceProvider.getScanDataPointProvider().getLastScanDataPoint().getCurrentFilename()
        apply_template_to_nexus_file(current_filename, NEXUS_TEMPLATE_YAML_FILE_NAME, spel_expression_node = ["absorbed_beam/"])
        print("NXxas subentry is added to %s" % current_filename)
    finally:
        if original_mode: # restore pre-scan XAS mode
            xas_mode_scannable.asynchronousMoveTo(original_mode)
        meta.rm("user_input", "command")    

    if PRINTTIME: print ("=== Scan ended: " + time.ctime() + ". Elapsed time: %.0f seconds" % (time.time() - start))


from gda.jython.commands.GeneralCommands import alias 
alias("xasscan")

