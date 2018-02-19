'''
Created on 3 Dec 2014

@author: dqz93389
'''
from utils.dRangeUtil import drange
from scan.concurrentAnalyserScan import pathscan

#jenergy.moveTo(0.25)

nsteps=8
xstart=2.1
xend=1.9

zstart=2.498
zend=2.84

dx=(xstart-xend)/nsteps
dz=(zstart-zend)/nsteps


xpoints=drange(xstart, xend, dx)
#ypoints=drange(-552.75, -549.5, 0.05)
zpoints=drange(zstart, zend, dz)
if len(xpoints) != len(zpoints):
    raise ValueError("The number of path points for each scannables must the same.")
path=zip(xpoints, zpoints)
scanpath=[]
for l in path:
    scanpath.append(list(l))
scanpath=tuple(scanpath)
print "scan path: ", scanpath

analyserscan((smpmx,smpmz), scanpath, smpmy, -552.18, -551.66, 0.05, ew4000, "user.seq")
#pathscan((smpmx,smpmz), scanpath,smpmy, -550.8, -550.4, 0.01, smpmiamp39)
#pathscan((x,z), scanpath,y, -550.8, -550.4, 0.01, smpmiamp39)

#pos fsi1 'In'

#analyserpathscan((smpmx,smpmz), scanpath, *args):
#for y in ypoints:
    #smpmy.moveTo(y)
    #analyserpathscan((smpmx,smpmz), scanpath, ew4000, "user.seq", smpmy)
    #pathscan((smpmx,smpmz), scanpath, smpmy, smpmamp39, 1)
    
