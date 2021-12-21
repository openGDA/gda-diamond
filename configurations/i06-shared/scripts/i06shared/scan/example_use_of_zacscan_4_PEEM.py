'''
Provide an example script to demonstrate the use of ROIs in 'zacscan'

Created on 27 Jul 2018
NOT YET tested! Cannot be tested off-beamline as constant velocity scan is implemented in EPICS.

@author: fy65
'''
import __main__  # @UnresolvedImport

#import correct fast energy scan controller based on which ID source is used.
if str(__main__.smode.getPosition())=='idd':
    from i06shared.scan.idd_fast_energy_scan import zacscan, fesController  # @UnusedImport
elif str(__main__.smode.getPosition())=='idu':
    from i06shared.scan.idu_fast_energy_scan import zacscan, fesController  # @Reimport

#define ROIs
roi1=[0,0,100,100]
roi2=[200,300,500,865]
roi3=[650,378,350,468]
roi4=[1000,1000,150,200]

fesController.setupAreaDetectorROIs([roi1, roi2, roi3, roi4])
#run zacscan
zacscan(600, 700, 180, 0.5)

