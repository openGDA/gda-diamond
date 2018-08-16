print 'CHECK ATTENUATION FIRST!!!'

sleep(3)

oldatten=atten()
olds6hgap = s6hgap()
olds6vgap = s6vgap()
olddelta = delta()
oldbase_z = base_z()
oldthp = thp()
oldtthp = tthp()
oldeta = eta()
oldfinepitch = finepitch()

#inc sz -1 ##################################
atten(100)
pos tthp -2.5 s6vgap .1 s6hgap 5 eta 0 delta 0.085 thp 0 
pos base_z -1


#scan finepitch -100 100 10 adc4 adc6 ct3 .1
#peak = FindScanPeak('ct3')
#newp = peak['finepitch']
fp0 = oldfinepitch
scan finepitch (fp0-20) (fp0+20) 1 adc4 adc6 ct3 .1
peak = FindScanPeak('ct3')
print 'wait for completion'

#try:
finepitch(peak['finepitch'])
	#print 'finepitch realigned'
#except:
#	finepitch(oldfinepitch)
#	print 'back to good old finepitch'

pos tthp oldtthp thp oldthp base_z oldbase_z[0] delta olddelta eta oldeta s6hgap olds6hgap s6vgap olds6vgap atten oldatten 
#inc sz 1 ###########################
print 'old finepitch:', oldfinepitch
print 'new finepitch:', peak['finepitch']
print 'ready' 
