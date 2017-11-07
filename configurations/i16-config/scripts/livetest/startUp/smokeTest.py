import unittest
class SmokeTest(unittest.TestCase):

	def test_pos_pil(self):
		print "smoke test 1: pos pil 1 "
		pos pil 1
	def test_scan_x(self):
		print "smoke test 2: scan x 1 10 1"
		scan x 1 10 1
	def test_scan_eta_pil_roi(self):
		print "smoke test 3: scancn eta .01 11 pil 1 lcroi"
		scancn eta .01 11 pil 1 lcroi
		
	
if __name__ == '__main__':
	#unittest.main() - this brings down the command server! See DAQ-770
	print "Run Smoke Tests"
	suite = unittest.TestLoader().loadTestsFromTestCase(SmokeTest)
	unittest.TextTestRunner(verbosity=2).run(suite)