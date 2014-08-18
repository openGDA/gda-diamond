#from mpl_toolkits.mplot3d import Axes3D
#import matplotlib.pyplot as fitplt
from dlstools import dataloader
#from dlstools.quickfit import *
#from dlstools.dirty_fit import fit

path='/dls/i16/data/2014/mt9485-1/'
d=dataloader.dlsloader(path+'%i.dat')
#p=dataloader.piloader(d, lambda obj: path+obj.pilatus100k_path_template)




print d(454161)
#print p(2)
#figure(); pcolor(p.image0); axis('tight'); title(p.file)

#print d(447336)
#figure(); plot(d.eta, d.sum); title(d.file+'\n'+d.cmd); axis('tight'); grid(1)
#fit(pv_c)

