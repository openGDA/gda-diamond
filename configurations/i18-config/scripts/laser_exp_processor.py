from os.path import dirname, basename
from org.eclipse.dawnsci.hdf5.nexus import NexusFileHDF5
from org.eclipse.january.dataset import DatasetFactory

def path_is_valid(file, path):
    f = None
    try :
        f = NexusFileHDF5.openNexusFileReadOnly(file)
        return f.isPathValid(path)
    finally :
        if f is not None :
            f.close()

def remove_node(file, fullpath) :
    if not path_is_valid(file, fullpath) :
        return 

    f = None
    try :
        dataname = basename(fullpath)
        grouppath = dirname(fullpath)
        f = NexusFileHDF5.openNexusFile(file)
        f.removeNode(grouppath, dataname)
    finally :
        if f is not None :
            f.close()
    
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

def add_dataset(file, fullpath, data) :
    dataname = basename(fullpath)
    grouppath = dirname(fullpath)
    print("Adding dataset to %s in %s" % (fullpath, file))
        
    dataset = DatasetFactory.createFromObject(data)
    dataset.setName(dataname)
    
    f = None
    try :
        f = NexusFileHDF5.openNexusFile(file)
        # 1 = LZW compression
        # True = create path
        f.createData(grouppath, dataset, True)
    finally :
        if f is not None :
            f.close()

from org.slf4j import LoggerFactory
import traceback
import scisoftpy as dnp

class ProcessLaserData :

    def __init__(self):
        self.logger = LoggerFactory.getLogger("ProcessLaserData")
        
        self.detector_name = "qexafs_counterTimer01"
        self.processed_path = "/entry1/processed/"
        self.end_frame_range = 50,60
        self.start_frame_range = 0,10
    
    def get_energy(self, filename) :
        energy_2d_data = load_dataset(filename, '/entry1/'+self.detector_name+"/energy")
        energy_data = energy_2d_data[:,0]
        return list(energy_data)
        
    def process_data(self, filename):
        self.logger.info("Computing processed datasets at end of scan")
        
        i0_data = load_dataset(filename, '/entry1/'+self.detector_name+"/I0")
        iapd_data = load_dataset(filename, '/entry1/'+self.detector_name+"/Iother")
        iapd_norm = iapd_data/i0_data
        num_time_frames=iapd_norm.shape[1]
        
        #average of the last few frames for wach row of iapd_norm data
        end_range = self.end_frame_range[1]-self.end_frame_range[0]
        end_timeframe_data = [sum(d)/end_range for d in iapd_norm[:, self.end_frame_range[0]:self.end_frame_range[1]]]
        
        start_range = self.start_frame_range[1]-self.start_frame_range[0]
        start_timeframe_data = [sum(d)/start_range for d in iapd_norm[:, self.start_frame_range[0]:self.start_frame_range[1]]]

        start_end_diff = [start - end for start, end in zip(start_timeframe_data, end_timeframe_data) ]
        
        #subtract last_timeframe_data from each row of normalised apd_normdata 
        iapd_norm_sub = [a-b for a, b in zip(iapd_norm, end_timeframe_data)]
        
        return i0_data, iapd_data, iapd_norm, start_timeframe_data, end_timeframe_data, start_end_diff, iapd_norm_sub
    
    def add_processed_data(self, filename, overwrite=False):
        try :
            self.add_datasets(filename, overwrite)
        except :
            stacktrace=traceback.format_exc()
            print("Problem adding processed datasets : "+stacktrace)
            self.logger.warn("Problem adding processed datasets to {} : {}", filename, stacktrace)
            
    def add_datasets(self, filename, overwrite=False):
        i0_data, iapd_data, iapd_norm, start_timeframe_data, end_timeframe_data, start_end_diff, iapd_norm_sub = self.process_data(filename)
        
        energy = self.get_energy(filename)
        print(energy.__class__)
        data_to_add = {"Inorm" : iapd_norm.tolist(), "InormSub" : self.to_list(iapd_norm_sub),
                       "EndAvg" : end_timeframe_data, "StartAvg" : start_timeframe_data,
                       "StartEndDiff" : start_end_diff, "energy" : energy}
        
        self.logger.info("Adding processed datasets to {}", filename)
        for node_name, dataset in data_to_add.items() :
            node_path = self.processed_path+node_name
            if overwrite :
                remove_node(filename, node_path)
            self.logger.info("Adding {}", node_path)
            add_dataset(filename, node_path, dataset)
        self.logger.info("Finished")

    def to_list(self, two_d_arr) :
        return [list(row) for row in two_d_arr]

laser_exp_processor = ProcessLaserData()

