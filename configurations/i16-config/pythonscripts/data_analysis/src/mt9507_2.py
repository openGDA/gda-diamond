from dlstools import dataloader
from dlstools.tictoc import tictoc
import h5py


datapath='/dls/i16/data/2014/cm4968-3/'
h5fmt='/home/i16user/steve/tmp/pdc_corr_%i.h5'

d=dataloader.dlsloader(datapath+'%i.dat')
p=dataloader.piloader(d, lambda obj: datapath+obj.pilatus100k_path_template)
d(450742); shape=p(1).image0.shape


ncoinc=0; nim=0
t=tictoc()
for scan in range(450745,450755):# pdc etazero+0.056 atten 0
    d(scan)
    fname= h5fmt % scan
    file = h5py.File(fname,'w')
    corr2 = file.create_dataset("corr2",shape+shape, int16) #two-event correlations
    sumdat = file.create_dataset("sum",shape, int32)

    for filepath in d.filepath:
        pmult=dataloader.piloader(filepath.replace('nnnnn','%05i'))
        for imno in range(200):
            pmult(imno); imdat=pmult.image0
            print pmult.file
            nim+=1
            sumdat+=imdat               # add to sum image
            for i in range(shape[0]):
                for j in range(shape[1]):
                    if imdat[i][j]>0:
                        corr2[i,j]+=imdat ## this takes most of the time - will be quick if sparse images (50 sec on laptop with full image)
    file.close()
print 'Found %i coincidences in %i images' % (ncoinc, nim)

