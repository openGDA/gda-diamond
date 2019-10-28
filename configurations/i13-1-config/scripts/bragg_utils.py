import numpy as np


def center_of_mass_3d(arr=None):
    array = double(array)
 
    tot = np.sum(np.sum(np.sum(array)))
 
    sz = np.size(array)
 
 
    nx = sz(2)
    ny = sz(1)
    if np.ndims(array) == 3:
        nz = sz(3); print nz
         
 
    xyz = []
 
    if np.ndims(array) == 3:
            [x, y, z] = np.meshgrid(np.linspace(-(nx - 1) / 2,(nx - 1) / 2), np.linspace(-(ny - 1) / 2:(ny - 1) / 2), np.linspace(-(nz - 1) / 2:(nz - 1) / 2))
            
    elif np.ndims(array) == 2:
            [x, y] = np.meshgrid(np.linspace(-(nx - 1) / 2:(nx - 1) / 2), np.linspace(-(ny - 1) / 2:(ny - 1) / 2))
                
 
 
 
 
                xyz(1) = np.sum(np.sum(np.sum(array * x))) / tot
                xyz(1) = xyz(1) + nx / 2
 
                xyz(2) = np.sum(np.sum(np.sum(array * y))) / tot
                xyz(2) = xyz(2) + ny / 2
 
    if np.ndims(array) == 3:
                    xyz(3) = np.sum(np.sum(np.sum(array * z))) / tot; print (xyz)
 
                    xyz(3) = xyz(3) + nz / 2
    return xyz
