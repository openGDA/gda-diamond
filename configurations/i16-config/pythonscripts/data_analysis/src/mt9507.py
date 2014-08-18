from dlstools import dataloader
from dlstools.tictoc import tictoc

import pickle

#path='/media/sf_data/mt9507-1/'
path='/dls/i16/data/2014/cm4968-3/'
d=dataloader.dlsloader(path+'%i.dat')
p=dataloader.piloader(d, lambda obj: path+obj.pilatus100k_path_template)
   



##zeros(195,487,195,487) gives memory error but zeros(pmult.image0.shape+(pmult.image0.shape[1],), dtype=numpy.int16) is ok (3d array)



print d(450742) #eta scan
print p(2)
#figure(); pcolor(p.image0); axis('tight'); title(p.file)

#p.sequence(d.path)
#p.s.image0[0]


#for imno in d.path:
#    print p.s.image0[imno-1].shape


newim=zeros(p.image0.shape,dtype=numpy.int32)
ncoinc=0; nim=0
t=tictoc()
for scan in range(450745,450755):# pdc etazero+0.056 atten 0
    d(scan)
    #for filepath in d.filepath[0:1]:
    for filepath in d.filepath:
        pmult=dataloader.piloader(filepath.replace('nnnnn','%05i'))
        for imno in range(200):
            pmult(imno)
            nim+=1
            if pmult.image0[49:52,149:152].sum()>0:
                newim+=pmult.image0
                ncoinc+=1

        
print t
#figure(); pcolor(pmult.image0); axis('tight'); title(pmult.file)
newim[149:152,149:152]=-9 #mark coincidence pixel block
filehandler = open('/home/i16user/tmp/newim.p', 'w') 
pickle.dump(newim, filehandler) 

figure(); pcolor(newim); axis('tight');
print 'Found %i coincidences in %i images' % (ncoinc, nim)

#filehandler = open('/home/i16user/tmp/newim.p', 'r') 
#newim1=pickle.load(filehandler)




