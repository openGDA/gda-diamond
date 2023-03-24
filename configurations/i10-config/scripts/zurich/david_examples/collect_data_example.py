import zhinst.ziPython 
import time

# Open connection to ziServer
#daq = zhinst.ziPython.ziDAQServer('172.23.110.84', 8004, 6)
daq = zhinst.ziPython.ziDAQServer('172.23.240.161', 8004, 6)


# setup dynamics
daq.setInt('/dev4206/demods/0/enable', 1) # Enable the demodulator output 
daq.setDouble('/dev4206/demods/0/rate', 100) # set transfer rate 100 S/s
daq.subscribe('/dev4206/demods/0/sample')


# setup statics
h = daq.scopeModule()
path = '/dev4206/scopes/0/wave'
h.subscribe(path)
h.set('scopeModule/mode', 0)
h.set('scopeModule/historylength', 1)

daq.setInt('/dev4206/scopes/0/channels/0/inputselect', 0) #select voltage input
daq.setDouble('/dev4206/scopes/0/length', 4096) #set sample length
daq.setInt('/dev4206/scopes/0/time', 5) #set sample rate

daq.setInt('/dev4206/scopes/0/enable', 1) # start continuous triggering

h.execute()
while h.progress() < 1:
    pass


time.sleep(10)







# collect data

for i in range(20):
    time.sleep(1.1) # wait while collecting data
    
    #dynamics readout
    data_d = daq.poll(0.020, 10, 0, True) # poll demodulator outputs 
    x = data_d['/dev4206/demods/0/sample']['x'][:-100].mean() # mean of demodulator output in the last 100 samples (1 s)
    y = data_d['/dev4206/demods/0/sample']['y'][:-100].mean()
    
    #statics readout
    data_s = h.read(True)
    static = data_s[path][0][0]['wave'].flatten().mean() * data_s[path][0][0]['channelscaling'][0]
   
    
    print static, x, y






