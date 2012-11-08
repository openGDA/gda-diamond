
from scannable.sampler import Sampler, SumProcessor, RmsProcessor
from mock import Mock
import unittest
from gda.device import Scannable
POSITIONS = []



		
class TestSampler(unittest.TestCase):
	
	def setUp(self):
		self.mock_scn = Mock(spec=Scannable)
		self.mock_scn.name = 'scn'
		self.mock_scn.outputFormat = '%.4f'
		self.mock_scn.getPosition.side_effect = self.pop_position
		self.sampler = Sampler(self.mock_scn, [SumProcessor()], True)
		self.positions_to_pop = []
		
	def pop_position(self):
		return self.positions_to_pop.pop(0)
	def test_name(self):
		self.assertEqual(self.sampler.getName(), 'scn_sampler')
		
	def test_inputNames(self):
		self.assertEqual(list(self.sampler.getInputNames()), ['scn_tsamp', 'scn_nsamp'])
		
	def test_getOutputFormat_no_sample_readout(self):
		sampler = Sampler(self.mock_scn, [SumProcessor()], False)
		self.assertEqual(sampler.getExtraNames(), ['scn_sum'])

	def test_getOutputFormat_with_sample_readout(self):
		sampler = Sampler(self.mock_scn, [SumProcessor()], True)
		self.positions_to_pop = [2, 3, 5, 1000]
		sampler.asynchronousMoveTo([1.23, 3])
		self.assertEqual(sampler.getExtraNames(), ['scn_0', 'scn_1', 'scn_2', 'scn_sum'])

	def testIsBusy(self):
		self.assertFalse(self.sampler.isBusy())
		
	def test_asynchronousMoveTo_and_getPosition_no_sample_readout(self):
		sampler = Sampler(self.mock_scn, [SumProcessor()], False)
		self.positions_to_pop = [2, 3, 5]
		sampler.asynchronousMoveTo([1.23, 3])
		self.assertEqual(sampler.getPosition(), [1.23, 3, 10])
		
	def test_asynchronousMoveTo_and_getPosition_with_sample_readout(self):
		sampler = Sampler(self.mock_scn, [SumProcessor()], True)
		self.positions_to_pop = [2, 3, 5]
		sampler.asynchronousMoveTo([1.23, 3])
		self.assertEqual(sampler.getPosition(), [1.23, 3, 2, 3, 5, 10])
	
#===============================================================================
	
	def test_sum(self):
		p = SumProcessor()
		self.assertEqual(p.process([1,2,3,4]), 10)
						
	def test_rms(self):
		p = RmsProcessor()
		self.assertEqual(p.process([1,2,3,4]), 2.7386127875258306)


def suite():
	return unittest.TestLoader().loadTestsFromTestCase(TestSampler)

if __name__ == '__main__':
	unittest.TextTestRunner(verbosity=2).run(suite())