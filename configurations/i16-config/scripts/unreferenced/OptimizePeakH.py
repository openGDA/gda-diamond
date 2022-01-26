def optimizePeakH(hkl0,dd,counter,tt):
	hkl(hkl0)
	mu0=mu()
	chi0=chi()
	gam0=gam()
	scan mu mu()-dd mu()+dd 0.01 hpos vpos rc ic1 ic2 ct1 counter tt
	peak = FindScanPeak(counter.name)
	mu1=peak['mu']
	scan chi chi()-dd chi()+dd 0.01 mu mu1 hpos vpos rc ic1 ic2 ct1 counter tt
	peak = FindScanCentroid(counter.name,'chi')
	chi1 = peak['chi']
	pos chi chi1 mu mu1
	scan gam gam()-dd gam()+dd 0.01 hpos vpos rc ic1 ic2 ct1 counter tt
	peak = FindScanCentroid(counter.name,'gam')
	gam1 = peak['gam']
	pos gam gam1
	scan mu mu1-dd mu1+dd 0.005 hpos vpos rc ic1 ic2 ct1 counter tt
	peak = FindScanPeak(counter.name)
	mu2 = peak['mu']
	pos mu mu2
	hkl1 = hkl()
	return hkl1

def OP2H(hkl0,dd=.2,dd2=.2,counter=ct3,tt=.1):
	step=2*dd/60.
	step2=2*dd2/60.
	hkl(hkl0)
	mu0=mu()
	chi0=chi()
	gam0=gam()
	scan mu mu()-dd mu()+dd step hpos vpos rc ic1 ic2 counter tt
	peak = FindScanPeak(counter.name)
	mu1=peak['mu']
	pos mu mu1
	scan chi chi()-dd2 chi()+dd2 step2 hpos vpos rc ic1 ic2 counter tt
	peak = FindScanCentroid(counter.name,'chi')
	chi1 = peak['chi']
	pos chi chi1 
	scan gam gam()-dd2 gam()+dd2 step2 hpos vpos rc ic1 ic2 counter tt
	peak = FindScanCentroid(counter.name,'gam')
	gam1 = peak['gam']
	pos gam gam1
	scan mu mu1-dd mu1+dd step hpos vpos rc ic1 ic2 counter tt
	peak = FindScanPeak(counter.name)
	mu2 = peak['mu']
	pos mu mu2
	hkl1 = hkl()
	return hkl1

def OP3H(hkl0,dd=.2,dd2=.2,counter=ct3,tt=.1):
	step=2*dd/30.
	step2=2*dd2/30.
	hkl(hkl0) 
	mu0=mu()
	chi0=chi()
	gam0=gam()
	scan mu mu()-dd mu()+dd step hpos vpos rc ic1 ic2 counter tt
	peak = FindScanPeak(counter.name)
	mu1=peak['mu']
	pos mu mu1
	scan chi chi()-dd2 chi()+dd2 step2 hpos vpos rc ic1 ic2 counter tt
	peak = FindScanPeak(counter.name,'chi')
	chi1 = peak['chi']
	pos chi chi1 mu mu1
	scan gam gam()-dd2 gam()+dd2 step2 hpos vpos rc ic1 ic2 counter tt
	peak = FindScanPeak(counter.name,'gam')
	gam1 = peak['gam']
	pos gam gam1
	scan mu mu1-dd mu1+dd step hpos vpos rc ic1 ic2 counter tt
	peak = FindScanPeak(counter.name)
	mu2 = peak['mu']
	pos mu mu2
	hkl1 = hkl()
	return hkl1

