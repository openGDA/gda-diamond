import mock

import unittest
from diffractometer.scannable.EulerKappa import EulerKappa
from gda.device.scannable.scannablegroup import ScannableMotionWithScannableFieldsBase

class EulerAngles():
	def __init__(self):
		self.Theta = 12
		self.Phi = 10
		self.Chi = 11
		
class KappaAngles():
	def __init__(self):
		self.KTheta = 2
		self.K = 1
		self.KPhi = 0

class TestEulerKappa(unittest.TestCase):
	
	def setUp(self):	
		self.kappa = mock.Mock() # [kphi, kap, kth, kmu, kdelta, kgam]
		self.ekcm = mock.Mock()
		self.euler = EulerKappa('euler', self.kappa, False)
		self.euler.ekcm = self.ekcm
		
		self.kappa.getPosition.return_value = (0, 1, 2, 3, 4, 5) # [kphi, kap, kth, kmu, kdelta, kgam]
				
		self.ekcm.getEulerianAngles.return_value = EulerAngles()
		self.ekcm.getKPossibleAngles.return_value = KappaAngles()
		
	def testInputNames(self):
		self.assertEquals([str(u) for u in self.euler.inputNames],
						   ['phi','chi','eta', 'mu', 'delta', 'gam'])

	def testRawGetPosition(self):
		self.assertEqual(self.euler.getPosition(), (10, 11, 12, 3, 4, 5))
		self.ekcm.getEulerianAngles.assert_called_with((2, 1, 0)) #getEulerianAngles
		
	def testEulerToKappa(self):
		# eta, chi, phi --> kth, kappa, kphi
		self.assertEqual(self.euler.eulerToKappa(12, 11, 10) , (2, 1, 0))
		self.ekcm.getKPossibleAngles.assert_called_with((12, 11, 10))

	def testRawAsynchMoveToAllAxes(self):
		self.euler.rawAsynchronousMoveTo((10, 11, 12, 3, None, 5))
		self.ekcm.getKPossibleAngles.assert_called_with((12, 11, 10))
		self.kappa.asynchronousMoveTo.assert_called_with((0, 1, 2, 3, None, 5))
		
	def testRawAsynchMoveToNonKappaOnly(self):
		self.euler.rawAsynchronousMoveTo((None, None, None, 3, None, 5))
		self.ekcm.getKPossibleAngles.called = False
		self.kappa.asynchronousMoveTo.assert_called_with((None, None, None, 3, None, 5))
		
	def testRawAsynchMoveToMissingChi(self):
		self.euler.rawAsynchronousMoveTo((10, None, 12, 3, None, 5))
		self.ekcm.getKPossibleAngles.assert_called_with((12, 11, 10)) # current kappa
		self.kappa.asynchronousMoveTo.assert_called_with((0, 1, 2, 3, None, 5))
		
	def testRawAsynchMoveToChiOnly(self):
		self.euler.rawAsynchronousMoveTo((None, 11.2, None, None, None, None))
		self.ekcm.getEulerianAngles.assert_called_with((2, 1, 0)) # current position
		self.ekcm.getKPossibleAngles.assert_called_with((12, 11.2, 10))
		self.kappa.asynchronousMoveTo.assert_called_with((0, 1, 2, None, None, None))
		
	def testRawAsynchMoveToChiOnlyInDriftingScan(self):
		self.kappa.getPosition.return_value = (0.3, 1.3, 2.3, 3, 4, 5) # [kphi, kap, kth, kmu, kdelta, kgam]
		self.euler.atScanStart()
		self.kappa.getPosition.return_value = (0, 1, 2, 3, 4, 5) # [kphi, kap, kth, kmu, kdelta, kgam]
		self.euler.rawAsynchronousMoveTo((None, 11.2, None, None, None, None))
		self.ekcm.getEulerianAngles.assert_called_with((2.3, 1.3, 0.3)) # original position
		self.ekcm.getKPossibleAngles.assert_called_with((12, 11.2, 10))
		self.kappa.asynchronousMoveTo.assert_called_with((0, 1, 2, None, None, None))
		
	def testSetGetUpperGdaLimits(self):
		self.euler.setUpperGdaLimits((0, 1, 2, 3, 4, 5))
		self.kappa.kmu.setUpperGdaLimits.assert_called_with(3)
		self.kappa.kdelta.setUpperGdaLimits.assert_called_with(4)
		self.kappa.kgam.setUpperGdaLimits.assert_called_with(5)
		# implementation test only:
		self.assertEqual(
						 tuple(ScannableMotionWithScannableFieldsBase.getUpperGdaLimits(self.euler)),
		 				(0.0, 1.0, 2.0, None, None, None))
		self.kappa.kmu.getUpperGdaLimits.return_value = (3,)
		self.kappa.kdelta.getUpperGdaLimits.return_value = (4,)
		self.kappa.kgam.getUpperGdaLimits.return_value = (5,)
		
		self.assertEqual(self.euler.getUpperGdaLimits(),
						  (0, 1, 2, 3, 4, 5))
		
	def testSetGetUpperGdaLimitsWithNone(self):
		self.euler.setUpperGdaLimits(None)
		self.kappa.kmu.setUpperGdaLimits.assert_called_with(None)
		self.kappa.kdelta.setUpperGdaLimits.assert_called_with(None)
		self.kappa.kgam.setUpperGdaLimits.assert_called_with(None)
		# implementation test only:
		self.assertEqual(
						ScannableMotionWithScannableFieldsBase.getUpperGdaLimits(self.euler),
		 				None)
		self.kappa.kmu.getUpperGdaLimits.return_value = None
		self.kappa.kdelta.getUpperGdaLimits.return_value = None
		self.kappa.kgam.getUpperGdaLimits.return_value = None
		
		self.assertEqual(self.euler.getUpperGdaLimits(), None)

	def testSetGetLowerGdaLimitsWithNone(self):
		self.euler.setLowerGdaLimits(None)
		self.kappa.kmu.setLowerGdaLimits.assert_called_with(None)
		self.kappa.kdelta.setLowerGdaLimits.assert_called_with(None)
		self.kappa.kgam.setLowerGdaLimits.assert_called_with(None)
		# implementation test only:
		self.assertEqual(
						 ScannableMotionWithScannableFieldsBase.getLowerGdaLimits(self.euler),
		 				 None)
		self.kappa.kmu.getLowerGdaLimits.return_value = None
		self.kappa.kdelta.getLowerGdaLimits.return_value = None
		self.kappa.kgam.getLowerGdaLimits.return_value = None
		self.assertEqual(self.euler.getLowerGdaLimits(), None)
		
	def testSetGetLowerGdaLimits(self):
		self.euler.setLowerGdaLimits((0, 1, 2, 3, 4, 5))
		self.kappa.kmu.setLowerGdaLimits.assert_called_with(3)
		self.kappa.kdelta.setLowerGdaLimits.assert_called_with(4)
		self.kappa.kgam.setLowerGdaLimits.assert_called_with(5)
		# implementation test only:
		self.assertEqual(
						 tuple(ScannableMotionWithScannableFieldsBase.getLowerGdaLimits(self.euler)),
		 				(0.0, 1.0, 2.0, None, None, None))
		self.kappa.kmu.getLowerGdaLimits.return_value = (3,)
		self.kappa.kdelta.getLowerGdaLimits.return_value = (4,)
		self.kappa.kgam.getLowerGdaLimits.return_value = (5,)
		
		self.assertEqual(self.euler.getLowerGdaLimits(),
						  (0, 1, 2, 3, 4, 5))
		
	def testSetGetContinuousMoveController(self):
		controller = mock.Mock()
		self.kappa.getContinuousMoveController.return_value = controller
		self.assertEqual(self.euler.getContinuousMoveController(), controller)
		self.euler.setContinuousMoveController(controller)
		self.kappa.setContinuousMoveController.assert_called_with(controller)
		
	def testSetOperatingContinuously(self):
		self.euler.setOperatingContinuously(True)
		self.kappa.setOperatingContinuously.assert_Called_with(True)
		self.euler.setOperatingContinuously(False)
		self.kappa.setOperatingContinuously.assert_Called_with(False)

	def testIsOperatingContinuously(self):
		self.kappa.isOperatingContinously.return_value = True # spelling error in interface!
		self.assertEqual(True, self.euler.isOperatingContinously())
		self.kappa.isOperatingContinously.return_value = False
		self.assertEqual(False, self.euler.isOperatingContinously())
		
	def testAsynchMoveToWhenOperatingContinuously(self):
		self.euler.setOperatingContinuously(True)
		self.euler.asynchronousMoveTo([0,1,2,3,4,5]) # math easy!
		self.kappa.asynchronousMoveTo.assert_called_with((0,1,2,3,4,5))
		
	def testStop(self):
		self.euler.stop()
		self.kappa.stop.assert_called_with()


def diff_ordered(kphi, kap, kth, kmu, kdelta, kgam):
	return kmu, kdelta, kgam, kth, kap, kphi
	
class TestEulerKappaDiffcalcOrdering(unittest.TestCase):
	
	def setUp(self):	
		self.kappa = mock.Mock() # [kphi, kap, kth, kmu, kdelta, kgam] --> [kmu, kdelta, kgam, kth, kap, kphi]
		self.ekcm = mock.Mock()
		self.euler = EulerKappa('euler', self.kappa, True)
		self.euler.ekcm = self.ekcm
		
		self.kappa.getPosition.return_value = diff_ordered(0, 1, 2, 3, 4, 5) # [kphi, kap, kth, kmu, kdelta, kgam]
				
		self.ekcm.getEulerianAngles.return_value = EulerAngles()
		self.ekcm.getKPossibleAngles.return_value = KappaAngles()
		
	def testInputNames(self):
		self.assertEquals([str(u) for u in self.euler.inputNames],
						   ['mu','delta','gam', 'eta', 'chi', 'phi'])

	def testRawGetPosition(self):
		self.assertEqual(self.euler.getPosition(), diff_ordered(10, 11, 12, 3, 4, 5))
		self.ekcm.getEulerianAngles.assert_called_with((2, 1, 0)) #getEulerianAngles
		
	def testEulerToKappa(self):
		# eta, chi, phi --> kth, kappa, kphi
		self.assertEqual(self.euler.eulerToKappa(12, 11, 10) , (2, 1, 0))
		self.ekcm.getKPossibleAngles.assert_called_with((12, 11, 10))

	def testRawAsynchMoveToAllAxes(self):
		self.euler.rawAsynchronousMoveTo(diff_ordered(10, 11, 12, 3, None, 5))
		self.ekcm.getKPossibleAngles.assert_called_with((12, 11, 10))
		self.kappa.asynchronousMoveTo.assert_called_with(diff_ordered(0, 1, 2, 3, None, 5))
		
	def testRawAsynchMoveToNonKappaOnly(self):
		self.euler.rawAsynchronousMoveTo(diff_ordered(None, None, None, 3, None, 5))
		self.ekcm.getKPossibleAngles.called = False
		self.kappa.asynchronousMoveTo.assert_called_with(diff_ordered(None, None, None, 3, None, 5))
		
	def testRawAsynchMoveToMissingChi(self):
		self.euler.rawAsynchronousMoveTo(diff_ordered(10, None, 12, 3, None, 5))
		self.ekcm.getKPossibleAngles.assert_called_with((12, 11, 10)) # current kappa
		self.kappa.asynchronousMoveTo.assert_called_with(diff_ordered(0, 1, 2, 3, None, 5))
		
	def testRawAsynchMoveToChiOnly(self):
		self.euler.rawAsynchronousMoveTo(diff_ordered(None, 11.2, None, None, None, None))
		self.ekcm.getEulerianAngles.assert_called_with((2, 1, 0)) # current position
		self.ekcm.getKPossibleAngles.assert_called_with((12, 11.2, 10))
		self.kappa.asynchronousMoveTo.assert_called_with(diff_ordered(0, 1, 2, None, None, None))
		
	def testRawAsynchMoveToChiOnlyInDriftingScan(self):
		self.kappa.getPosition.return_value = diff_ordered(0.3, 1.3, 2.3, 3, 4, 5) # [kphi, kap, kth, kmu, kdelta, kgam]
		self.euler.atScanStart()
		self.kappa.getPosition.return_value = diff_ordered(0, 1, 2, 3, 4, 5) # [kphi, kap, kth, kmu, kdelta, kgam]
		self.euler.rawAsynchronousMoveTo(diff_ordered(None, 11.2, None, None, None, None))
		self.ekcm.getEulerianAngles.assert_called_with((2.3, 1.3, 0.3)) # original position
		self.ekcm.getKPossibleAngles.assert_called_with((12, 11.2, 10))
		self.kappa.asynchronousMoveTo.assert_called_with(diff_ordered(0, 1, 2, None, None, None))
		
	def testSetGetUpperGdaLimits(self):
		self.euler.setUpperGdaLimits(diff_ordered(0, 1, 2, 3, 4, 5))
		self.kappa.kmuDC.setUpperGdaLimits.assert_called_with(3)
		self.kappa.kdeltaDC.setUpperGdaLimits.assert_called_with(4)
		self.kappa.kgamDC.setUpperGdaLimits.assert_called_with(5)
		# implementation test only:
		self.assertEqual(
						 tuple(ScannableMotionWithScannableFieldsBase.getUpperGdaLimits(self.euler)),
		 				diff_ordered(0.0, 1.0, 2.0, None, None, None))
		self.kappa.kmuDC.getUpperGdaLimits.return_value = (3,)
		self.kappa.kdeltaDC.getUpperGdaLimits.return_value = (4,)
		self.kappa.kgamDC.getUpperGdaLimits.return_value = (5,)
		
		self.assertEqual(self.euler.getUpperGdaLimits(),
						  diff_ordered(0, 1, 2, 3, 4, 5))
		
	def testSetGetUpperGdaLimitsWithNone(self):
		self.euler.setUpperGdaLimits(None)
		self.kappa.kmuDC.setUpperGdaLimits.assert_called_with(None)
		self.kappa.kdeltaDC.setUpperGdaLimits.assert_called_with(None)
		self.kappa.kgamDC.setUpperGdaLimits.assert_called_with(None)
		# implementation test only:
		self.assertEqual(
						ScannableMotionWithScannableFieldsBase.getUpperGdaLimits(self.euler),
		 				None)
		self.kappa.kmuDC.getUpperGdaLimits.return_value = None
		self.kappa.kdeltaDC.getUpperGdaLimits.return_value = None
		self.kappa.kgamDC.getUpperGdaLimits.return_value = None
		
		self.assertEqual(self.euler.getUpperGdaLimits(), None)

	def testSetGetLowerGdaLimitsWithNone(self):
		self.euler.setLowerGdaLimits(None)
		self.kappa.kmuDC.setLowerGdaLimits.assert_called_with(None)
		self.kappa.kdeltaDC.setLowerGdaLimits.assert_called_with(None)
		self.kappa.kgamDC.setLowerGdaLimits.assert_called_with(None)
		# implementation test only:
		self.assertEqual(
						 ScannableMotionWithScannableFieldsBase.getLowerGdaLimits(self.euler),
		 				 None)
		self.kappa.kmuDC.getLowerGdaLimits.return_value = None
		self.kappa.kdeltaDC.getLowerGdaLimits.return_value = None
		self.kappa.kgamDC.getLowerGdaLimits.return_value = None
		self.assertEqual(self.euler.getLowerGdaLimits(), None)
		
	def testSetGetLowerGdaLimits(self):
		self.euler.setLowerGdaLimits(diff_ordered(0, 1, 2, 3, 4, 5))
		self.kappa.kmuDC.setLowerGdaLimits.assert_called_with(3)
		self.kappa.kdeltaDC.setLowerGdaLimits.assert_called_with(4)
		self.kappa.kgamDC.setLowerGdaLimits.assert_called_with(5)
		# implementation test only:
		self.assertEqual(
						 tuple(ScannableMotionWithScannableFieldsBase.getLowerGdaLimits(self.euler)),
		 				diff_ordered(0.0, 1.0, 2.0, None, None, None))
		self.kappa.kmuDC.getLowerGdaLimits.return_value = (3,)
		self.kappa.kdeltaDC.getLowerGdaLimits.return_value = (4,)
		self.kappa.kgamDC.getLowerGdaLimits.return_value = (5,)
		self.assertEqual(self.euler.getLowerGdaLimits(),
						  diff_ordered(0, 1, 2, 3, 4, 5))
		
	def testSetGetContinuousMoveController(self):
		controller = mock.Mock()
		self.kappa.getContinuousMoveController.return_value = controller
		self.assertEqual(self.euler.getContinuousMoveController(), controller)
		self.euler.setContinuousMoveController(controller)
		self.kappa.setContinuousMoveController.assert_called_with(controller)
		
	def testSetOperatingContinuously(self):
		self.euler.setOperatingContinuously(True)
		self.kappa.setOperatingContinuously.assert_Called_with(True)
		self.euler.setOperatingContinuously(False)
		self.kappa.setOperatingContinuously.assert_Called_with(False)

	def testIsOperatingContinuously(self):
		self.kappa.isOperatingContinously.return_value = True # spelling error in interface!
		self.assertEqual(True, self.euler.isOperatingContinously())
		self.kappa.isOperatingContinously.return_value = False
		self.assertEqual(False, self.euler.isOperatingContinously())
		
	def testAsynchMoveToWhenOperatingContinuously(self):
		self.euler.setOperatingContinuously(True)
		self.euler.asynchronousMoveTo(diff_ordered(0,1,2,3,4,5)) # math easy!
		self.kappa.asynchronousMoveTo.assert_called_with(diff_ordered(0,1,2,3,4,5))
		
	def testStop(self):
		self.euler.stop()
		self.kappa.stop.assert_called_with()

