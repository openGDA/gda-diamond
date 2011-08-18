counterTimer01.clearFrameSets() 
counterTimer01.addFrameSet(3,1.0e-4,1000,0,0,-1,0)
counterTimer01.addFrameSet(1,1.0e-4,2000,0,0,-1,0)
counterTimer01.addFrameSet(1,1.0e-4,3000,0,0,-1,0)
counterTimer01.loadFrameSets()
counterTimer01.start()
counterTimer01.restart()

for i in range(4):
	print 'a'
	print counterTimer01.getStatus()
	sleep(1.0)
	counterTimer01.restart()
#counterTimer01.restart()
for i in range(4):
	print 'b'
	print counterTimer01.getStatus()
	sleep(2.0)
counterTimer01.restart()
for i in range(4):
	print 'c'
	print counterTimer01.getStatus()
	sleep(2.0)


print counterTimer01.readFrame(0)
print counterTimer01.readFrame(0,4,0)
print counterTimer01.readFrame(1)
print counterTimer01.readFrame(0,4,1)
print counterTimer01.readFrame(2)
print counterTimer01.readFrame(0,4,2)
print counterTimer01.readFrame(3)

counterTimer01.stop()
