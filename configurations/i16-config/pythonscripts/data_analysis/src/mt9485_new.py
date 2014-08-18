from dlstools import dataloader

path='/dls/i16/data/2014/mt9485-1/'
d=dataloader.dlsloader(path+'%i.dat')
#p=dataloader.piloader(d, lambda obj: path+obj.pilatus100k_path_template)
m=dataloader.tiffloader(path+'/snapped-data/medipix/%05i.tif')

print d(454161)

imdat=0
for mpix_im in range(6027,6037):
    print m(mpix_im)
    imdat+=m.image0
figure(); pcolor(imdat); axis('tight'); clim(0,10)


#print p(2)
#figure(); pcolor(p.image0); axis('tight'); title(p.file)

#print d(447336)
#figure(); plot(d.eta, d.sum); title(d.file+'\n'+d.cmd); axis('tight'); grid(1)
#fit(pv_c)

