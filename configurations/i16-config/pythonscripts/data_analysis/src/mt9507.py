from dlstools import dataloader
from dlstools.tictoc import tictoc
#path='/media/sf_data/mt9507-1/'
path='/dls/i16/data/2014/cm4968-3/'
d=dataloader.dlsloader(path+'%i.dat')
p=dataloader.piloader(d, lambda obj: path+obj.pilatus100k_path_template)





print d(450742)
print p(2)
figure(); pcolor(p.image0); axis('tight'); title(p.file)

#p.sequence(d.path)
#p.s.image0[0]


#for imno in d.path:
#    print p.s.image0[imno-1].shape

newim=zeros(p.image0.shape)
t=tictoc()
for imno in d.path:
    p(imno)
    print p.image0.shape
    if sum(p.image0[10:20,10:20])>1:
        newim+=p.image0
print t



