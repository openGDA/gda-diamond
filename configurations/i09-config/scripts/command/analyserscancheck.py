'''
Created on 15 May 2013

@author: fy65
'''
from gda.factory import Finder
from org.opengda.detector.electronanalyser.nxdetector import EW4000, IConfigureSequenceDetector
from gdascripts.utils import caput
from gda.device import Scannable
from gdaserver import dcmenergyEv, pgmenergy, analyser #@UnresolvedImport
from i09shared.command.analyserScan import getSequenceFilename

def zerosupplies():
    caput("BL09I-EA-DET-01:CAM:ZERO_SUPPLIES", 1)

def is_region_valid(region_validator, region, elementset, excitationenergy):
    if region.isEnabled():
        if not region_validator.isValidRegion(region, elementset, excitationenergy):
            return False
    return True

def analyserscancheck(*args):
    region_validator=Finder.find("regionvalidator")

    ew4000 = None

    energy_scan = False

    pgm_excitation_energy_start = []
    pgm_excitation_energy_stop  = []

    dcm_excitation_energy_start = []
    dcm_excitation_energy_stop  = []

    args = list(args)

    scannable_name = ""

    i = 0
    while i < len(args):
        arg = args[i]

        if isinstance( arg,  EW4000 ):
            ew4000 = arg     
            filename = getSequenceFilename(args[i + 1])
            i = i + 1
            continue

        elif not isinstance(arg, Scannable):
            i = i + 1
            continue

        #If energy scan values are used, we need to validate our regions against these
        elif arg.getName() =="ienergy" or arg.getName()=="dcmenergy" or arg.getName()=="dcmenergyEv" or arg.getName()=="jenergy" or arg.getName()=="pgmenergy" :
            try:
                scannable_name = arg.getName()

                if isinstance(args[i + 1], tuple):
                    params = args[i + 1]
                    i = i + 1
                else:
                    params = tuple(args[i + 1], args[i + 2], args[i + 3])
                    i = i + 3

                if arg.getName() =="ienergy" or arg.getName()=="dcmenergy" or arg.getName()=="dcmenergyEv":
                    min_param = min(params)
                    max_param = max(params)
                    #Convert from keV to eV
                    if arg.getName() =="ienergy" or arg.getName()=="dcmenergy":
                        min_param = min_param * 1000
                        max_param = max_param * 1000
                    dcm_excitation_energy_start.append(min_param)
                    dcm_excitation_energy_stop.append(max_param)

                elif arg.getName() =="jenergy" or arg.getName()=="pgmenergy":
                    pgm_excitation_energy_start.append(min(params))
                    pgm_excitation_energy_stop.append(max(params))

            except IndexError:
                raise SyntaxError(
                    "Incorrect syntax for " + arg.getName()
                )
            energy_scan = True

        i = i + 1

    ew4000.setSequenceFile(filename)
    regions = ew4000.getCollectionStrategy().getEnabledRegions()

    element_set = analyser.getPsuMode()
    xray_limit = ew4000.getRegionDefinitionResourceUtil().getXRaySourceEnergyLimit()

    invalid_regions = []

    def print_invalid_message(region, exctiation_energy):
        if not valid_region:
            invalid_regions.append(region.getName())
            print("Region " + region.getName() + " is not valid at " + scannable_name + " " + str(exctiation_energy) + " eV.")

    for region in regions:
        valid_region = False

        if energy_scan:
            for i in range(0, len(dcm_excitation_energy_start)):

                #If this is a pgm, we only want to check it's valid against pgm and not the dcm scannable args
                if region.getExcitationEnergy() < xray_limit:
                    valid_region = is_region_valid(region_validator, region, element_set, region.getExcitationEnergy())
                    print_invalid_message(region, region.getExcitationEnergy())
                    break
                #Check all dcm scannable args are valid for region
                else:
                    valid_region = is_region_valid(region_validator, region, element_set, dcm_excitation_energy_start[i])
                    print_invalid_message(region, dcm_excitation_energy_start[i])

                    valid_region = is_region_valid(region_validator, region, element_set, dcm_excitation_energy_stop[i])
                    print_invalid_message(region, dcm_excitation_energy_stop[i])

            for i in range(0, len(pgm_excitation_energy_start)):

                if region.getExcitationEnergy() > xray_limit:
                    valid_region = is_region_valid(region_validator, region, element_set, region.getExcitationEnergy())
                    print_invalid_message(region, region.getExcitationEnergy())
                    break

                else:
                    valid_region = is_region_valid(region_validator, region, element_set, pgm_excitation_energy_start[i])
                    print_invalid_message(region, pgm_excitation_energy_start[i])

                    valid_region = is_region_valid(region_validator, region, element_set, pgm_excitation_energy_stop[i])
                    print_invalid_message(region, pgm_excitation_energy_stop[i])
        else:
            excitation_energy = float(pgmenergy.getPosition())
            if region.getExcitationEnergy() > xray_limit:
                excitation_energy = float(dcmenergyEv.getPosition())

            valid_region = is_region_valid(region_validator, region, element_set, excitation_energy)
            print_invalid_message(region, excitation_energy)

    if len(invalid_regions) == 0:
        print("All regions are valid!")