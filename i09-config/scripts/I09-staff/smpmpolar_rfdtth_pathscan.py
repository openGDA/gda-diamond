'''
Created on 3 Dec 2014

@author: dqz93389
'''
from utils.dRangeUtil import drange
from scan.concurrentAnalyserScan import pathscan

jenergy.moveTo(0.456)

nsteps=40
xstart=2.2
xend=1.8

zstart=2
zend=2.4

dx=(xstart-xend)/(nsteps-1)
dz=(zstart-zend)/(nsteps-1)


xpoints=drange(xstart, xend, dx)
zpoints=drange(zstart, zend, dz)
if len(xpoints) != len(zpoints):
    raise ValueError("The number of path points for each scannables must the same.")
path=zip(xpoints, zpoints)
scanpath=[]
for l in path:
    scanpath.append(list(l))
scanpath=tuple(scanpath)
print "scan path: ", scanpath

#analyserpathscan((smpmpolar,rfdtth), scanpath, ew4000, "user.seq",cleverIamp10,hm3iamp20)
pathscan((smpmpolar,rfdtth), scanpath, cleverIamp10,hm3iamp20)

#pos fsi1 'In'

    
