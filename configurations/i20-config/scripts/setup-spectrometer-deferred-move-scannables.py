from __builtin__ import True
print("\nRunning 'setup-spectrometer-deferred-move-scannables.py'")

from gda.jython import InterfaceProvider

from gda.device.scannable import PVScannable
from gda.device.scannable.scannablegroup import ScannableGroup
import math

def create_scannable(scn_name, pv_name):
    if LocalProperties.isDummyModeEnabled() :
        scn = DummyScannable(scn_name)
    else : 
        scn = PVScannable(scn_name, pv_name)
        
    placeInJythonNameSpace(scn)
    return scn

# Get the PV name from a scannable motor
from gda.device.motor import EpicsMotor
def getPvName(scnMotor):
    mot = scnMotor.getMotor()
    if isinstance(mot, EpicsMotor) :
        return mot.getPvName()
    else :
        return mot.getName()

def placeInJythonNameSpace(scannable) :
    jythonNamespace = InterfaceProvider.getJythonNamespace()
    jythonNamespace.placeInJythonNamespace(scannable.getName(), scannable)

# Generate ScannableGroup of new PVScannables pointing to :DirectDemand PVs from group of ScannableMotors
def generate_direct_move_group(scannableGroup, debug=False):
    allScannables = []
    for scnMotor in scannableGroup.getGroupMembers() :
        pvName = getPvName(scnMotor).strip()
        directDemandPv = pvName+":DirectDemand"
        scnName = scnMotor.getName()+"_directDemand"
        allScannables.append(create_scannable(scnName, directDemandPv))
        if debug :
            print(scnName+" : "+directDemandPv)
        
    scnGroup = ScannableGroup(scannableGroup.getName()+"_directDemand", allScannables)
    scnGroup.configure()
    placeInJythonNameSpace(scnGroup)

    return scnGroup

# Generate ScannableGroup of new PVScannables pointing to :DeferMove PVs from list of base PV names
def generate_defer_move_group(pv_name_list, scn_name_prefix) :
    defer_scannables = []
    for pv_name in pv_name_list :
        scn_name = scn_name_prefix+"_"+pv_name+"_defer_move"
        defer_scannables.append(create_scannable(scn_name, pv_name+":DeferMoves"))
        
    defer_group = ScannableGroup(scn_name_prefix+"defer_move", defer_scannables)
    defer_group.configure()
    placeInJythonNameSpace(defer_group)
    return defer_group

def set_deferred_move_scannables(pv_name_list, xes_bragg_scannable, scn_name_prefix) :
    print("  Setting up deferred move scannables for "+xes_bragg_scannable.getName())
    defer_move_group = generate_defer_move_group(pv_name_list, scn_name_prefix)

    xes_bragg_scannable.setDeferredMoveStartStopGroup(defer_move_group)

    # print("Deferred move scannable names for "+scannable.getName()+" : ")
    for n in defer_move_group.getGroupMemberNames() :
        print("\t"+n)

print("Generating map of scannable groups for XES spectrometer 'direct demand' PVs : ")
directDemandScannableMap = {}
for crystalsGroup in [upper_spectrometerCrystals, lower_spectrometerCrystals] :
    for scnGroup in crystalsGroup.getGroupMembers() :
        directDemandGroup = generate_direct_move_group(scnGroup, debug=False) 
        print("\t"+directDemandGroup.getName()+" -> "+scnGroup.getName())
        directDemandScannableMap[scnGroup] = directDemandGroup

# Set up XES spectrometer objects to use the map
XESBraggLower.setDirectDemandScannablesMap(directDemandScannableMap)
XESBraggUpper.setDirectDemandScannablesMap(directDemandScannableMap)

# (need to control the 'defer move' PV on each of these)

# PowerPMac base PVs for x, y, yaw, pitch stages for upper and lower rows (for testing)
defer_test_upper = []
pmac_pv_base = "BL20I-MO-PMAC-"
#x, y, yaw, pitch
for num in [51, 52, 63, 64, 55, 56, 59, 60] :
    defer_test_upper.append(pmac_pv_base+str(num))

defer_test_lower = []
for num in [53, 54, 65, 66, 57, 58, 61, 62] :
    defer_test_lower.append(pmac_pv_base+str(num))

# Geobrick base PVs for x, y, yaw, pitch stages for upper and lower rows 
defer_geobrick_upper = ["BL20I-MO-STEP-17", "BL20I-MO-STEP-22", "BL20I-MO-STEP-18", "BL20I-MO-STEP-21"]
defer_geobrick_lower = ["BL20I-MO-STEP-19", "BL20I-MO-STEP-24", "BL20I-MO-STEP-20", "BL20I-MO-STEP-23"]
# PV to use to see if IOC is running
defer_geobrick_ioc_status = "BL20I-MO-IOC-17:STATUS"

# PowerPMac base PVs for x, y, yaw, pitch stages for upper and lower rows 
defer_ppmac_upper = ["BL20I-MO-PMAC-40", "BL20I-MO-PMAC-38", "BL20I-MO-PMAC-34", "BL20I-MO-PMAC-36"]
defer_ppmac_lower = ["BL20I-MO-PMAC-33", "BL20I-MO-PMAC-39", "BL20I-MO-PMAC-35", "BL20I-MO-PMAC-37"]
# PV to use to see if IOC is running
defer_ppmac_ioc_status = "BL20I-MO-IOC-40:STATUS"

def check_status_pv(status_pv) :
    """
    Return True if given :STATUS PV returns "Running" (i.e. IOC is running), otherwise return False.
    Return False if an exception is thrown (due to timeout etc)
    """
    try :
        return CAClient.get(status_pv) == "Running"
    except Exception as ex :
        print("Problem trying to read status PV ("+status_pv+")")
        return False

def setup_for_deferred_moves() :
    print("Generating scannable groups for XES spectrometer 'deferred move' : ")

    XESBraggLower.setUseDeferredMove(True)
    XESBraggUpper.setUseDeferredMove(True)
    
    #Decide which set of deferred move PVs to used based on whether PPMac or Geobrick IOCs are running
    if check_status_pv(defer_ppmac_ioc_status) :
        print("Using Power PMac 'deferred move' PVs")
        set_deferred_move_scannables(defer_ppmac_upper, XESBraggUpper, "upper")
        set_deferred_move_scannables(defer_ppmac_lower, XESBraggLower, "lower")
    elif check_status_pv(defer_geobrick_ioc_status) :
        print("Using GeoBrick 'deferred move' PVs")
        set_deferred_move_scannables(defer_geobrick_upper, XESBraggUpper, "upper")
        set_deferred_move_scannables(defer_geobrick_lower, XESBraggLower, "lower")
    else :
        print("** Warning : PPMac and GeoBrick deferred move IOCs do not seem to be running!\n" \
              " - disabling deferred moves for XES upper and lower! **")
        XESBraggLower.setUseDeferredMove(False)
        XESBraggUpper.setUseDeferredMove(False)
    print("Finished")

setup_for_deferred_moves()
print("\nUse 'setup_for_deferred_moves()' function to update the 'deferred move' PVs to match the currently running Geobrick/PPmac IOCs in Epics.")