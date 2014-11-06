#### plot out FeBO3 data July 2014

#from mpl_toolkits.mplot3d import Axes3D
#import matplotlib.pyplot as fitplt
from dlstools import dataloader
from dlstools.quickfit import *
from dlstools.dirty_fit import fit
from dlstools.dataloader import ScanSequence

path='/dls/i16/data/2014/cm4968-3/'
d=dataloader.dlsloader(path+'%i.dat')
p=dataloader.piloader(d, lambda obj: path+obj.pilatus100k_path_template)

#for scan in range(455580,455619):
#    d.note=''
#    d(scan); print d.cmd, d.note
    
ss=d.findscans(range(455580,455619), 'len(self.magrot)>1 and self.stoke==0')
d.sequence(ss)
                  
#figure(); pcolor(p.image0); axis('tight'); title(p.file)
#print d(447336)
#figure(); plot(d.eta, d.sum); title(d.file+'\n'+d.cmd); axis('tight'); grid(1)
#fit(pv_c)

