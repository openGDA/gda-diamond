'''
X-ray beam alignment for Grazing Incidence X-ray Powder Diffraction experiments
Created on 23 Jan 2015

@author: fy65
'''
# motors: height. chi, psi
# detcetor: etl1, (based on scaler2 channel 18, and elt1detector) 

#mount sample with white tag 
#doing optical alignment first - height
#install beam stop
#doing sample alignment with beam
# find the beam through detector 1st
# put detector in beam - delta=0
# move sample Down
# looking for delta peak position
cscan delta 0.01 0.002 etl1
# move delta to the peak=17.444
move delta 17.444
# move sample back 
pos height 0
# get through beam to detector
pos height 0.5
#align theta
pos theta 3
scan theta -3 3 0.1 etl1 1
#move to the center of the profile 0
pos theta 0
# move height
pos height 0.3
# repeat theta scan
scan theta -3 3 0.2 etl1 1
#repeat above
pos theta 0
pos height 0.1
scan theta -2 2 0.1 etl1 1

pos theta 0.1
cscan theta 1 0.05 etl1 1
# 0 is good
pos theta 0
# align height
pos height 0
scan height -0.2 0.2 0.05 etl1 1
scan height -.03 0.3 0.01 etl1 1
# find the position for half way of the through beam
pos height -0.013
cscan theta 1 0.01 etl1 1
# do a fitting to find the peak at 0.038
pos theta 0.038

# set the theta start position to 4
pos theta 0.038+4



 