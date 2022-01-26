#533702
pos atten 100
hh=[2,2,2]

def opt():
	scancn eta 0.01 41 checkbeam pil 0.2 roi2
	go maxval
	scancn delta 0.01 41 checkbeam pil 0.2 delroi
	go maxval
	scancn chi 0.01 41 checkbeam pil 0.2 chiroi
	go maxval
	scancn eta 0.001 41 checkbeam pil 0.2 roi2
	go maxval
while 1:
	for psival in [-26.12,-24.6,-9.39]:
		pos psic psival
		pos hkl hh
		opt()
		hh=hkl()
		for ii in frange(1,10,1):
			scancn eta 0.001 41 checkbeam pil 0.2 roi2
		for ii2 in frange(1,10,1):
			scancn psic 0.001 1001 hkl hh checkbeam pil 0.2 roi2 roi1
		for psival2 in frange(psival-0.2,psival+0.2,0.01):
			pos psic psival2
			pos hkl hh
			scancn eta 0.001 51 checkbeam pil 0.2 roi2 roi1

