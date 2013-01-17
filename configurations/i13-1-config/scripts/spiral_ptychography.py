'''
Created on 19 Nov 2012

@author: tjs15132
'''
import math
if __name__ == '__main__':
    asize = (300, 300);
    a2 = asize[0] * asize[1];

    # Physical parameters for this dataset

# all lengths in meter

    energy = 8.7;           # Energy (in keV)
    lambda1 = 1.2398e-9/energy;  # wavelength

    dr = 0.5e-6;                # shell step size
    lx =10e-6;                 # field of view (x)
    ly =10e-6;                 # field of view (y)
    nth = 5 ;                    # theta intervals in first shell

    dwell_time = 0.1;             # Counts per diffraction pattern in seconds
    projections = 1;          # Number of scans to be run
    
    z = 2.1;                     # Distance from object to screen 
    ds = 20e-6;                  # Camera pixel size
    
    dx_spec = (lambda1*z /(asize[0]*ds),lambda1*z /(asize[1]*ds) )         # resolution in the specimen plane
    
    theta_offset = 0;          # Offset the whole scan by this number of degrees
    ## Prepare field of view
    
    rmax = math.sqrt((lx/2)*(lx/2) + (ly/2)*(ly/2));
    nr = int(1 + math.floor(rmax/dr));
    real_positions = [];
    positions = [];
    for ir in range(1, nr+2):
        rr = ir*dr;
        dth = 2*math.pi / (nth*ir);
        for ith in range(0,nth*ir):
            th = ith*dth + (theta_offset*math.pi/180);
            x2 = rr * math.cos(th);
            x1 = rr * math.sin(th);
            if( abs(x1) >= ly/2 or (abs(x2) > lx/2) ):
                continue
            real_positions.append((x1, x2)); ##ok<AGROW>
    
    # For now: round this up
    real_positions_zipped = zip(*real_positions)
    min_real_position_x = min(real_positions_zipped[0])
    min_real_position_y = min(real_positions_zipped[1])
    positions=[]
    for x , y in real_positions:
#        print x,y, min_real_position_x, dx_spec[0]
        x11 = ( x - min_real_position_x) /dx_spec[0]
        y11 = ( y - min_real_position_y) /dx_spec[1]
        positions.append((x11,y11))
    for i,pos in enumerate(positions):
        print i+1,pos

    f = open("/dls_sw/i13-1/scripts/spiral.txt","w")
    for x,y in positions:
        f.write ( `x` + " " + `y` + "\n")
    f.close()
    
