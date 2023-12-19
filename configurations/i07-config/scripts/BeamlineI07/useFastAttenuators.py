from gdaserver import fatt, exr, exv, excalibur, excalibur_atten, dcm1energy, transmissions_lookup_table
from gda.configuration.properties import LocalProperties
import time, datetime
from gdascripts.installation import isLive

add_default(fatt)

def att(attenuation=None):
    if attenuation != None:
        pos(fatt, attenuation)
    else :
        pos(fatt)

def autofon():
    exr.setDetector(excalibur_atten)
    exv.setDetector(excalibur_atten)
    LocalProperties.set("gda.beamline.auto.attenuation", True)
    exc_scan = getRunnableDeviceService().getRunnableDevice("BL07I-ML-SCAN-01")
    setProcessingEnabled(exc_scan.getProcessing().getProcessorMap(), True)
    print("Automatic attenuation enabled for exr, exv, exc and exs")

def autofoff():
    exr.setDetector(excalibur)
    exv.setDetector(excalibur)
    LocalProperties.set("gda.beamline.auto.attenuation", False)
    exc_scan = getRunnableDeviceService().getRunnableDevice("BL07I-ML-SCAN-01")
    setProcessingEnabled(exc_scan.getProcessing().getProcessorMap(), False)
    fatt.manualMode()
    print("Automatic attenuation disabled for exr, exv, exc and exs")

def setProcessingEnabled(procs, enabled):
    atten = [conf for conf in procs if conf.detFileNameSuffix() == "-attenuation.h5"]
    for a in atten:
        for proc in procs[a]:
            proc.setEnabled(enabled)

def exc_fast_exp_time(time=None):
    if time==None:
        print("exc_fast_exp_time : " + excalibur_atten.getCollectionStrategy().getFastExpTime())
    elif time<=0:
        raise ValueError("exc_fast_exp_time must be positive.")
    else:
        excalibur_atten.getCollectionStrategy().setFastExpTime(time)

alias(att)
alias(autofon)
alias(autofoff)
alias(exc_fast_exp_time)

epics_filter_names = ["Cu", "Mo1", "Mo2", "Mo3", "Ag1", "Ag2"]
filter_names = ["Cu", "Mo100", "Mo200", "Mo450", "Ag400", "Ag800"]

def get_transmissions(key):
    t1 = transmissions_lookup_table.lookupValue(key, "T1")
    t2 = transmissions_lookup_table.lookupValue(key, "T2")
    t3 = transmissions_lookup_table.lookupValue(key, "T3")
    t4 = transmissions_lookup_table.lookupValue(key, "T4")
    return [t1, t2, t3, t4]

def list_transmissions(sort_key="Energy"):
    column_names = transmissions_lookup_table.getScannableNames()
    if sort_key not in column_names :
        print "Can only sort on one of the column names: " +str(column_names)
        return
    
    print column_names
    
    unsorted_energies = []
    for row_index in transmissions_lookup_table.lookupKeys:
        unsorted_energies.append((row_index, transmissions_lookup_table.lookupValue(row_index, sort_key)))
    sorted_energies = sorted(unsorted_energies, key=lambda pair: pair[1])
    
    for entry in sorted_energies:
        index=entry[0]
        filter_name = filter_names[int(transmissions_lookup_table.lookupValue(index, "Filterset"))]
        energy = transmissions_lookup_table.lookupValue(index, "Energy")
        energy_unit = transmissions_lookup_table.lookupUnitString("Energy")
        t = get_transmissions(index)
        date = int(transmissions_lookup_table.lookupValue(index, "Date"))
        print (str(int(index)) + ": " + filter_name + ", " + str(energy) + energy_unit + ", " + str(t[0]) + ", " + str(t[1]) + ", " + str(t[2]) + ", " + str(t[3]) + ", " + str(datetime.fromtimestamp(date)))

def load_transmissions(index):
    fatt.setFilterTransmissions(get_transmissions(index))
    fatt.setFilterSet(epics_filter_names[int(transmissions_lookup_table.lookupValue(index, "Filterset"))])

def save_current_transmissions():
    filterset_number = epics_filter_names.index(fatt.getFilterSet())
    t=fatt.getFilterTransmissions()
    add_transmissions(filter_names[filterset_number], dcm1energy.getPosition(), t[0], t[1], t[2], t[3])

def add_transmissions(filterset, energy, T1, T2, T3, T4):
    if filterset not in filter_names :
        print("Filter set not recognised, valid filter sets are the following: ")
        print(filter_names)
        return
    filterset_number = filter_names.index(filterset)
    index = transmissions_lookup_table.getLookupKeys()[-1]+1
    row = str(int(index)) +"\t" +str(filterset_number) +"\t" +str(energy) +"\t" +str(T1) +"\t" +str(T2) +"\t" +str(T3) +"\t" +str(T4) +"\t" +str(time.time()) +"\n"
    with open(transmissions_lookup_table.getPath(), "a") as tempfile :
        tempfile.write(row)
    transmissions_lookup_table.reload()
    print("Added to transmissions table")

def remove_transmissions(index):
    if index not in transmissions_lookup_table.getLookupKeys():
        print("Index not found in table")
        return
    with open(transmissions_lookup_table.getPath(), "r") as read :
        content = read.readlines()
    with open(transmissions_lookup_table.getPath(), "w") as write :
        for row in content :
            if not row.startswith(str(index) + "\t"):
                write.write(row)
            else: 
                print("Removing [" +row.strip("\n") +"] from transmissions table")
    transmissions_lookup_table.reload()

alias(list_transmissions)
alias(load_transmissions)
alias(save_current_transmissions)
alias(add_transmissions)
alias(remove_transmissions)

# Default to off
if isLive():
    autofoff()
