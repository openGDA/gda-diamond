'''
A simplified version of cvscan - which does not support old 'egy_g' and 'egy' scannable any more.

Created on 28 July 2020
added ID access control observer on 06/08/2021

@author: fy65
'''
from numbers import Number
import sys

from gda.jython.commands.GeneralCommands import alias
from gdascripts.scan import trajscans
from gdascripts.scan.installStandardScansWithProcessing import scan_processor
from gdascripts.scan.scanListener import ScanListener
from org.slf4j import LoggerFactory
from scannables.checkbeanscannables import ZiePassthroughScannableDecorator
from scannables.waveform_channel.WaveformChannelScannable import WaveformChannelScannable
from utils.ExceptionLogs import localStation_exception
from gda.factory import Finder
from gda.observable import IObserver
from calibrations.mode_polarisation_energy_instances import smode
from calibrations.xraysource import X_RAY_SOURCE_MODES
from time import sleep
from gda.device import Scannable
from types import IntType, FloatType
from gdascripts.metadata.nexus_metadata_class import meta

from gda.jython import InterfaceProvider
from functions.nexusYamlTemplateProcessor import apply_template_to_nexus_file
from uk.ac.diamond.osgi.services import ServiceProvider # @UnresolvedImport
from uk.ac.diamond.daq.configuration import BeamlineConfiguration
from gda.configuration.properties import LocalProperties
spring_profiles = ServiceProvider.getService(BeamlineConfiguration).profiles.toList()
beamline_name = LocalProperties.get(LocalProperties.GDA_BEAMLINE_NAME, "i10")

if beamline_name == "i10":
    NEXUS_TEMPLATE_YAML_FILE_NAME = "NXxas_template_fastscan.yaml"
elif beamline_name == "i10-1":
    if "hfm" in spring_profiles:
        NEXUS_TEMPLATE_YAML_FILE_NAME = "NXxas_template_hfm_fastscan.yaml"
    if "em" in spring_profiles:
        NEXUS_TEMPLATE_YAML_FILE_NAME = "NXxas_template_em_fastscan.yaml"
        
class TrajectoryControllerHelper(ScanListener):

    def __init__(self):  # motors, maybe also detector to set the delay time
        self.logger = LoggerFactory.getLogger("TrajectoryControllerHelper")
        self.original_default_scannables = []

    def prepareForScan(self):
        self.logger.info("prepareForCVScan()")
        # remove default scannables as they cannot work with cvscan
        self.original_default_scannables = []
        from gda.jython.commands.ScannableCommands import get_defaults, remove_default
        default_scannables = get_defaults()
        self.logger.debug("remove original default scannables: %r from default" % default_scannables)
        for scn in default_scannables:
            self.original_default_scannables.append(scn)
            remove_default(scn)

    def update(self, scan_object):
        self.logger.info("update(%r)" % scan_object)
        # restore default scannables after cvscan completed.
        if self.original_default_scannables is not None:
            from gda.jython.commands.ScannableCommands import add_default
            self.logger.debug("add original default scannables %r to default" % self.original_default_scannables)
            for scn in self.original_default_scannables:
                add_default(scn)
            self.original_default_scannables = []
        else:
            self.logger.debug("original default scannables is empty!")


trajectory_controller_helper = TrajectoryControllerHelper()
cvscan_traj = trajscans.CvScan([scan_processor, trajectory_controller_helper])

idd_access_control = Finder.find("idblena_id1")
idu_access_control = Finder.find("idblena_id2")

from gda.epics.IAccessControl import Status


class IDAccessObserver(IObserver):

    def __init__(self, id_access_control):
        self.id_control = id_access_control
        self.status = Status.ENABLED  # @UndefinedVariable
        id_access_control.addIObserver(self)

    def update(self, source, arg):
        if source == self.id_control:
            self.status = arg

    def getStatus(self):
        return self.status


idd_access_observer = IDAccessObserver(idd_access_control)
idu_access_observer = IDAccessObserver(idu_access_control)

print("-"*100)
print("Creating I10 GDA 'cvscan' commands: - dwell time must apply to all waveform scannables individually!")


def cvscan(c_energy, start, stop, step, *args):
    ''' parse arguments and set scan time required to collect data before topup when 'checkbeamcv' is used.
    '''
    command = "cvscan "
    wfs = []
    dwell = []
    others = []
    beam_checker = None
    newargs = [c_energy, start, stop, step]
    command += c_energy.getName() + " " + " ".join(map(str, newargs[1:])) + " "
    for arg in args:
        if isinstance(arg, WaveformChannelScannable):
            wfs.append(arg)
        elif isinstance(arg, Number):
            dwell.append(arg)
        elif isinstance(arg, ZiePassthroughScannableDecorator):
            beam_checker = arg
        else:
            others.append(arg)
    if not checkContentEqual(dwell):
        raise ValueError("dwell time specified must be equal for all detectors!")
    for each in wfs:
        newargs.append(each)
        command += each.getName() + " "
        newargs.append(dwell[0])  # the pull stream code require every channel have dwell time even they are on the same EPICS scaler
        command += str(dwell[0]) + " "
    for other in others:
        newargs.append(other)
        if isinstance(other, Scannable):
            command += other.getName() + " "
        if type(other) == IntType or type(other) == FloatType:
            command += str(other) + " "
    if beam_checker is not None:
        # set time required for cvscan before topup
        scan_time = abs((stop - start) / step * dwell[0])
        topup_checker = beam_checker.getDelegate().getGroupMember("checktopup_time_cv")
        topup_checker.minimumThreshold = scan_time + 5
        newargs.append(beam_checker)
        command += beam_checker.getName()
    # wait for ID access control is enabled before continue - see I10-513
    if smode.getPosition() == X_RAY_SOURCE_MODES[0]:
        first_time = True
        while idd_access_observer.getStatus() == Status.DISABLED:  # @UndefinedVariable
            if first_time:
                print("Waiting for idd access from beamline to be enabled by Main Control Room, Tel: 8899")
                first_time = False
            sleep(5)
    elif smode.getPosition() == X_RAY_SOURCE_MODES[1]:
        first_time = True
        while idu_access_observer.getStatus() == Status.DISABLED:  # @UndefinedVariable
            if first_time:
                print("Waiting for idu access from beamline to be enabled by Main Control Room, Tel: 8899")
                first_time = False
            sleep(5)

    meta.addScalar("user_input", "command", command)
    try:
        cvscan_traj([arg for arg in newargs])
        print("Creating NXxas sub-entry ...")
        current_filename = InterfaceProvider.getScanDataPointProvider().getLastScanDataPoint().getCurrentFilename()
        apply_template_to_nexus_file(current_filename, NEXUS_TEMPLATE_YAML_FILE_NAME, spel_expression_node = ["absorbed_beam/"])
        print("NXxas subentry is added to %s" % current_filename)
    except Exception as e:
        localStation_exception(sys.exc_info(), "cvscan exits with Error: %s" % (e))
    finally:
        meta.rm("user_input", "command")
 

alias('cvscan')


def checkContentEqual(lst):
    return lst[1:] == lst[:-1]

# cvscan testing
# cvscan energy 750 850 1 mcs16 0.1
