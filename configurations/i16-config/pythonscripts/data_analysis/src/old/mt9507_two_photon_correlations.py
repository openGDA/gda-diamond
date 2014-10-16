from dlstools import dataloader
from dlstools.tictoc import tictoc
import h5py

#run pilfiles_to_hdf5.py first to get each scan into single hdf5 compressed file

scans=range(450745,450755)# pdc etazero+0.056 atten 0

datapath='/dls/i16/data/2014/cm4968-3/'
h5infmt=datapath+'processing/scan_images_%i.h5'
h5out=datapath+'processing/two_photon_%i.h5' % scans[0]     #label output file with first scan number

(nn, ni, nj)=h5py.File(h5infmt % scans[0], 'r')['images'].shape #get shape (no. images and image dimensions)
outfile = h5py.File(h5out,'w')
corr2 = outfile.create_dataset("corr2",(ni, nj, ni, nj), int16) #two-event correlations
sumdat = outfile.create_dataset("sum", (ni, nj), int32)


ncoinc=0; nim=0
for scan in scans:
    t=tictoc()
    infile = h5py.File(h5infmt % scan, 'r')
    print h5infmt % scan
    for n in range(nn): #image number
        imdat=infile['images'][n]
        nim+=1
        sumdat+=imdat               # add to sum image
        print n
        for i in range(ni): #pixel i
            for j in range(nj): #pixel j
                if imdat[i][j]>0:
                    #pass
                    corr2[i,j]+=imdat ## 0.4 sec/image without file out; 70 sec with (32 bit)
    infile.close()
print 'Found %i coincidences in %i images' % (ncoinc, nim)
outfile.close()

