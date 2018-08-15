'''
Created on 5 Jul 2011

@author: Mark Basham
'''

# You will need plot 1 and 2 open to use this properly, the fits
# will be displayed in plot 2 and the initial image of all the data
# and then the voltage Vs FWHM will appear in Plot 1

import scisoftpy as dnp
import scisoftpy.fit.function as dff
import scisoftpy.fit as dnf
from time import sleep

# hardcoded location to load in the file from
#data = dnp.io.load('/dls/i22/data/2012/cm5716-3/i22-79397.nxs')# vertical focusing on sample table
#data = dnp.io.load('/dls/i22/data/2012/cm5716-3/i22-79403.nxs')# vertical focusing at 9.2m
#data = dnp.io.load('/dls/i22/data/2012/cm5716-3/i22-79407.nxs')# horizontal focusing at 9.2m (1st data before voltages trip)
#data = dnp.io.load('/dls/i22/data/2012/cm5716-3/i22-79408.nxs')# horizontal focusing at 9.2m (2nt data after voltages trip)
data = dnp.io.load('/dls/i22/data/2012/cm5716-3/i22-79455.nxs')

diode = data['/entry1/default/d10d1'][:]
scanvalue = data['/entry1/default/sdx'][:]#*1.8 # Magic scaling value here
voltage = data['/entry1/default/allHfm'][:]

dnp.plot.image(diode)
sleep(5)

voltages = []
fwhm = []

for i in range(diode.shape[0]) :
	x = scanvalue[i,:]
	y = diode[i,:]
	fr = dnf.fit([dff.gaussian],x, dnp.diff(y),[x.mean(),0.1,0.1],[(x.min(),x.max()),(0.,x.peakToPeak()),(0,x.peakToPeak()*y.peakToPeak())], optimizer='global' )
	fr.plot('Plot 2')
	voltages.append(voltage[i,0])
	fwhm.append(fr[1])
	
	v = dnp.asDataset(voltages)
	f = dnp.asDataset(fwhm)
	v.setName("Bimorph Voltages")
	f.setName("beam FWHM")
	dnp.plot.line(v, f)
	sleep(1)

#fr = dnp.fit.fit([myfunc], v, f, [-55,3,-1,1])
#print fr
#fr.plot()
#print "Min at: " + str(fr[0])+"/"+str(fr[1])

# get all the results, then fit a polynomial
v = dnp.asDataset(voltages)
f = dnp.asDataset(fwhm)

p = dnf.polyfit(v, f, 2, rcond=None, full=True)
print p

p[1].plot()

min = (-p[0][1]/(2.0*p[0][0]))
print min

n = len(fwhm)
for i in range(n) :
	print str(voltages[i])+" "+str(fwhm[i])

