#LAUDA

print "Script started"

pos lauda 20
scan showtime 0 1*60 1
scan lauda 20 70 2 ncddetectors
scan showtime 0 1*60 1
scan lauda 70 20 2 ncddetectors
scan showtime 0 1*60 1
scan showtime 0 1 1 ncddetectors

pos shutter "Close"
inc pxyx 75

print "Script done"
