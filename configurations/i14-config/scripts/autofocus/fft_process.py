import logging
import numpy as np

from adPythonPlugin import AdPythonPlugin


class FftProcess(AdPythonPlugin):
	"""
	Version for I14 autofocus

	Estimate focus quality via Discrete 2D Fourier Transform.
	An image in focus will have more "high" frequencies than one (low resolution data).

	The bottom 5% along each axis are regarded as "low" frequencies and are discounted,
	so we return the average of the magnitudes of the higher 95%.

	https://stackoverflow.com/a/7767755

	Parameter usage:
		int1 (input): number of strips to divide the array into
		int2 (output): FFT value for the first strip (pending a way to return all values)

	"""

	def __init__(self):
		self.log.setLevel(logging.DEBUG)
		params = dict(int1 = 1,      int1Name = "Strips",
                      int2 = 2,      int2Name = "Output",
                      double1 = 1.0, double1Name = "-1",
                      double2 = 2.0, double2Name = "-1")
		AdPythonPlugin.__init__(self, params)

	def paramChanged(self):
		pass

	# Compute the mean FFT value for each strip in the input array
	# NB The last index of the array is the fastest-changing i.e. the x axis
	def processArray(self, arr, attr={}):
		num_strips = self["int1"]
		self.log.debug("Apply FFT2 to data array %s in %s strip(s)" % (str(arr.shape), num_strips))

		strips = np.hsplit(arr, num_strips)
		output = np.zeros(num_strips, dtype=np.int32)

		for i in range(0, num_strips):
			output[i] = int(self.computeMean(strips[i]))

		self.log.debug("Output: %s" % output)

		# Pending a parameter that can handle multiple values being added to the AD template, return the first element of output
		self["int2"] = int(output[0])

		# Return the original array in case another plugin wants to read it.
		return arr

	# Perform an FFT on the input array and return the mean value
	def computeMean(self, strip):
		#self.log.debug("Apply FFT2 to strip of shape %s" % (str(strip.shape)))
		data_fft = np.fft.rfft2(strip)
		fft_abs = np.abs(data_fft).copy()
		h, w = fft_abs.shape

		return np.mean(fft_abs[
			int(0.05 * h) : int(0.95 * h)-1,
			int(0.05 * w) : -1])
