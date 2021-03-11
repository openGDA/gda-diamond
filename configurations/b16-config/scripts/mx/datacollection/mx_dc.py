from datacollection.diffraction import *
import time

today = time.strftime("%Y%m%d")

runN = request.metadata._start_run_number

def setup(total_exposure,total_oscillation,prefix=False,folder=False,wavelength=False,osc_per_frame=0.25,run_number=False):
	if folder:
		request.metadata.setDirectory("%s/%s" %(today,folder))
		request.metadata.setDetectorWritePath("%s/%s" %(today,folder))
	else:
		request.metadata.setDirectory(today)
		request.metadata.setDetectorWritePath(today)

	if prefix:
		request.metadata.setPrefix(prefix)
	if run_number:
		request.metadata.setStartRunNumber(run_number)
		runN = run_number
	else:
		runN = int(request.metadata._start_run_number)
		request.metadata.setStartRunNumber(runN+1)

	if wavelength:
		request.run_data.setWavelength(wavelength)

	n_images = int(total_oscillation / osc_per_frame)
	print "Going to try set number of images to %s" %(n_images)
	request.run_data.setNumImages(n_images)
	
	exposure_per_frame = float(total_exposure) / float(n_images)
	print ""
	print "########################################################"
	print "Going to try to set the exposure per frame to %s seconds" %(exposure_per_frame)
	request.run_data.setExposureTime(exposure_per_frame)

	print "Setting oscillation per frame to %s" %(osc_per_frame)
	request.run_data.setStep(osc_per_frame)

	print "Data will be copied to folder"
	print "Path: %s%s/%s" %(DEF_VISIT_FOLDER,request.metadata.directory(),request.metadata.prefix())
	print "Using the run number %s" %(request.metadata._start_run_number)
	print "########################################################"
	print ""
	request.run_data()

 
def collect():
	print request.run_data()
	print request.metadata.directory()
	print request.metadata.prefix()

	diff.run(request)

	print "Data will appear in a few seconds in folder"
	print "Path: %s%s/%s" %(DEF_VISIT_FOLDER,request.metadata.directory(),request.metadata.prefix())
	print "Using the run number %s" %(request.metadata._start_run_number)
