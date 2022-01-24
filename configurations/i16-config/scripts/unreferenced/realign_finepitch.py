#print 'CHECK ATTENUATION FIRST!!!'

sleep(3)

oldatten=atten()
olds6hgap = s6hgap()
olds6vgap = s6vgap()
olddelta = delta()
oldzp = zp()
oldthp = thp()
oldtthp = tthp()
oldeta = eta()
oldfinepitch = finepitch()

inc sz -1
atten(96)
pos s6vgap .1 s6hgap 5 eta 0 delta 0 tthp -2.5 thp 180 zp 5


#scan finepitch -100 100 10 adc4 adc6 ct3 .1
#peak = FindScanPeak('ct3')
#newp = peak['finepitch']
fp0 = oldfinepitch
#pos qbpm6 2

scan finepitch (fp0-20) (fp0+20) 1 adc4 adc6 ct3 .1
peak = FindScanPeak('ct3')
print 'wait for completion'

finepitch(peak['finepitch'])

pos tthp oldtthp thp oldthp zp oldzp delta olddelta eta oldeta s6hgap olds6hgap s6vgap olds6vgap atten oldatten 
inc sz 1
print 'old finepitch:', oldfinepitch
print 'new finepitch:', peak['finepitch']
print 'ready'
