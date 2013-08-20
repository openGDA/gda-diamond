
#Old version of magnet control
#from Diamond.Magnet.i06Magnet import i06Magnet
from Diamond.Magnet.i06Magnet import *

print "init_i06_magnet startup script"

print "making the complete magnet object"
psuTolerance = 0.005
magnet = i06Magnet("i06Magnet")

print "magnet: " + str(magnet)
