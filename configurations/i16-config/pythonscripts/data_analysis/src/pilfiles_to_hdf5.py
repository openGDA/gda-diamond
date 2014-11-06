from dlstools import dataloader
from dlstools.tictoc import tictoc
import h5py

#original script created 32 bit compressed files
#second version creates 8 bit (smallest allowed) uncompressed

datapath='/dls/i16/data/2014/cm4968-3/'
h5fmt=datapath+'processing/scan_images_%i.h5'
h5fmt=datapath+'processing/scan_images_8bit_%i.h5'

d=dataloader.dlsloader(datapath+'%i.dat')
p=dataloader.piloader(d, lambda obj: datapath+obj.pilatus100k_path_template)
d(450742); shape=p(1).image0.shape
nmult=200   #images per scan point

for scan in range(450745,450755):# pdc etazero+0.056 atten 0 #is 754 complete?
#for scan in range(450755,450761+1):# 761 is a partial set
#for scan in range(450762,450766):# the rest...
    d(scan)
    nrows=len(d.filepath)
    fname= h5fmt % scan
    file = h5py.File(fname,'w')
#    images = file.create_dataset("images",(nrows*nmult,)+shape, int32, compression='gzip', compression_opts=1, chunks=(1,)+shape)   
    images = file.create_dataset("images",(nrows*nmult,)+shape, int8, compression='gzip', compression_opts=1, chunks=(1,)+shape)   
    nim=0    
    for filepath in d.filepath:
        pmult=dataloader.piloader(filepath.replace('nnnnn','%05i'))
        for imno in range(nmult):
            pmult(imno);
            print pmult.file+' image number %i' % nim
            images[nim]=pmult.image0 # this line takes almost all of the time when compression is used
            nim+=1
    file.close()
