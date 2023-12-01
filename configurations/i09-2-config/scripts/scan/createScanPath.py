'''
Created on 23 Jan 2014

@author: fy65
'''
from utils.dRangeUtil import drange

xpoints=drange(2.597, 0.203, 0.04728)
zpoints=drange(1.152, 3.9, -0.05496)

if len(xpoints) != len(zpoints):
    raise ValueError("The number of path points for each scannables must the same.")

path=zip(xpoints, zpoints)

scanpath=[]
for l in path:
    scanpath.append(list(l))
scanpath=tuple(scanpath)
print("scan path: ", scanpath)

