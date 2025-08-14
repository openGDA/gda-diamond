from gda.org.myls.scannable import ScannableClassGenerator, Gaussian
import pytest

@pytest.mark.plotting
@pytest.mark.parametrize("noise", [.1, .2, .3, .4, .5])
def test_scan(main, noise):
	scannableGaussian = ScannableClassGenerator.generateScannableGaussian(
		Gaussian(0, 1, 1, noise)) # centre, width, height, noise
	
	main.scan(scannableGaussian, -1, 1, .1)

""" These are failing with:

________________________________ test_scan[0.1] ________________________________

a = (), kw = {'main': <module '__main__' (built-in)>, 'noise': 0.1}

    @wraps(fn)
    def inner(*a, **kw):
        try:
>           fn(*a, **kw)

/dls_sw/p38/software/gda_versions/gda-9-38-default/workspace_git/gda-core.git/uk.ac.gda.core/scripts/beamline_test/__init__.py:86: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/dls_sw/p38/software/gda_versions/gda-9-38-default/workspace_git/gda-core.git/uk.ac.gda.core/scripts/beamline_test/__init__.py:86: in inner
    fn(*a, **kw)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

main = <module '__main__' (built-in)>, noise = 0.1

    @pytest.mark.plotting
    @pytest.mark.parametrize("noise", [.1, .2, .3, .4, .5])
    def test_scan(main, noise):
    	scannableGaussian = ScannableClassGenerator.generateScannableGaussian(
    		Gaussian(0, 1, 1, noise)) # centre, width, height, noise
    
>   	main.scan(scannableGaussian, -1, 1, .1)
E    AttributeError: 'module' object has no attribute 'scan'

/dls_sw/p38/software/gda_versions/gda-9-38-default/workspace_git/gda-diamond.git/configurations/p38-config/tests/test_plotting.py:10: AttributeError

""" 