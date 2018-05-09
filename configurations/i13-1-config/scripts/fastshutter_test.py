import time
def fastshutter_test(posn, itersleep=1, niter=30):
	failed = True
	if posn=="Open" or posn=="Close" or posn=="Closed":
		_posn_out_dct = {"Open": "Open", "Close": "Closed", "Closed": "Closed"}
		pos expt_fastshutter posn
		cnt = 0
		failed = True
		while failed and (cnt < niter):
			posn_out=expt_fastshutter.getPosition()
			if posn_out==_posn_out_dct[posn]:
				failed = False
				print "Shutter found in the desired position %s on count %i" %(_posn_out_dct[posn], cnt)
			else:
				cnt += 1
				time.sleep(itersleep)
				print " %i zzz..." %(cnt)
	else:
		print("Unsupported shutter position: %s" %(posn))
	return (not failed)

def fastshutter_ntests(ntests, testsleep=1, itersleep=1, niter=30):
	_posn_toggle_dct = {"Open": "Closed", "Close": "Open", "Closed": "Open"}
	for i in range(ntests):
		posn_curr=expt_fastshutter.getPosition()
		success = fastshutter_test(_posn_toggle_dct[posn_curr], itersleep, niter)
		if not success:
			print "Tests failed while changing shutter position from %s to %s on test %i (of %i)" %(posn_curr, _posn_toggle_dct[posn_curr], (i+1), ntests)
			break
		time.sleep(testsleep)
	print("Finished shutter tests on test %i - bye!" %(i+1))
