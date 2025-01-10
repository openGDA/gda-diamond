'''
A Scan wrapper command or function for XAS experiments. It loads NXxas Nexus template before scan starts and remove it after scan completed or aborted/failed.

Created on Dec 2, 2024

@author: fy65
'''
from gda.jython.commands.ScannableCommands import scan
from gda.device import Scannable
import time
from i06shared.scan.miscan import parse_other_arguments, parse_tuple_arguments
from types import TupleType
from gdascripts.metadata.nexus_metadata_class import meta
from gda.jython import InterfaceProvider
from gda.device.scannable import ScannableMotionBase
from i06shared.localStation import XAS_MODES
from i06shared.functions.nexusYamlTemplateProcessor import apply_template_to_nexus_file


PRINTTIME = False

NEXUS_TEMPLATE_YAML_FILE_NAME = "NXxas_template_slowscan.yaml"

def xasscan(*args):
    '''a wrapper scan parser for XAS experiments which set NXxas Application Definition template before data collection and remove it after scan completed
    For example (i06 GDA):
        xasscan energy start stop step ca51sr 1 ca52sr 1 ca53sr 1 ca54sr 1 xasmode TEY
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
        elif isinstance(arg, ScannableMotionBase) and arg.getName() == 'xasmode':
            if args[i+1] not in XAS_MODES:
                raise ValueError("%s is not a supported measurement mode. Supported mode must be one of %r." % (arg[i+1], XAS_MODES))
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

