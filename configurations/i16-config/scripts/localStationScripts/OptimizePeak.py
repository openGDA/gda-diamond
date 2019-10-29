def optimizePeak(hkl0,dd,counter,tt):
	hkl(hkl0)
	eta0=eta()
	chi0=chi()
	delta0=delta()
	scan eta eta()-dd eta()+dd 0.01 hpos vpos rc ic1 ic2 ct1 counter tt
	peak = FindScanPeak(counter.name)
	eta1=peak['eta']
	scan chi chi()-dd chi()+dd 0.01 eta eta1 hpos vpos rc ic1 ic2 ct1 counter tt
	peak = FindScanCentroid(counter.name,'chi')
	chi1 = peak['chi']
	pos chi chi1 eta eta1
	scan delta delta()-dd delta()+dd 0.01 hpos vpos rc ic1 ic2 ct1 counter tt
	peak = FindScanCentroid(counter.name,'delta')
	delta1 = peak['delta']
	pos delta delta1
	scan eta eta1-dd eta1+dd 0.005 hpos vpos rc ic1 ic2 ct1 counter tt
	peak = FindScanPeak(counter.name)
	eta2 = peak['eta']
	pos eta eta2
	hkl1 = hkl()
	return hkl1

def OP2(hkl0,dd=.02,dd2=.2,counter=ct3,tt=.1):
	step=2*dd/31.
	step2=2*dd2/31.
	hkl(hkl0)
	eta0=eta()
	chi0=chi()
	delta0=delta()
	scan eta eta()-dd eta()+dd step hpos vpos rc ic1 ic2 counter tt
	peak = FindScanPeak(counter.name)
	eta1=peak['eta']
	scan chi chi()-dd2 chi()+dd2 step2 eta eta1 hpos vpos rc ic1 ic2 counter tt
	peak = FindScanCentroid(counter.name,'chi')
	chi1 = peak['chi']
	pos chi chi1 eta eta1
	scan delta delta()-dd2 delta()+dd2 step2 hpos vpos rc ic1 ic2 counter tt
	peak = FindScanCentroid(counter.name,'delta')
	delta1 = peak['delta']
	pos delta delta1
	scan eta eta1-dd eta1+dd step hpos vpos rc ic1 ic2 counter tt
	peak = FindScanPeak(counter.name)
	eta2 = peak['eta']
	pos eta eta2
	hkl1 = hkl()
	return hkl1

def OP3(hkl0,dd=.2,dd2=.2,counter=ct3,tt=.1):
	step=2*dd/30.
	step2=2*dd2/30.
	hkl(hkl0)
	eta0=eta()
	chi0=chi()
	delta0=delta()
	scan eta eta()-dd eta()+dd step hpos vpos rc ic1 ic2 counter tt
	peak = FindScanPeak(counter.name)
	eta1=peak['eta']
	scan chi chi()-dd2 chi()+dd2 step2 eta eta1 hpos vpos rc ic1 ic2 counter tt
	peak = FindScanPeak(counter.name,'chi')
	chi1 = peak['chi']
	pos chi chi1 eta eta1
	scan delta delta()-dd2 delta()+dd2 step2 hpos vpos rc ic1 ic2 counter tt
	peak = FindScanPeak(counter.name,'delta')
	delta1 = peak['delta']
	pos delta delta1
	scan eta eta1-dd eta1+dd step hpos vpos rc ic1 ic2 counter tt
	peak = FindScanPeak(counter.name)
	eta2 = peak['eta']
	pos eta eta2
	hkl1 = hkl()
	return hkl1

