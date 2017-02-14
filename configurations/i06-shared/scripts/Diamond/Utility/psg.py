
#An utility function to print out the result of ScannableGroup members 
def psg(sm):
	if not isinstance(sm, gda.device.scannable.scannablegroup.ScannableGroup):
		print "This device is not a 'ScannableGroup' type"
		return;
	
	for sn in sm.getGroupMemberNames():
		s=sm.getGroupMember(sn);
		print s;

alias("psg")
