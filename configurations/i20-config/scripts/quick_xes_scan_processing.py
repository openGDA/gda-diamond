from uk.ac.diamond.daq.scanning import ScanHookParticipant
import re
import scisoftpy as dnp

from org.eclipse.dawnsci.hdf5.nexus import NexusFileHDF5
from os.path import dirname, basename
from __builtin__ import False
from time import sleep


# Load single dataset from Nexus file, then close immediately.
# Using dnp.io.load to get data from Nexus file seems to leave 'dangling' nexus file connections
# which cause problems when trying to add data using Nexux template 
def load_dataset(file, fullpath, get_link_target=False):
    dataname = basename(fullpath)
    grouppath = dirname(fullpath)
    print("Loading %s/%s from %s" % (grouppath, dataname, file))
    f = None
    try:
        f = NexusFileHDF5.openNexusFileReadOnly(file)
        group = f.getGroup(grouppath, False)
        if get_link_target : 
            return group.getNode(dataname).getAttributeNames()
        else : 
            datanode = f.getData(group, dataname)
            return dnp.array(datanode.getDataset().getSlice(None))
    finally:
        # print("Finally called")
        if f is not None:
            f.close()
    
from org.eclipse.january.dataset import DatasetFactory
def add_dataset(file, fullpath, data) :
    dataname = basename(fullpath)
    grouppath = dirname(fullpath)
    print("Adding dataset to %s in %s" % (fullpath, file))

    dataset = DatasetFactory.createFromObject(data)
    dataset.setName(dataname)
    try :
        f = NexusFileHDF5.openNexusFile(file)
        # 1 = LZW compression
        # True = create path
        f.createData(grouppath, dataset, True)
    finally :
        if f is not None :
            f.close()
            
def path_is_valid(file, path):
    f = None
    try :
        f = NexusFileHDF5.openNexusFileReadOnly(file)
        return f.isPathValid(path)
    finally :
        if f is not None :
            f.close()

def remove_node(file, fullpath) :
    f = None
    try :
        dataname = basename(fullpath)
        grouppath = dirname(fullpath)
        f = NexusFileHDF5.openNexusFile(file)
        f.removeNode(grouppath, dataname)
    finally :
        if f is not None :
            f.close()
            
from java.net import URI
def add_link(file, ext_source, dest, is_group=False, is_external=False) :
    f = None
    try :
        f = NexusFileHDF5.openNexusFile(file)
        if is_external :
            print("Adding ext link from %s to %s"%(dest, ext_source))
            f.linkExternal(URI(ext_source), dest, is_group)
        else :
            print("Adding internal link from %s to %s"%(dest, ext_source))
            f.link(ext_source, dest)
    finally :
        if f is not None :
            f.close()              
               
class QuickXesNexusProcessor :
     
    def __init__(self) :
        self.filename = None
        self.entryName = "entry/"

        ## Group where processed data should be written to
        self.processedPath = "/entry/FFI1"
        
        # Path to medipix 'sum' data
        self.medipixDataPath = "/entry/Medipix%d_sum/sum"
        self.numDetectors = 2
        
        # Path to the I1 ionchamber data
        self.I1DataPath = "/entry/I1/data"
        self.scanRankPath = "/entry/diamond_scan/scan_rank"

        self.scanAxesPath = "/entry/diamond_scan/scan_axes"
        self.pointStartTimes = "point_start_times"
        
    def setup_dummy(self):
        self.medipixDataPath = "/entry/medipix%d_addetector_total/total"
        self.numDetectors = 1

    def add_link(self, name, target, external=False):
        add_link(self.filename, target, name, is_group=False, is_external=external)
        
    def add_dataset(self, fullpath, data)  :
        add_dataset(self.filename, fullpath, data)
        
    def load_dataset(self, fullpath=None): 
        return load_dataset(self.filename, fullpath)

    def add_processed_data(self) :
        self.show_info("Adding processed data to "+self.filename)
        group_path=self.processedPath

        if path_is_valid(self.filename, group_path) :
            print("Removing old processed data at %s "%(group_path))
            remove_node(self.filename, group_path)
        
        if not LocalProperties.isDummyModeEnabled() :
            self.add_medipix_ffI1()
        
        self.add_pitch_energy_values()
        
        self.add_time_values()

            
    def get_i1_values(self) :
        return self.load_dataset(self.I1DataPath)
    
    def get_medipix_sum(self, num) :
        return self.load_dataset(self.medipixDataPath%(num))

    def get_ff_i1(self, num):
        ff = self.get_medipix_sum(num)
        i1 = self.get_i1_values()
        return ff/i1
    
    def get_scan_axes(self) :
        return self.load_dataset(self.scanAxesPath)
    
    def get_xes_energy_scannable(self, axis_name):
        if re.search("lo.*pitch", axis_name) is not None :
            return XESEnergyLower
        elif re.search("up.*pitch", axis_name) is not None :
            return XESEnergyUpper
        else :
            raise Exception("Could not find XESEnergy scannable corresponding to axis "+axis_name)
            
    # Compute energy (eV) from given pitch value (degrees)
    # using XES energy scannable
    def get_energy(self, XESEnergyScannable, pitch) :
        bragg_angle = 90 - math.fabs(pitch) # Bragg angle = 90 - pitch (degrees)
        return XESEnergyScannable.convertAngleToEnergy(bragg_angle)
    
    def add_time_axis_link(self):
        # Link target for 'dummy' malcolm scans
        link_target_name="/entry/diamond_scan/point_start_times"
        link_name = self.processedPath+"/"+self.pointStartTimes
        external_link = False
        
        # If link doesn't exist then data is from Malcolm scan and need to link
        # to PCAP data in hdf file written by panda :
        if not path_is_valid(self.filename, link_target_name) :
            external_link = True
            scan_name = basename(self.filename).replace(".nxs", "")
            link_target_name=scan_name+"/"+scan_name+"-PANDABOX-01.h5#entry/NDAttributes/PCAP.TS_START.Value"

        print("Adding link %s to time information in %s"%(link_name, link_target_name))
        self.add_link(link_name, link_target_name, external_link)
        
        return link_name
    
    def get_scan_rank(self):
        return len(self.get_scan_axes())
    
    def get_first_time(self, all_times) :
        scan_rank = self.get_scan_rank()
        if scan_rank == 1 :
            return all_times[0]
        elif scan_rank == 2 :
            return all_times[0][0]
        print("Unexpected scan rank = %d - using 0 for time of first point in scan"%(scan_rank))
        return 0
    
    def get_relative_times(self, all_times) :        
        return all_times - self.get_first_time(all_times)
    
    def get_start_times(self, all_times) :
        first_time = self.get_first_time(all_times)
        start_times=[]
        for t in all_times :
            start_times.append(min(t) - first_time)
        return start_times


    def show_info(self, msg):
        print("--- "+str(msg)+" ---")
        
    ## Make Links to the detector and I1 datasets, generate FFI1 values
    def add_medipix_ffI1(self):
        self.show_info("Adding Medipix FFI1 values")

        group_path=self.processedPath

        # link to the ROI counts (FF)
        self.add_link(group_path+"/FF_medipix1", self.medipixDataPath%(1))
        self.add_link(group_path+"/FF_medipix2", self.medipixDataPath%(2))
        self.add_link(group_path+"/I1", self.I1DataPath)

        ## Add the FFI1 values - convert to list from array first so Nexus writing is happy
        self.add_dataset(group_path+"/FFI1_medipix1", self.get_ff_i1(1).tolist())
        self.add_dataset(group_path+"/FFI1_medipix2", self.get_ff_i1(2).tolist())
        
        
    def add_pitch_energy_values(self):
        self.show_info("Adding pitch and XES energy values")

        # Add link to the pitch demand values :
        # Read the names of the scan axes from Nexus file
        scan_axes = self.get_scan_axes()
        
        # xes pitch is the last one
        pitch_values_name = scan_axes[len(scan_axes)-1]
        print("Pitch values axis : "+pitch_values_name)
        pitch_values_path = "/entry/instrument/"+pitch_values_name+"/value_set"
        self.add_link(self.processedPath+"/pitch_demand_values", pitch_values_path)
        
        ## Create energy axis : load the pitch demand values and calculate the energy for each
        xes_energy_scannable = self.get_xes_energy_scannable(pitch_values_name);
        print("XES energy scannable for pitch axis : "+xes_energy_scannable.getName())
        pitch_vals = self.load_dataset(pitch_values_path)
        energy_vals=[]
        for pitch in pitch_vals :
            energy_vals.append(self.get_energy(xes_energy_scannable, pitch))
            
        self.add_dataset(self.processedPath+"/"+xes_energy_scannable.getName(), energy_vals)

  
    def add_time_values(self) :
        self.show_info("Adding time axis values")
        group_path=self.processedPath

        # Add link to captured point start time data
        start_times_path = self.add_time_axis_link()
        
        # read the time data (make sure we are dealing with floats so DatasetFactory.createfroMObject is happy 
        # (dummy malcolm uses 64-bit ints for time data)
        start_times_data = self.load_dataset(start_times_path).astype(float)
        self.scan_rank = self.get_scan_rank()
        
        # add relative time and spectrum start time data
        self.add_dataset(group_path+"/relative_point_start_times", self.get_relative_times(start_times_data).tolist())
        
        # Only add spectrum start times for 2d scans
        if self.get_scan_rank() == 2 :
            self.add_dataset(group_path+"/spectrum_start_times", self.get_start_times(start_times_data))

class ScanHooks(ScanHookParticipant) :
    
    def __init__(self, name) :
        self.setName(name)
        self.run_post_processing = False
        self.sleep_time_sec = 3
        
    def atPrepareForScan(self, scanModel):
        # Look at scannable names and work out if processing is required at end of the scan
        scnNames = scanModel.getScanInformation().getScannableNames();
        last_name = scnNames.get(scnNames.size()-1)
        self.run_post_processing = last_name.endswith("pitch")
        print("Running scan with "+last_name+" - run post processing = "+str(self.run_post_processing))

    def atFileDeclared(self, filename):
        if filename.endswith(".nxs") :
            self.filename = filename
    
    def atScanFinally(self) :
        print("ScanEnd: Scan finished. Nexus File name "+self.filename)
        if not self.run_post_processing :
            return
        
        if self.sleep_time_sec > 0 :
            print("Sleeping for %d seconds before processing data"%(self.sleep_time_sec))
            sleep(self.sleep_time_sec)
        
        # Stop the detectors - seem to be left armed when doing single line scan
        print("Stopping medipix detectors")
        medipix1.stop()
        medipix2.stop()
        sleep(1)
        
        scanProcessor = QuickXesNexusProcessor()
        if LocalProperties.isDummyModeEnabled() :
            scanProcessor.setup_dummy()
        scanProcessor.filename = self.filename
        scanProcessor.add_processed_data()
        
scanEndHook = ScanHooks("scanEndHook")
scanEndHook.addScanParticipant()

