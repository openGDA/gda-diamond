g00=62.4555
for kpval in [-66.7,23.3,113.3,203.3]:
	pos kphi kpval gam g00
	pos s6hgap 1
	scancn kphi 0.01 100 t 1 checkbeam
	go FindScanPeak('APD')['kphi']
	kp0=kphi()
	pos s6hgap .1
	scancn gam 0.01 100 t 1 checkbeam
	go FindScanPeak('APD')['gam']
	g0=gam()
	scan kphi kp0-.5 kp0+.5 0.01 gam g0-1 0.02 t 1 checkbeam
	pos kphi kp0
	for gval in frange(62,62.8,0.01):
		pos gam gval
		scancn kphi 0.01 80 t 1 checkbeam

#first: 81400
