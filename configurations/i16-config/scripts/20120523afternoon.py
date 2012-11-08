# hk7 mesh Na0.5CoO2 15K 7.69keV Pilatus
# Afternoon 23/5/12
# RHUL

pos x1 1
pos atten 0

# 1st scan: 266070
for hpos in frange(-0.1,0.9,0.01):
	pos hkl [hpos,-0.1,7]
	try: # catch detecor malfunction
		scan hkl [hpos,-0.1,7] [hpos,0.9,7] [0,0.01,0] pil 1 checkbeam Ta Tb Tc Td delta eta chi phi roi2 roi1 roi6
	except:
		enablexps # if detector angle malfunctions, reset and restart
		scan hkl [hpos,-0.1,7] [hpos,0.9,7] [0,0.01,0] pil 1 checkbeam Ta Tb Tc Td delta eta chi phi roi2 roi1 roi6