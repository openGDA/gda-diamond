'''
define sample position for transfer

the sample positions for transfer are always the same below 100K, irrespective of the sample plate. 
"z" will change in case we transfer at 300K. But 95% of the cases we transfer below 100K.

Created on Jun 15, 2023

@author: fy65
'''
from gdaserver import m5tth, gv16, gv17, x, y, z, phi, chi, th  # @UnresolvedImport
from time import sleep

def go_transfer():
    m5tth.moveTo(50)
    gv16('Close')
    gv17('Close')
    x.asynchronousMoveTo(-1.73)
    y.asynchronousMoveTo(0)
    z.asynchronousMoveTo(-3.8)
    phi.asynchronousMoveTo(0)
    chi.asynchronousMoveTo(0)
    th.asynchronousMoveTo(-54)
    while x.isBusy() or y.isBusy() or z.isBusy() or phi.isBusy() or chi.isBusy() or th.isBusy():
        sleep(0.1)
