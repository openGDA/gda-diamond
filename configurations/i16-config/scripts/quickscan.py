import read_list_pd 

adcvals=[]
times=[]
inctime.atScanStart()

print "starting"
for i in range(10):
	adcvals+=[adc1()]
	times+=[inctime()]
print "done"

scan x 0 9 1 ReadListPVClass('list',adcvals,'units','%.3f') 0 1 ReadListPVClass('list',times,'units','%.3f') 0 1 