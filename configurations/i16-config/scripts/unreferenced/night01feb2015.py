#495244-495276
hh=[0,0,2.1]
for psival in frange(42,135,6)+frange(-45,-138,6):
	pos psic psival
	scan energy 6 6.16 0.02 checkbeam hkl hh pil 150
