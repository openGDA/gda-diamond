import time 

            
def setTemperature(temp):
    from beamline import device
    ca = device()
    ca.caput("ME01D-EA-TCTRL-01:SETP_S", str(temp))
    time.sleep(1)
    
    tolerence = 0.5
    stableTime = 100
    stableSince = time.time()
    
    while True:
        if abs(float(ls340.getPosition()[0]) - temp) > tolerence:
            stableSince = time.time()        
        
        if time.time() > stableSince + stableTime:
            print "temperature stable"
            break
        
        time.sleep(1)
        print "waiting for temperature",ls340.getPosition()[0] , " " , temp

           