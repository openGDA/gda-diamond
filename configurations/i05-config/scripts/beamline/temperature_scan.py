import arpes;
arpes.ARPESRun("/dls_sw/i05/scripts/arpes2.arpes").run()  ##configure only!!

# Things which need to be set #####################################################################
# Temperatures
# using range(start, stop, step)
temperatures = range(60, 300, 25)
# or a list of temperatures
#temperatures = [10, 30, 35, 50, 100]

# Tolerance parameters
tolerance = 4 # K Must be within this value of the setpoint before measuring
tolerenceWaitTime = 60 # second to wait between tolerance checks

# Stability parameters
stabilityTolerence = 0.5 # K the change must be less than this value to be considered stable
stabilityTime = 120 # Seconds over which the temperature must be stable within stabilityTolerence

##################################################################################################

# Optional items
cryostat.setRampEnable(1)
cryostat.setRampRate(2.0)
cryostat.setP(50)
cryostat.setI(40)
cryostat.setD(0)

print "Temperature script started"

for temp in temperatures:
    print "set T=", temp
    # Check the setpoint value if below 50 K use medium heater power else use high
    if temp < 50:
        cryostat.setHeaterRange(2)  #medium
    else:
        cryostat.setHeaterRange(3)  #high

    print "Waiting for cryostat to reach setpoint"
    pos cryostat temp

    # Tolerance loop
    print "Waiting for sample temperature to be in tolerance"
    while (abs(cryostat.getPosition()[2] - temp) > tolerance ): #sample temperature diff set point
        print "Temperature difference", (abs(cryostat.getPosition()[2] - temp)), "K is outside tolerance (", tolerance, "K ). Waiting 1 min"
        sleep(tolerenceWaitTime)
    print "Temperature is within tolerance"

    # Stability loop
    print "Waiting for sample temperature to stabilise for", stabilityTime, "seconds"
    referenceTemperature = cryostat.getPosition()[2]
    print "Stability reference temperature =", referenceTemperature
    stabilityTimeCounter = 0
    while (stabilityTimeCounter < stabilityTime):
        if (abs(referenceTemperature - cryostat.getPosition()[2])) > stabilityTolerence:
            stabilityTimeCounter = 0
            referenceTemperature = cryostat.getPosition()[2] # Update the reference temperature
            print "Temperature was unstable resetting stability check. Stability reference temperature =", referenceTemperature
        else:
            stabilityTimeCounter += 1 # increment the stability counter
        sleep(1) # Wait for 1 second
    print "Sample temperature is stable"

    print "Start measurement"
    print "Ts_start =", cryostat.getPosition()[2], "K"
    staticscan
    print "Ts_stop =", cryostat.getPosition()[2], "K"

print "Temperature script finished"