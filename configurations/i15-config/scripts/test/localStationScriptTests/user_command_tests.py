import unittest
from mock import Mock

from localStationScripts.user_commands import * # @UnusedWildImport

class UserCommandsTest(unittest.TestCase):

	def setUp(self):
		self.exposeTime=0.1
		self.exposeNumber=1
		self.fileName="fileName"
		self.rockAngle=.1
		self.rockNumber=1
		self.horizStep=.1
		self.horizStepNumber=1
		self.vertStep=.1
		self.vertStepNumber=1
		self.stepSize=.1
		self.stepNumber=1
		self.AbsoluteHorizStart=.1
		self.AbsoluteHorizEnd=.1
		self.AbsoluteVertStart=.1
		self.AbsoluteVertEnd=.1
		self.AbsoluteStartPos=.1
		self.AbsoluteEndPos=.1
		
		self.motorDx=Mock()
		self.motorDx.name = "dx"
		self.motorDx.getPosition.return_value = 10.
		self.motorDz=Mock()
		self.motorDz.name = "dz"
		self.motorDx.getPosition.return_value = 20.
		self.motorDkphi=Mock()
		self.motorDkphi.name = "dkphi"
		self.motorDx.getPosition.return_value = 58.
		self.motorFail=Mock()
		self.motorFail.name = "fail"

	def tearDown(self):
		pass

		"""
	def testexpose(self):
		self.assertEqual(expose_new(self.exposeTime, self.fileName), None)

	def testexposeFail(self):
		self.assertEqual(expose_new(self.fileName, self.exposeTime),
						["exposeTime should be a positive number: 'fileName'", 'fileName should be a string: 0.1'])
"""

	def testexposeN(self):
		self.assertEqual(exposeN(self.exposeTime, self.exposeNumber, self.fileName), None)

	def testexposeNFail(self):
		self.assertEqual(exposeN('Fail', 'Fail', 0),
						["exposeTime should be a positive number: 'Fail'", "exposeNumber should be a positive integer: 'Fail'"])

	def testexposeLineAbs(self):
		self.assertEqual(exposeLineAbs(self.exposeTime, self.motorDx, self.AbsoluteStartPos, self.AbsoluteEndPos, self.stepNumber, self.fileName), None)

	def testexposeLineStep(self):
		self.assertEqual(exposeLineStep(self.exposeTime, self.motorDx, self.stepSize, self.stepNumber, self.fileName), None)

	def testexposeLineStepFail(self):
		self.assertEqual(exposeLineStep('Fail', 'Fail', 'Fail', 'Fail', 0),
						["exposeTime should be a positive number: 'Fail'", "lineMotor invalid, use dx, dy or dz: 'Fail'", "stepSize should be a number: 'Fail'", "stepNumber should be a positive integer: 'Fail'"])

	def testexposeNLineAbs(self):
		self.assertEqual(exposeNLineAbs(self.exposeTime, self.exposeNumber, self.motorDx, self.AbsoluteStartPos, self.AbsoluteEndPos, self.stepNumber, self.fileName), None)

	def testexposeNLineStep(self):
		self.assertEqual(exposeNLineStep(self.exposeTime, self.exposeNumber, self.motorDx, self.stepSize, self.stepNumber, self.fileName), None)

	def testexposeGridAbs(self):
		self.assertEqual(exposeGridAbs(self.exposeTime, self.AbsoluteHorizStart, self.AbsoluteHorizEnd, self.horizStepNumber, self.AbsoluteVertStart, self.AbsoluteVertEnd, self.vertStepNumber, self.fileName), None)

	def testexposeGridStep(self):
		self.assertEqual(exposeGridStep(self.exposeTime, self.horizStep, self.horizStepNumber, self.vertStep, self.vertStepNumber, self.fileName), None)

	def testexposeNGridAbs(self):
		self.assertEqual(exposeNGridAbs(self.exposeTime, self.exposeNumber, self.AbsoluteHorizStart, self.AbsoluteHorizEnd, self.horizStepNumber, self.AbsoluteVertStart, self.AbsoluteVertEnd, self.vertStepNumber, self.fileName), None)

	def testexposeNGridAbsFail(self):
		self.assertEqual(exposeNGridAbs('Fail', 'Fail', 'Fail', 'Fail', 'Fail', 'Fail', 'Fail', 'Fail', 0),
						["exposeTime should be a positive number: 'Fail'", "exposeNumber should be a positive integer: 'Fail'", "horizStepNumber should be a positive integer: 'Fail'", "vertStepNumber should be a positive integer: 'Fail'", "AbsoluteHorizStart should be a number: 'Fail'", "AbsoluteHorizEnd should be a number: 'Fail'", "AbsoluteVertStart should be a number: 'Fail'", "AbsoluteVertEnd should be a number: 'Fail'"])

	def testexposeNGridStep(self):
		self.assertEqual(exposeNGridStep(self.exposeTime, self.exposeNumber, self.horizStep, self.horizStepNumber, self.vertStep, self.vertStepNumber, self.fileName), None)

	def testexposeNGridStepFail(self):
		self.assertEqual(exposeNGridStep('Fail', 'Fail', 'Fail', 'Fail', 'Fail', 'Fail', 0),
						["exposeTime should be a positive number: 'Fail'", "exposeNumber should be a positive integer: 'Fail'", "horizStep should be a number: 'Fail'", "horizStepNumber should be a positive integer: 'Fail'", "vertStep should be a number: 'Fail'", "vertStepNumber should be a positive integer: 'Fail'"])

	def testexposeRock(self):
		self.assertEqual(exposeRock(self.exposeTime, self.rockAngle, self.fileName), None)

	def testexposeRockN(self):
		self.assertEqual(exposeRockN(self.exposeTime, self.rockAngle, self.rockNumber, self.fileName), None)

	def testexposeNRockN(self):
		self.assertEqual(exposeNRockN(self.exposeTime, self.exposeNumber, self.rockAngle, self.rockNumber, self.fileName), None)

	def testexposeNRockNFail(self):
		self.assertEqual(exposeNRockN('Fail', 'Fail', 'Fail', 'Fail', 'Fail'),
						["exposeTime should be a positive number: 'Fail'", "exposeNumber should be a positive integer: 'Fail'", "rockAngle should be a number: 'Fail'", "rockNumber should be a positive integer: 'Fail'"])

	def testexposeRockLineAbs(self):
		self.assertEqual(exposeRockLineAbs(self.exposeTime, self.rockAngle, self.motorDx, self.AbsoluteStartPos, self.AbsoluteEndPos, self.stepNumber, self.fileName), None)

	def testexposeRockLineStep(self):
		self.assertEqual(exposeRockLineStep(self.exposeTime, self.rockAngle, self.motorDx, self.stepSize, self.stepNumber, self.fileName), None)

	def testexposeRockGridAbs(self):
		self.assertEqual(exposeRockGridAbs(self.exposeTime, self.rockAngle, self.AbsoluteHorizStart, self.AbsoluteHorizEnd, self.horizStepNumber, self.AbsoluteVertStart, self.AbsoluteVertEnd, self.vertStepNumber, self.fileName), None)

	def testexposeRockGridStep(self):
		self.assertEqual(exposeRockGridStep(self.exposeTime, self.rockAngle, self.horizStep, self.horizStepNumber, self.vertStep, self.vertStepNumber, self.fileName), None)

	def testexposeNRockLineAbs(self):
		self.assertEqual(exposeNRockLineAbs(self.exposeTime, self.exposeNumber, self.rockAngle, self.motorDx, self.AbsoluteStartPos, self.AbsoluteEndPos, self.stepNumber, self.fileName), None)

	def testexposeNRockLineStep(self):
		self.assertEqual(exposeNRockLineStep(self.exposeTime, self.exposeNumber, self.rockAngle, self.motorDx, self.stepSize, self.stepNumber, self.fileName), None)

	def testexposeNRockGridAbs(self):
		self.assertEqual(exposeNRockGridAbs(self.exposeTime, self.exposeNumber, self.rockAngle, self.AbsoluteHorizStart, self.AbsoluteHorizEnd, self.horizStepNumber, self.AbsoluteVertStart, self.AbsoluteVertEnd, self.vertStepNumber, self.fileName), None)

	def testexposeNRockGridStep(self):
		self.assertEqual(exposeNRockGridStep(self.exposeTime, self.exposeNumber, self.rockAngle, self.horizStep, self.horizStepNumber, self.vertStep, self.vertStepNumber, self.fileName), None)

	def testexposeNRockNLineAbs(self):
		self.assertEqual(exposeNRockNLineAbs(self.exposeTime, self.exposeNumber, self.rockAngle, self.rockNumber, self.motorDx, self.AbsoluteStartPos, self.AbsoluteEndPos, self.stepNumber, self.fileName), None)

	def testexposeNRockNLineAbsFail(self):
		self.assertEqual(exposeNRockNLineAbs('fail', 'fail', 'fail', 'fail', 'fail', 'fail', 'fail', 'fail', 0),
						["exposeTime should be a positive number: 'fail'", "exposeNumber should be a positive integer: 'fail'", "rockAngle should be a number: 'fail'", "rockNumber should be a positive integer: 'fail'", "lineMotor invalid, use dx, dy or dz: 'fail'", "stepNumber should be a positive integer: 'fail'", "AbsoluteStartPos should be a number: 'fail'", "AbsoluteEndPos should be a number: 'fail'"])

	def testexposeNRockNLineAbsWrongMotor(self):
		self.assertEqual(exposeNRockNLineAbs('fail', 'fail', 'fail', 'fail', self.motorFail, 'fail', 'fail', 'fail', 0),
						["exposeTime should be a positive number: 'fail'", "exposeNumber should be a positive integer: 'fail'", "rockAngle should be a number: 'fail'", "rockNumber should be a positive integer: 'fail'", 'lineMotor invalid, use dx, dy or dz: <mock.Mock object at 0x6>', "stepNumber should be a positive integer: 'fail'", "AbsoluteStartPos should be a number: 'fail'", "AbsoluteEndPos should be a number: 'fail'"])

	def testexposeNRockNLineStep(self):
		self.assertEqual(exposeNRockNLineStep(self.exposeTime, self.exposeNumber, self.rockAngle, self.rockNumber, self.motorDx, self.stepSize, self.stepNumber, self.fileName), None)

	def testexposeNRockNLineStepFail(self):
		self.assertEqual(exposeNRockNLineStep('fail', 'fail', 'fail', 'fail', 'fail', 'fail', 'fail', 0),
						["exposeTime should be a positive number: 'fail'", "exposeNumber should be a positive integer: 'fail'", "rockAngle should be a number: 'fail'", "rockNumber should be a positive integer: 'fail'", "lineMotor invalid, use dx, dy or dz: 'fail'", "stepSize should be a number: 'fail'", "stepNumber should be a positive integer: 'fail'"])

	def testexposeNRockNGridAbs(self):
		self.assertEqual(exposeNRockNGridAbs(self.exposeTime, self.exposeNumber, self.rockAngle, self.rockNumber, self.AbsoluteHorizStart, self.AbsoluteHorizEnd, self.horizStepNumber, self.AbsoluteVertStart, self.AbsoluteVertEnd, self.vertStepNumber, self.fileName), None)

	def testexposeNRockNGridAbsFail(self):
		self.assertEqual(exposeNRockNGridAbs('fail', 'fail', 'fail', 'fail', 'fail', 'fail', 'fail', 'fail', 'fail', 'fail', 0),
						["exposeTime should be a positive number: 'fail'", "exposeNumber should be a positive integer: 'fail'", "rockAngle should be a number: 'fail'", "rockNumber should be a positive integer: 'fail'", "horizStepNumber should be a positive integer: 'fail'", "vertStepNumber should be a positive integer: 'fail'", "AbsoluteHorizStart should be a number: 'fail'", "AbsoluteHorizEnd should be a number: 'fail'", "AbsoluteVertStart should be a number: 'fail'", "AbsoluteVertEnd should be a number: 'fail'"])

	def testexposeNRockNGridStep(self):
		self.assertEqual(exposeNRockNGridStep(self.exposeTime, self.exposeNumber, self.rockAngle, self.rockNumber, self.horizStep, self.horizStepNumber, self.vertStep, self.vertStepNumber, self.fileName), None)

	def testexposeNRockNGridStepFail(self):
		self.assertEqual(exposeNRockNGridStep('fail', 'fail', 'fail', 'fail', 'fail', 'fail', 'fail', 'fail', 0),
						["exposeTime should be a positive number: 'fail'", "exposeNumber should be a positive integer: 'fail'", "rockAngle should be a number: 'fail'", "rockNumber should be a positive integer: 'fail'", "horizStep should be a number: 'fail'", "horizStepNumber should be a positive integer: 'fail'", "vertStep should be a number: 'fail'", "vertStepNumber should be a positive integer: 'fail'"])
	
