#### if not in DAWN
import sys
#sys.path.append('/dls_sw/i16/software/gda/config/pythonscripts/data_analysis/src/')
sys.path.append('/dls_sw/i16/software/gda/config/pythonscripts/data_analysis/dlstools/')
from numpy import *
#####



#from dlstools import dataloader
from dlstools.tictoc import tictoc
import h5py
#(195, 487)
#run pilfiles_to_hdf5.py first to get each scan into single hdf5 compressed file
# this version keeps 3d data in memory (need too much memory for 4d data)

scans=range(450745,450755)# pdc etazero+0.056 atten 0

datapath='/dls/i16/data/2014/cm4968-3/'
#h5infmt=datapath+'processing/scan_images_%i.h5'
h5infmt=datapath+'processing/scan_images_8bit_%i.h5' ##### test 8 bit version then delete
h5out=datapath+'processing/two_photon_%i.h5' % scans[0]     #label output file with first scan number

(nn, ni, nj)=h5py.File(h5infmt % scans[0], 'r')['images'].shape #get shape (no. images and image dimensions)
outfile = h5py.File(h5out,'w')
corr2 = outfile.create_dataset("corr2",(ni, nj, ni, nj), 'int16', chunks=(1, 1, ni, nj)) #two-event correlations
sumdat = outfile.create_dataset("sum", (ni, nj), 'int32')
infile = h5py.File(h5infmt % scans[0], 'r')

#hist(infile['images'][0].flatten(),bins=10,range=(-3,7))

t=tictoc()
for i in range(ni):
    print '=== Reading nj slice for i= ',i,': Time since last i loop: ',t
    tstr=t.__repr__()
    t.reset()
    nj_dat=infile['images'][:,i,:]
    jijdat=zeros((nj,ni,nj),'int16')
    for j in range(nj):
        print 'j=',j,' Time for last loop:',tstr
        for n in range(nn):
            if nj_dat[n,j]>0:
                jijdat[j]+=infile['images'][n]
    corr2[i]=jijdat



#time ~ 120 sec (may be faster wth different chunking - create two verions of h5py file?)
#t=tictoc()
#nj_dat=infile['images'][:,0,:]
#print '=== Time to read one nj slice: '+t.__repr__()

#took 1818 sec (30 mins)
#t=tictoc()
#for n in range(4000*nj):
#    ij_dat=infile['images'][0]
#print '=== Time to read 4000*nj ij slices (image): '+t.__repr__()



'''
infile = h5py.File(h5infmt % scans[0], 'r')
imdat=infile['images'][0]
outfile.close()
infile.close()
24.*3600/ni/200000 #time allowed for one i loop
24.*3600/200000 #time allowed for one image
'''
