from dlstools import dataloader
from dlstools.tictoc import tictoc
import h5py
#(195, 487)
#run pilfiles_to_hdf5.py first to get each scan into single hdf5 compressed file
# this version keeps 3d data in memory (need too much memory for 4d data)

scans=range(450745,450755)# pdc etazero+0.056 atten 0

datapath='/dls/i16/data/2014/cm4968-3/'
h5infmt=datapath+'processing/scan_images_%i.h5'
h5out=datapath+'processing/two_photon_%i.h5' % scans[0]     #label output file with first scan number

(nn, ni, nj)=h5py.File(h5infmt % scans[0], 'r')['images'].shape #get shape (no. images and image dimensions)
outfile = h5py.File(h5out,'w')
corr2 = outfile.create_dataset("corr2",(ni, nj, ni, nj), int16, chunks=(1, nj, ni, nj)) #two-event correlations
sumdat = outfile.create_dataset("sum", (ni, nj), int32)

ncoinc=0; nim=0
for scan in scans:
    t=tictoc()
    infile = h5py.File(h5infmt % scan, 'r')
    print h5infmt % scan
    for n in range(nn): #image number
        imdat=int16(infile['images'][n])#to int16 just in case it is faster (needs testing)
        nim+=1
        sumdat+=imdat               # add to sum image
        for i in range(ni): #pixel i
            jij_dat=corr2[i]
            for j in range(nj): #pixel j
                print 'scan: %i\tn: %i\ti: %i\tj: %i' % (scan, n, i, j)
                if imdat[i][j]>0:
                    #pass
                    jij_dat[j]+=imdat
            corr2[i]=jij_dat
    infile.close()
print 'Found %i coincidences in %i images' % (ncoinc, nim)
outfile.close()

'''
infile = h5py.File(h5infmt % scans[0], 'r')
imdat=infile['images'][0]
outfile.close()
infile.close()
24.*3600/ni/200000 #time allowed for one i loop
24.*3600/200000 #time allowed for one image
'''