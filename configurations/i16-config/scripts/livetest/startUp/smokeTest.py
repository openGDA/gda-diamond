import unittest
class SmokeTest(unittest.TestCase):

	def test_pos_pil(self):
		print  "="*100 + "smoke test 1: pos pil3 1 " + "="*100
		pos pil3 1

	def test_scan_x(self):
		print "="*100 + " smoke test 2: scan x 1 10 1 pil3 1 " + "="*100
		scan x 1 10 1 pil3 1

	def test_ub(selfself):
		print "="*100 + " smoke test 2: ub " + "="*100
		ub

	def test_scan_eta_pil_roi(self):
		print "="*100 + " smoke test 3: scancn phi .01 21 pil3 .5 lcroi " + "="*100
		scancn phi .01 21 pil3 .5 lcroi

	def test_scan_eta_pil_roi(self):
		print "="*100 + " smoke test 3: scancn eta .01 11 pil3 1 lcroi " + "="*100
		scancn eta .01 11 pil3 1 lcroi

if __name__ == '__main__':
	#unittest.main() - this brings down the command server! See DAQ-770
	print "Run Smoke Tests"
	suite = unittest.TestLoader().loadTestsFromTestCase(SmokeTest)
	unittest.TextTestRunner(verbosity=2).run(suite)