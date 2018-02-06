# set this to the original processed data files
from localStation import mythen_data_converter
filenames = []
for run_num in range(73724, 73734):
    for file in range(1, 16):
        filenames.append("/dls/i11/data/2011/ee6285-1/A001_graphite_300K/%d-mythen-%04d.dat" % (run_num, file))
print "%d filename(s) specified" % len(filenames)

# this will contain the new, summed data
new_summed_data_file = "/dls/i11/data/2011/ee6285-1/A001_graphite_300K/rf_test.dat"

# you probably don't need to change these
number_of_modules = 18
step = 0.004

from gda.device.detector.mythen.data import MythenDataFileUtils, MythenSum

all_data = MythenDataFileUtils.readMythenProcessedDataFiles(filenames)
print "loaded data"
summed_data = MythenSum.sum(all_data, number_of_modules, mythen_data_converter.badChannelProvider, step)
print "data summed"
MythenDataFileUtils.saveProcessedDataFile(summed_data, new_summed_data_file)
print "summed data saved to %s" % new_summed_data_file
