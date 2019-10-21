


move_m5tth(ang, m, c):
    '''
    Move m5tth to the input angle (ang) and m5hqry to another angle,
    calculated from the input ang using a given linear function with
    slope m and intercept c, ie m*ang + c. 
    '''
    print("Moving m5tth to %.3f..." %(ang))    
    m5tth.moveTo(ang)
    interp_ang = m*ang + c
    print("Moving m5hqry to %.3f..." %(interp_ang))
    m5hqry.moveTo(interp_ang)
    print("All done!)
 
