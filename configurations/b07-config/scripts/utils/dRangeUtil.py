'''
drange(start, stop, step) function is designed to provide a list of values whose number of decimal places are exactly the same as step value.
Different from frange(start, stop, step) which has floating point inaccuracy build in.

Created on 23 Jan 2014

@author: fy65
'''
from decimal import Decimal
def drange(start,end,step):
    'Decimal version of range():   drange(start,end,step) to provide exact number of decimal places as step value inputed'
    dstep=Decimal(str(step));dstart=Decimal(str(start)).quantize(dstep); dend=Decimal(str(end)).quantize(dstep);
    #print dstep, dstart, dend
    r=abs(dend-dstart)
    dstep=abs(dstep)*(dend-dstart)/r
    #print r, dstep
    #print abs(r/dstep)
    limit=Decimal(str(1e6))
    if abs(r/dstep)>limit:
        print 'Too many points in list!'
        raise
    out=[dstart]
    while (abs(out[-1]-dstart)-abs(dstep/limit))<r:
        out+=[out[-1]+dstep]
    return [float(x) for x in out[:-1]]
