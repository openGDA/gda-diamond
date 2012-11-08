#start 177193-177204-
#177205-177218

#177234

#reffile('GdMn2O5_S3_3IC'), from reflection 12

#hklhtn=[4.49731638810769, 3.992654636265599, -0.0047002003712079965]
hklhtn=[4.486120986206422, 3.9944859828952537, 0.18211670979809322]

for tval in frange(37,45,0.5):
	pos tset tval
	w(30)
	pos hkl hklhtn
	scancn eta 0.003 31 checkbeam Ta Tb pil 1 roib1 roib2 roib3 roi4 roi2 roi1
	go maxpos
	scancn chi 0.01 31 checkbeam Ta Tb pil 1 roib1 roib2 roib3 roi1 roi2 roi4
	go maxpos
	hklhtn=hkl()
	saveref()

pos tval
pos hkl

#reffile('GdMn2O5_S3_3')


#hklic1=[4.486120986206422, 3.9944859828952537, 0.18211670979809322]