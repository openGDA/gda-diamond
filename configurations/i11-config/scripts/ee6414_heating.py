'''
Created on 23 Sep 2011

@author: fy65
'''
start_temp=900.0
end_temp=1100.0
heating_rate=0.1
exposure_time=15.0

pos capf start_temp
sleep(30)
scan delta 2 2.25 0.25 smythen 15.0
capf.setRampRate(heating_rate)
capf.asynchronousMoveTo(end_temp) #non-blocking call
#capf.moveTo(end_temp) #block call

while (float(capf.getPosition())<end_temp):
    scan delta 2 2.25 0.25 smythen 15.0
    
