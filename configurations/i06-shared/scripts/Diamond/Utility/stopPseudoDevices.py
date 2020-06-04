from gda.device.scannable import ScannableMotionBase

pds=[];
all=globals();
for name,type in all.iteritems():
	if isinstance(all[name], ScannableMotionBase):
		pds.append(all[name]);
#		print name

for pd in pds:
	print pd.getName();
	pd.stop();
