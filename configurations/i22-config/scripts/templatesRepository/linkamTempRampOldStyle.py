#Crystallisation Study script
#the following line sets the ramp rate
linkam.setRate(30)
#the next line sets the limit temperature
linkam(130)
#the next line makes the DSC/Linkam hold for 300sec
sleep(300)
#the following line sets the ramp next rate
linkam.setRate(50)
#the next line sets the limit temperature
linkam(100)
#the following line would run whatever was in ncddetectors e.g. 100 frames 10
staticscan ncddetectors
