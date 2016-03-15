#LAUDA
'''
Lauda bath maximum rates that can be sensibly achieved:

Big one - Integral T: UP:
            DOWN:
            
Medium one - RE510: UP:
                    DOWN:
                    
Little one -        : UP:
                    : DOWN:
                    

If you try to exceed these rates, you won't get linear ramps!

'''
       

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
