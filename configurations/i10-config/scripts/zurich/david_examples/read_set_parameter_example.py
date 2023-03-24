
import zhinst.ziPython

# Open connection to ziServer
#daq = zhinst.ziPython.ziDAQServer('172.23.110.84', 8004, 6)
daq = zhinst.ziPython.ziDAQServer('172.23.240.161', 8004, 6)





""" set volts per amp output scale """

daq.setDouble('/dev4206/auxouts/0/scale', 2)
daq.setDouble('/dev4206/auxouts/1/scale', 5)



""" read volts per amp output scale """

sample = daq.get('/dev4206/auxouts/0/scale')
print sample['dev4206']['auxouts']['0']['scale']['value'][0]

sample = daq.get('/dev4206/auxouts/1/scale')
print sample['dev4206']['auxouts']['1']['scale']['value'][0]

