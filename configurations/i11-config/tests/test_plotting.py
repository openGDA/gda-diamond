from gda.org.myls.scannable import ScannableClassGenerator, Gaussian
import pytest

@pytest.mark.plotting
@pytest.mark.parametrize("noise", [.1, .2, .3, .4, .5])
def test_scan(main, noise):
	scannableGaussian = ScannableClassGenerator.generateScannableGaussian(
		Gaussian(0, 1, 1, noise)) # centre, width, height, noise
	
	main.scan(scannableGaussian, -1, 1, .1)
