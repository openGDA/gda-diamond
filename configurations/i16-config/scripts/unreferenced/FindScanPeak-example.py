run "FindScanPeak2"
#from FindScanPeak import FindScanPeak
from pprint import pprint
from PDArray import PDArray
from GenPoisson import GenPoisson

# reload(FindScanPeak)

# Make a 1d test data set. This function, as it finds the maximum values will work for data of any dimension
#y = PDArray('y', [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 5.5, 4.4, 3.3],'','%2.2f')
scan y 0 8 1


# Find the peak (and print as ToPrint flag is not set to 0.
peakValues = FindScanPeak2("y",["index","y"])

# peakValues contains a dictionary of the line where the peak occured:
print ''
print 'Returned Dictionary:'
pprint(peakValues)

print "--------"
print "Testing with poisson distributed noise (Lambda=10) with spike of 30 in the middle."
print "Note that the calculated value of Lambda is higher than 10 because of the spike."
print "The normal statistics are not used, but are included for comparison"
a=gen_poisson(10)
ydata=[]
# Make noise
for i in range(1,11):
	ydata.append(a.next())

# Add spike
ydata[7] = 30
yspike = PDArray('y', ydata,'','%2.2f')

scan yspike 0 9 1
peakValues = FindScanPeak2("y",["index","y"], peakRatio=2)
