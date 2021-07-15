
import os
import numpy as np
import h5py
import matplotlib.pyplot as plt

path = "/dls/i06/data/2019/cm22966-3/processing/optical_microscope"

# Create a list of the image files to stitch and sort by numerical order
hdf_files = []
for file in os.listdir(path):
    if file.endswith(".hdf"):
        hdf_files.append(str(os.path.join(path, file)))

hdf_files.sort()

for file in hdf_files:
    print(file)

f = h5py.File(hdf_files[0], 'r')
print(list(f.keys()))
print(list(f['entry'].keys()))

dset = f['entry']['data']['data']
print(dset.shape)
print(dset.dtype)

image = np.asarray(dset[0, : , :])
print(np.shape(image))

plt.imshow(image)
plt.show()