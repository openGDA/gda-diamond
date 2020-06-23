from uk.ac.diamond.daq.devices.specs.phoibos.api import SpecsPhoibosSequence
from uk.ac.diamond.daq.devices.specs.phoibos.api import SpecsPhoibosRegion
from gdaserver import analyser

def configure_analyser_fixed_transmission(region_name, axis_name, start_energy, end_energy, step_energy, pass_energy, exposure_time, number_iterations):

	region = SpecsPhoibosRegion()
	
	# Hard-coded values
	region.setValues(1)
	region.setSlices(100) 
	region.setAcquisitionMode("Fixed Transmission")
	region.setPsuMode("3.5kV")
	region.setLensMode("SmallArea")
	
	# Parameterised values
	region.setName(region_name)
	region.setStartEnergy(start_energy)
	region.setEndEnergy(end_energy)
	region.setStepEnergy(step_energy)
	region.setPassEnergy(pass_energy)
	region.setIterations(number_iterations)
	region.setExposureTime(exposure_time)

	energy_mode = ''
  	if axis_name =='BE':
  		region.setBindingEnergy(True)
  		energy_mode = 'Binding Energy'
	elif axis_name =='KE':
		region.setBindingEnergy(False)
		energy_mode = 'Kinetic Energy'
	else:
		raise Exception('Could not resolve axis name, please specify either KE or BE')

	# Calculated values
	centre_energy = (start_energy + end_energy) / 2
	region.setCentreEnergy(centre_energy)

	# Create and set sequence
	sequence = SpecsPhoibosSequence()
	sequence.addRegion(region)
	analyser.setSequence(sequence, "")

	# Calculate run-time
	estimated_runtime = number_iterations * (2.4 + (exposure_time + 0.082)*(abs(end_energy-start_energy) + 0.11*pass_energy)/step_energy )

	# Confirmation output
	print('')
	print('GDA has been configured with a region with the following values:')
	print('')
	print('Region name:      {}'.format(region_name))
	print('Acquisition mode: Fixed Transmission')
	print('PSU mode:         3.5kV')
	print('Lens mode:        SmallArea')
	print('Energy mode:      {}'.format(energy_mode))
	print('Start energy:     {}'.format(start_energy))
	print('End energy:       {}'.format(end_energy))
	print('Step energy:      {}'.format(step_energy))
	print('Pass energy:      {}'.format(pass_energy))
	print('Centre energy:    {}'.format(centre_energy))
	print('Iterations:       {}'.format(number_iterations))
	print('Exposure time:    {}'.format(exposure_time))
	print('Values:           {}'.format(1))
	print('Slices:           {}'.format(100))
	print('')
	print('These values will be sent to the analyser via EPICS when the scan is started. The scan can be run with "scan dummy_a 0 0 1 analyser".')
	print('The estimated run-time of this scan is {:.1f} seconds.'.format(estimated_runtime))