
from gdascripts.pd.dummy_pds import DummyPD

import unittest

class MockCounter:
	'''Dummy PD Class'''
	def __init__(self, name):
		self.busy = False
		self.countTime = 0
		self.toReturn = None
		
	def isBusy(self):
		return self.busy

	def asynchronousMoveTo(self,new_position):
		self.countTime = float(new_position)
		self.busy = True
		
	def getPosition(self):
		return self.toReturn
		
	def complete(self):
		self.toReturn = 2*self.countTime
		self.busy = False
		
		
class TestWaitWhileScannableBelowThreshold(unittest.TestCase):
	def setUp(self):
		self.mon = DummyPD('mon')
		self.cnt = MockCounter()
		
	def testMockCounter(self):
		# usage:
		self.assertEqual(self.cnt.isBusy(), False)
		self.cnt.asynchronousMoveTo(1.)
		self.assertEqual(self.cnt.isBusy(), True)
		self.cnt.complete()
		self.assertEqual(self.cnt.isBusy(), False)
		self.assertEqual(self.cnt.getPosition(), 2.)
		
		




def suite():
	return unittest.TestLoader().loadTestsFromTestCase(TestWaitWhileScannableBelowThreshold)

if __name__ == '__main__':
	unittest.TextTestRunner(verbosity=2).run(suite())