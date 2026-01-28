'''
A wrapper scan for XMCD-PEEM - https://jira.diamond.ac.uk/browse/I06-1391

Created on 22 Jan 2026

@author: fy65
'''

from gdascripts.scannable.virtual_scannable import VirtualScannable
from i06shared.scannables.polarisation import Polarisation
from __main__ import pol, energy  # @UnresolvedImport
from gdaserver import medipix, mpx  # @UnresolvedImport
import time
from types import FloatType, IntType, BooleanType
from gda.device.scannable import DummyScannable
from gda.jython.commands.ScannableCommands import scan
from gdascripts.metadata.nexus_metadata_class import meta
from gda.device.scannable.scannablegroup import ScannableGroup


PRINTTIME = False
dummyScannable = DummyScannable("dummyScannable")

SRW, CRW = ["SRW", "CRW"]

resonant = VirtualScannable("resonant", initial_value = False, value_format = '%s', valid_values = [True, False])

def xmcd(*args):
    ''' a wrapper scan command for XMCD experiment using polarisation, energy, resonant scannables, and CRW or SRW flag to specify detector driver mode.
    This function parses input arguments according their data types and positions, and group and assign them to pol, energy, resonant scannables and
    detector accordingly. A detector driver mode flag (SRW or CRW) must be provided before detector parameters for number of images and exposure time.
    This flag is used to select the detector is used in the scan.

    In SRW mode, a dummyScannable is used to do image counting while medpix detector is used to control exposure;
    In CRW mode, mpx detector is used for data collection.

    command syntax requested in https://jira.diamond.ac.uk/browse/I06-1391 and its mapping to scan:

        xmcd pc nc nc pc Eres Eoff True False SRW numImages IntTime
          ->  scan pol (pc nc nc pc) energy_resonant ([E1,True], [E2, False]) ds 1 numImages 1 medipix IntTime

        xmcd pc nc nc pc Eres Eoff True False CRW numImages IntTime
          ->  scan pol (pc nc nc pc) energy_resonant ([E1,True], [E2, False]) mpx numImages IntTime

        xmcd pc E1 E2 True True SRW numImages IntTime
          ->  pol.moveTo(pc); scan pol energy_resonant ([E1,True], [E2,True]) ds 1 numImages 1 medipix IntTime

        xmcd pc E1 E2 True True CRW numImages IntTime
          ->  pol.moveTo(pc); scan energy_resonant ([E1,True], [E2,True]) mpx numImages IntTime

        xmcd pc nc E1 True SRW numImages IntTime
          ->   scan pol (pc, nc) energy_resonant ([E1,True],) ds 1 numImages 1 medipix IntTime

        xmcd pc nc E1 True CRW numImages IntTime
          ->  scan pol (pc, nc) energy_resonant ([E1,True],) mpx numImages IntTime
    '''

    if len(args) < 7:
        raise ValueError("Missing arguments - xmcd requires minimum of 7 arguments to work!")
    command = "xmcd "  # rebuild the input command as String so it can be recored into data file

    polarisation_values = []
    energy_values = []
    resonant_values = []
    use_medipix = False
    use_mpx = False
    number_images = 0
    integration_time = 0.0
    others = []

    starttime = time.ctime()
    start = time.time()
    if PRINTTIME: print("=== Scan started: " + starttime)
    newargs = []
    i = 0;
    while i < len(args):
        arg = args[i]
        if arg in Polarisation.POLARISATIONS[:-1]:
            polarisation_values.append(arg)
            command += str(arg) + " "
        elif type(arg) == FloatType or type(arg) == IntType:
            if use_medipix or use_mpx:
                number_images = arg
                integration_time= args[i + 1]
                command += str(arg) + " " + str(args[i+1]) + " "
                i = i + 1
            else:
                energy_values.append(arg)
                command += str(arg) + " "
        elif type(arg) == BooleanType:
            resonant_values.append(arg)
            command += str(arg) + " "
        elif arg in [SRW, CRW]:
            command += str(arg) + " "
            if arg == SRW:
                use_medipix = True
            elif arg == CRW:
                use_mpx = True
            else:
                raise ValueError("xmcd command must specify detector mode either SRW or CRW but not both")
        else:
            others.append(arg)
            command += str(arg) + " "
        i = i + 1

    #rebuild scan command arguments
    if len(polarisation_values) == 1:
        print("move polarisation to %s" % polarisation_values[0])
        pol.moveTo(polarisation_values[0])
    else:
        newargs.append(pol)
        newargs.append(tuple(polarisation_values))
    scannable_group = ScannableGroup()
    scannable_group.setName("energy_resonant")
    scannable_group.addGroupMember(energy)
    scannable_group.addGroupMember(resonant)
    newargs.append(scannable_group)
    newargs.append(tuple(list(e) for e in zip(energy_values, resonant_values)))
    if use_medipix:
        newargs.append(dummyScannable)
        newargs.append(1)
        newargs.append(number_images)
        newargs.append(1)
        newargs.append(medipix)
        newargs.append(integration_time)
    if use_mpx:
        newargs.append(mpx)
        newargs.append(integration_time)
        newargs.append(number_images)
    if not others:
        newargs.extend(others)
    #debug
    # print(newargs)
    # print(command)

    meta.addScalar("user_input", "command", command)
    try:
        scan([e for e in newargs])
    finally:
        meta.rm("user_input", "command")

    if PRINTTIME: print("=== Scan ended: " + time.ctime() + ". Elapsed time: %.0f seconds" % (time.time() - start))


from gda.jython.commands.GeneralCommands import alias
alias("xmcd")
