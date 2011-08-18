print 'showtime1:',showtime()
counterTimer01.clearFrameSets() 
counterTimer01.addFrameSet(20,1000,1.0E-4,0,0,-1,0)
counterTimer01.loadFrameSets()
counterTimer01.start()
for i in range(20):
	counterTimer01.restart()
	while(counterTimer01.getStatus()==1):
		continue
		sleep(0.05)
print 'showtime2:',showtime()
for i in range(20):
	counterTimer01.countAsync(1000)
	while(counterTimer01.getStatus()==1):
		#continue
		sleep(0.05)
print 'showtime3:',showtime()
