### LOCAL CONFIGURATION

# mask needs to be called "mask"
# sector needs to be called "Profile 1"
maskandsector="/dls/i22/data/2013/cm5948-5/processing/testmask.nxs"
# 
reductionsetupxml="/home/i22user/Desktop/testdatareduction.xml"

## There is setBackgroundFile("filename") to set the background if required

###
### No more work needed routinely below
###

print "\nSetting Processing Parameters"
deti=finder.find("detectorInfoPath")

deti.setSaxsDetectorInfoPath(maskandsector)
deti.setDataCalibrationReductionSetupPath(reductionsetupxml)

npl=finder.find("ncddetectorsProcessingListener")

if npl.isDisabled():
    print "Automatic Processing was disabled -- ENABLING NOW"
    npl.setDisabled(False)
else:
    print "Automatic Processing was enabled -- DISABLING NOW"
    npl.setDisabled(True)

print "done\n"