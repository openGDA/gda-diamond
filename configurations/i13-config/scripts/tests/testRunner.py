'''
Created on 12 Apr 2010

@author: tjs15132
'''
from gda.configuration.properties import LocalProperties
import sys
import tests.beamline_tests
import unittest


def suite():
    return unittest.TestSuite(
#                            unittest.TestLoader().loadTestsFromTestCase(tests.simple.Test1),
#                            unittest.TestLoader().loadTestsFromModule(tests.complex),
                            tests.beamline_tests.get_test_scannable_suite(LocalProperties.get("gda.config") + "/scripts/tests/scannables_to_test")
                            )
def run_tests():
    runner = unittest.TextTestRunner(stream=sys.stdout, descriptions=1, verbosity=1)
    runner.run(unittest.TestSuite(suite()))
    print "End of tests"
    