# Recording initial RL-position
#234790
hkl_temp=[3.500003665148893, 0.00018160908354874356, -0.000433292530619956]
pos atten 10

for evalue in frange(6.52,6.56,0.001):
	pos energy evalue
	pos hkl hkl_temp
	scancn eta 0.01 41 pil 3 checkbeam roib1 roib2 roib3 roib4 roi6 roi1
	
