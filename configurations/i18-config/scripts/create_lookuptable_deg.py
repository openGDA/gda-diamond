from gda.analysis.numerical.optimization.objectivefunction import AbstractObjectiveFunction
from gda.analysis.numerical.linefunction import AbstractCompositeFunction
from gda.analysis.numerical.linefunction import CompositeFunction
from gda.analysis.numerical.linefunction import Gaussian1D
from gda.analysis.numerical.linefunction import BGAsymmetricGaussian1D
from gda.analysis.numerical.linefunction import BGGaussian1D
from gda.analysis.numerical.linefunction import AsymmetricGaussian1D
from gda.analysis.numerical.linefunction import Polynomial
from gda.analysis.numerical.linefunction import Parameter
from gda.analysis.numerical.differentiation import Differentiate
from gda.analysis.numerical.optimization.objectivefunction import chisquared
from gda.analysis.numerical.optimization.optimizers.leastsquares import minpackOptimizer
from gda.analysis.numerical.optimization.optimizers.simplex import NelderMeadOptimizer
from gda.analysis.datastructure import DataVector
from time import sleep
#
# A simple method for performing the gap scan
#
def scangap(start_gap,stop_gap,step_gap):
	npoints=int((stop_gap-start_gap)/step_gap)
	currentgap=start_gap
	xdata = DataVector([npoints])
	ydata = DataVector([npoints])
	for i in range(npoints):
		pos sc_idgap currentgap
		xdata[i] = currentgap
		ydata[i] = d7bdiode.getPosition()
		#ydata[i] = multict.getPosition()[0]
		print 'i gap',i,('%.3f' %xdata[i]),('%.5f' %ydata[i])
		#print 'i gap',i,('%.3f' %currentgap),('%.3f' %multict.getPosition()[0])
		currentgap=currentgap+step_gap
	return xdata, ydata
	
#
#
# Fit the data from the gap scan with a gaussian and return
# the peak position
#
#	
def fitdata(xdata,ydata):
	# Find the min and max of the data set
	maxcount=0
	mincount=0
	maxval=ydata[0]
	minval= 10000000000000.0
	ysize=len(ydata)
	for i in range(ysize):	
		if(ydata[i]>maxval):
			maxval=ydata[i]
			maxcount=i
		if(ydata[i]<minval):
			minval=ydata[i]
			mincount=i
	for i in range(ysize):
		ydata[i]=ydata[i]-minval
	for i in range(ysize):	
		ydata[i]=ydata[i]/maxval
		
	gauss = BGGaussian1D([ydata[maxcount]/100.0,xdata[maxcount],0.005,minval])
	#gauss=BGAsymmetricGaussian1D([ydata[maxcount]/100.0,xdata[maxcount],0.005,0.005,minval])
	gauss.getParameter("area").setLowerLimit(1.0E-5)
	gauss.getParameter("area").setUpperLimit(0.1)     
	gauss.getParameter("position").setLowerLimit(xdata[0])
	gauss.getParameter("position").setUpperLimit(xdata[ysize-1])
	gauss.getParameter("sigma").setLowerLimit(0.0005)
	gauss.getParameter("sigma").setUpperLimit(0.05)

	#gauss.getParameter("sigma1").setLowerLimit(0.0005)
	#gauss.getParameter("sigma1").setUpperLimit(0.05)
	#gauss.getParameter("sigma2").setLowerLimit(0.0005)
	#gauss.getParameter("sigma2").setUpperLimit(0.05)
	gauss.getParameter("background").setLowerLimit(1.0E-12)
	gauss.getParameter("background").setUpperLimit(0.1)
	myfunction = CompositeFunction()
	myfunction.addFunction("Gaussian", gauss)
	chifunc = chisquared(myfunction,[xdata,ydata])
	minpack = minpackOptimizer(chifunc)
	minpack.setMaxNoOfEvaluations(150000)
	minpack.reset()
	minpack.optimize()
	bestValues=minpack.getBest()	
	print 'maxcount',xdata[maxcount]
	print 'best values',bestValues,minpack.getMinimum()
	return bestValues,xdata[maxcount]

#
# Script to regenerate a lookup table for a given harmonic
#
angleStart=16.7
angleStop=14.300
angleStep=-0.200
gaprange=0.040
gapstep=0.003
offset=0



#
# The code uses comboDCM, i.e. the current lookup table to get a starting point for the scans
#
converter = finder.find("auto_mDeg_idGap_mm_converter")

converter.enableAutoConversion()

pos sc_comboDCM_d angleStart
#pos comboDCM_eV 7200

#converter = finder.find("auto_mDeg_idGap_mm_converter")

converter.disableAutoConversion()

lookup = finder.find("lookup_name_provider")
print 'Harmonic set to ',lookup.getConverterName()

#
# Selection mode 
# 0 fit the curve with a gaussian and pick the centre
# 1 use the peak position
selectionMode=1

new_harmonic_file='/dls/science/groups/i18/lookuptables/Fe_Jul19b.txt'
#new_harmonic_file='/dls/i18/data/2017/sp15308-1/processing/Fe-Jan17.txt'
#new_harmonic_file='/dls/i18/data/2014/cm4970-4/U_l3-Oct14.txt'
#new_harmonic_file='/dls/i18/data/2018/cm19669-3/P_Jun18.txt'

fod=open(new_harmonic_file,"w")
print >>fod,"Bragg\tGap"
#
# Will update
#
#pos comboDCM angleStart
#current_gap=idgap.getPosition()
for i in range(angleStart,angleStop,angleStep):
	# Move to position
	pos sc_comboDCM_d i
	sleep(6)
	current_gap=sc_idgap.getPosition()+offset
	# Scan gap
	myxdata,myydata=scangap(current_gap-gaprange,current_gap+gaprange,gapstep)
	result,bestx=fitdata(myxdata,myydata)
	# Write to new file
	if(selectionMode==0):
		myline="%d\t%.5f" %(i,result[1])
	else:
		myline="%d\t%.5f" %(i,bestx)
	print >>fod,myline
	#print >>fod,i,"\t",result[1]
fod.close()

converter.enableAutoConversion()
print 'Done'







