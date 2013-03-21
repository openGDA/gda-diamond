from gda.device.scannable import PseudoDevice

pds=[];
all=globals();
for name,type in all.iteritems():
	if isinstance(all[name], PseudoDevice):
		pds.append(all[name]);
#		print name

for pd in pds:
	print pd.getName();
	pd.stop();
