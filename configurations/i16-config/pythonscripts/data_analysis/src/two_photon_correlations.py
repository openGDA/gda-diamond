import sys
#command line params: datapath scan_no firstpoint lastpoint  (indexed from 1)
# /dls/i16/data/2014/cm4968-3/ 1234567 1 100
datapath=sys.argv[1]
scan_no=int(sys.argv[2])
firstpoint=int(sys.argv[3])
lastpoint=int(sys.argv[4])


sys.path.append('/dls_sw/i16/software/gda/config/pythonscripts/data_analysis')
from dlstools import dataloader
from dlstools.tictoc import tictoc
from numpy import *
import h5py



# This version works with a single scan passed as a command line argument
#scan_no=450745

print '=== Processing scan: %i, point from %i to %i' % (scan_no, firstpoint,lastpoint) 

#path='/dls/i16/data/2014/cm4968-3/'

d=dataloader.dlsloader(datapath+'%i.dat')
p=dataloader.piloader(d, lambda obj: datapath+obj.pilatus100k_path_template)

#datapath='/dls/i16/data/2014/cm4968-3/'
h5outfmt=datapath+'processing/twophoton_%i_%i_%i.h5'
ni, nj=195, 487



print '=== Making zeros array'
ijij_dat=zeros((ni, nj, ni, nj), 'int16')
sum_dat=zeros((ni, nj), 'int32')
print '=== Made zeros array'    
ncoinc=0; nim=0
d(scan_no)
icount=0
for filepath in d.filepath[firstpoint-1:lastpoint]:
    icount+=1
    pmult=dataloader.tiffloader(filepath.replace('nnnnn','%05i'))
    for imno in range(200):
        pmult(imno)
        imdat=int8(pmult.image0)
        sum_dat+=imdat
        nim+=1
        print pmult.file
        for i in range(ni):
            for j in range(nj):
                if imdat[i, j]>0:
                    ijij_dat[i, j]+=imdat[i, j]*imdat
                    
#    if icount % 10 == 0: #save after each 10 scan points - could do it just once at the end but this shows progress
h5out=h5outfmt % (scan_no, firstpoint, lastpoint) 
outfile = h5py.File(h5out,'w') 
corr2 = outfile.create_dataset("corr2",(ni, nj, ni, nj), int16, chunks=(1, nj, ni, nj), compression='gzip', compression_opts=1) #two-event correlations
imsum = outfile.create_dataset("sum",(ni, nj), int32, compression='gzip', compression_opts=1) #two-event correlations
corr2[...]=ijij_dat  #save after each scan point - could do it just once at the end but this shows progress - seems to take a long time...
imsum[...]=sum_dat
outfile.close()




