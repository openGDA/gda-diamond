def OP2(hkl0,dd=.2,dd2=.2,counter=ct3,tt=.1):
	step=2*dd/30.
	step2=2*dd2/30.
	hkl(hkl0)
	eta0=eta()
	chi0=chi()
	delta0=delta()
	scan eta eta()-dd eta()+dd step rc ic1 ic2 counter tt
	peak = FindScanPeak(counter.name)
	eta1=peak['eta']
	scan chi chi()-dd2 chi()+dd2 step2 eta eta1 rc ic1 ic2 counter tt
	peak = FindScanCentroid(counter.name,'chi')
	chi1 = peak['chi']
	pos chi chi1 eta eta1
	scan delta delta()-dd2 delta()+dd2 step2 rc ic1 ic2 counter tt
	peak = FindScanCentroid(counter.name,'delta')
	delta1 = peak['delta']
	pos delta delta1
	scan eta eta1-dd eta1+dd step rc ic1 ic2 counter tt
	peak = FindScanPeak(counter.name)
	eta2 = peak['eta']
	pos eta eta2
	hkl1 = hkl()
	return hkl1


def OP3(hkl0=hkl(),tt=1):
	scancn eta 0.01 71 t tt
	peak = FindScanCentroid('APD','eta')
	eta1 = peak['eta']
	pos eta eta1
#	go maxpos

	scancn chi 0.02 51 t tt
	peak = FindScanCentroid('APD','chi')
	chi1 = peak['chi']
	pos chi chi1
	
	scancn delta 0.02 51 t tt
	peak = FindScanCentroid('APD','delta')
	delta1 = peak['delta']
	pos delta delta1
			
	scancn eta 0.005 71 t tt
	peak = FindScanCentroid('APD','eta')
	eta1 = peak['eta']
	pos eta eta1


#latt([4.99393227096, 4.99393227096, 13.9156606363, 90.0, 90.0, 120])
#reffile('V2O3')
#showref()
#ubm()
