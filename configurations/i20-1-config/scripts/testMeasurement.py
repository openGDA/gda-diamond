#
# Deprecated. Now use singlescan.py.
#
#



from gda.data import PathConstructor, NumTracker

from uk.ac.diamond.scisoft.analysis.dataset import DoubleDataset, IntegerDataset
from uk.ac.diamond.scisoft.analysis import SDAPlotter;

import collectData
from jarray import zeros
import math

def _doDKCorrection(data, dk_data):
    if len(data) != len(dk_data):
        raise "Arrays uneven length! Cannot perform correction"
    
    corrected = zeros(len(data),java.lang.Double)
    for i in range(len(data)):
        corrected[i] = data[i] - dk_data[i]
    return corrected

def _calcLnI0It(i0,it):
    if len(i0) != len(it):
        raise "Arrays uneven length! Cannot perform correction"
    
    lni0it = zeros(len(i0),java.lang.Double)
    for i in range(len(i0)):
        if it[i] == 0.0 or it[i] < 0.0 or i0[i] == 0.0 or i0[i] < 0.0:
            lni0it[i] = 0.0
        else:
            lni0it[i] = math.log(float(i0[i])/float(it[i]))
    return lni0it
   

#########################################
#
# Variables to be set to run this script
#
#########################################

# define i0 positions
i0_samx = 0.0
i0_samy = 0.0
i0_samz = 0.0

# define it positions
it_samx = 0.0
it_samy = 0.0
it_samz = 0.0

# define I0 integration time
i0_scan_time = 0.1
i0_num_scans = 1

# define It integration time
it_scan_time = 0.005
it_num_scans = 1

################
# collect darks
################
print "Collecting darks..."
#   close shutter
###shutter2('Close')
print "Shutter closed"
#print "Moving to I0 positions..."
#pos samplex i0_samx sampley i0_samy samplez i0_samz
print "Collect I0 dark"
i0_dk = collectData.doMultipleCollections(i0_num_scans,i0_scan_time)
#   plot
ds_i0dk = IntegerDataset(i0_dk, [len(i0_dk)]);
ds_i0dk.setName("I0 dark")
SDAPlotter.plot("Plot 1",ds_i0dk)
    
#print "Moving to It positions..."
#pos samplex it_samx sampley it_samy samplez it_samz
print "Collect It dark"
it_dk = collectData.doMultipleCollections(it_num_scans,it_scan_time)
#   plot
ds_itdk = IntegerDataset(it_dk, [len(it_dk)]);
ds_itdk.setName("It dark")
SDAPlotter.plot("Plot 1",None, [ds_i0dk,ds_itdk])
    
###################
# collect with beam
###################
print "Collecting with-beam measurements"
#   open shutter
####shutter2('Open')
print "Shutter open"
print "Moving to I0 positions..."
###pos samplex i0_samx sampley i0_samy samplez i0_samz
print "Collect I0"
i0 = collectData.doMultipleCollections(i0_num_scans,i0_scan_time)
#   correct for dk
i0_corrected = _doDKCorrection(i0,i0_dk)
#   plot
ds_i0 = IntegerDataset(i0, [len(i0)]);
ds_i0.setName("I0 uncorrected")
ds_i0_corr = DoubleDataset(i0_corrected, [len(i0_corrected)]);
ds_i0_corr.setName("I0 corrected")
SDAPlotter.plot("Plot 1",None, [ds_i0dk,ds_itdk,ds_i0,ds_i0_corr])

print "Moving to It positions..."
###pos samplex it_samx sampley it_samy samplez it_samz
print "Collect It"
it = collectData.doMultipleCollections(it_num_scans,it_scan_time)
#   correct for dk
it_corrected = _doDKCorrection(it,it_dk)
#   plot
ds_it = IntegerDataset(it, [len(it)]);
ds_it.setName("It uncorrected")
ds_it_corr = DoubleDataset(it_corrected, [len(it_corrected)]);
ds_it_corr.setName("It corrected")
SDAPlotter.plot("Plot 1",None, [ds_i0dk,ds_itdk,ds_i0,ds_i0_corr,ds_it,ds_it_corr])

print "Calculating ln(I0\It)..."
lni0it = _calcLnI0It(i0_corrected,it_corrected)
ds_lni0it = DoubleDataset(lni0it, [len(lni0it)]);
ds_lni0it.setName("Ln(I0\It) corrected")
#   plot
SDAPlotter.plot("Plot 1",None, [ds_i0dk,ds_itdk,ds_i0,ds_i0_corr,ds_it,ds_it_corr,ds_lni0it])
    
###############
# write to file
###############
print "Writing data sets to file..."

# create strip number header
stripNames = zeros(len(i0),java.lang.String)
for i in range(len(i0)):
    stripNames[i] = str(i)

# determine a good file name
dataDir = PathConstructor.createFromDefaultProperty();
runNumber = NumTracker("i20-1");
scanNumber = runNumber.incrementNumber();
filename = dataDir + str(scanNumber) + ".dat"
print "Writing data to",filename
# open file and write above into it.
file = open(filename,'w')
#file.write(_arrayToTabString(stripNames))
#file.write(_arrayToTabString(i0_corrected))
#file.write(_arrayToTabString(it_corrected))
#file.write(_arrayToTabString(lni0it))
#file.write(_arrayToTabString(energy))
#file.write(_arrayToTabString(i0_dk))
#file.write(_arrayToTabString(it_dk))
#file.write(_arrayToTabString(i0))
#file.write(_arrayToTabString(it))

file.write("Strip #\tI0_corr\tIt_corr\tLn(I0/It)\tI0_dark\tIt_dark\tI0_raw\tIt_raw\n")
for i in range(len(i0)):
    stringToWrite = stripNames[i]+"\t"
    stringToWrite += '%(value).2f' % {'value' : i0_corrected[i]} +"\t"
    stringToWrite += '%(value).2f' % {'value' : it_corrected[i]}+"\t"
    stringToWrite += '%(value).5f' % {'value' : lni0it[i]}+"\t"
#    stringToWrite += energy[i]+"\t"
    stringToWrite += '%(value)d' % {'value' : i0_dk[i]}+"\t"
    stringToWrite += '%(value)d' % {'value' : it_dk[i]}+"\t"
    stringToWrite += '%(value)d' % {'value' : i0[i]}+"\t"
    stringToWrite += '%(value)d' % {'value' : it[i]}+"\n"
    file.write(stringToWrite)

file.close()
    
print "Done."