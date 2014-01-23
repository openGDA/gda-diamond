'''
Created on 23 Jan 2014

@author: fy65
'''
from utils.dRangeUtil import drange

xpoints=drange(1, 2, 0.01)
print "x-points: ",xpoints
ypoints=drange(2, 3, 0.01)
print "y-points: ", ypoints
zpoints=drange(3, 4, 0.01)
print "z-points: ", zpoints
if len(xpoints) != len(ypoints) or len(xpoints) != len(zpoints):
    raise ValueError("The number of path points for each scannables must the same.")
scanpath=zip(xpoints, ypoints, zpoints)
print "scan path: ", scanpath

#pathscan((x,y,z),scanpath,[])