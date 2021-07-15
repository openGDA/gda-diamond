import h5py
import numpy as np
from scipy import ndimage, misc
import matplotlib.pyplot as plt

def get_image_dataset_from_hdf(scanfilenamehdf):
    data = h5py.File(scanfilenamehdf, 'r')
    data = data['entry']['data']['data']
    data = np.asarray(data)
    return data

def write_nexus(nexuspath, image, x_axes, y_axes):
    with h5py.File(nexuspath, "w") as file:
        file["/entry/image/data"] = image
        file["/entry"].attrs["NX_class"] = "NXentry"
        nxdata = file["/entry/image"]
        nxdata.attrs["NX_class"] = "NXdata"
        nxdata.attrs["signal"] = "data"
        nxdata.attrs["axes"] = ["psy", "psx"]
        nxdata["psy"] = y_axes
        nxdata["psx"] = x_axes
        nxdata.attrs["psy_indices"] = 0
        nxdata.attrs["psx_indices"] = 1

def get_data_from_dat_file(dat_filepath):
    data = []
    with open(dat_filepath, 'r') as f:
        d = f.readlines()
        for i in d:
            k = i.rstrip().split("=")
            if "psx" in i or "psy" in i or "FOV" in i or "leem_rot" in i:
                data.append(k)
                print(str(k))
    return float(data[0][1]), float(data[1][1]), float(data[2][1])/1000, float(data[3][1])

def get_extent_vals(psx, psy, fov):
    x_start_motor_pos = (psx - fov/2)
    y_start_motor_pos = (psy - fov/2)
    x_end_motor_pos = (psx + fov/2)
    y_end_motor_pos = (psy + fov/2)
    extent_vals = [x_start_motor_pos, x_end_motor_pos,
                   y_start_motor_pos, y_end_motor_pos]    
    return extent_vals

def get_nxs_file_axes_arrays(extent_vals, img_shape):
    x_axes = np.linspace(extent_vals[0], extent_vals[1], img_shape[1])
    y_axes = np.linspace(extent_vals[2], extent_vals[3], img_shape[0])
    return x_axes, y_axes

### MAIN CODE ###
def create_nxs_file(input_hdf_file, output_filename):
    input_dat_file = input_hdf_file.replace("medipix-", "")
    input_dat_file = input_dat_file.replace("hdf", "dat")
    psx, psy, fov, leem_rot = get_data_from_dat_file(input_dat_file)
    extent_vals = get_extent_vals(psx, psy, fov)
    dataset = get_image_dataset_from_hdf(input_hdf_file)
    image = dataset[0, :, :]
    image = ndimage.rotate(image, -leem_rot, reshape=False)
    x_axes, y_axes = get_nxs_file_axes_arrays(extent_vals, image.shape)
    write_nexus(output_filename, image, x_axes, y_axes)

input_hdf_file = "/dls/i06/data/2019/cm22966-4/medipix-230223.hdf"
output_filename = "/dls/i06/data/2019/cm22966-3/processing/optical_microscope/SEM_calibration_data/medipix-230223-3.nxs"
create_nxs_file(input_hdf_file, output_filename)





