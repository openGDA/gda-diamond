from dlstools import dataloader
from dlstools.tictoc import tictoc
path='/media/sf_data/mt9507-1/'
d=dataloader.dlsloader(path+'%i.dat')
p=dataloader.piloader(d, lambda obj: path+obj.pilatus100k_path_template)





print d(447331)
print p(2)
#newim=zeros(p.image0.shape)
shape=p.image0.shape
imdat=p.image0

t=tictoc()

import h5py
fname='/home/spc93/tmp/pdc_corr2.h5'
file = h5py.File(fname,'w')
corr2 = file.create_dataset("corr2",shape+shape, int16) #two-event correlations
sumdat = file.create_dataset("sum",shape, int32)
corr2[0,0]=p.image0
corr2[0,1]=p.image0
sumdat=p.image0

sumdat+=imdat               # add to sum image
for i in range(shape[0]):
    for j in range(shape[1]):
        if imdat[i][j]>0:
            corr2[i,j]+=imdat ## this takes most of the time - will be quick if sparse images (50 sec on laptop with full image)



file.close()

print t


'''
file = h5py.File(fname, 'r')
corr2 = file["corr2"]
sumdat = file["sum"]
figure(); pcolor(corr2[0,0]); axis('tight');
figure(); pcolor(sumdat[...]); axis('tight');
file.close()
'''



