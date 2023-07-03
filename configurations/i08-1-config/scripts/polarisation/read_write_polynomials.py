from gda.epics import CAClient

ca = CAClient()

print("Running read_write_polynomials script")

#coefficients path
inputPath='/dls_sw/i08-1/scripts/polynomials/'

def read_poly(direction,pol_list):
    rows=12
    txt = inputPath + "polyfit_coeff_"+direction+".dat"
    cols=len(pol_list)
    arr = [[0 for i in range(cols)] for j in range(rows)]
    f=open(txt, 'r')
    f.readline()
    data=[]
    for line in f:
        help2=line.split()
        help2.pop(0)
        data.append(help2)
        
    coef = ['A','B','C','D','E','F','G','H','I','J','K','L']    
    return(data)
        
def write_polynomials(undulator, direction, pol):
    # Add in EPICS table the new polynomial coefficients extracted from August/Sept. 2020 analysis
    
    if direction == 'forward':
        pol_all = {'LH': 'VT','LV':'VT','C':'VT'}
        
    else:
        pol_all={'LH': 'BVT','LV':'BVT','C':'BVT'} # relates polarisation to the name given name, B represents backward 

    cols_all = {'LH': 0,'LV':1,'C':2}
    
    rows=12
    cols=cols_all[pol]
    
    arr = read_poly(direction,['LH','LV','C'])
    
    for i in range(rows):
        pv = 'BL08I-OP-'+undulator+'-01:'+pol_all[pol]+':C'+str(i+1)
        #print(pv,arr[i][cols])
        ca.put(pv,arr[i][cols])

def set_ID_poly(pol):
    write_polynomials("ID", "forward",  pol)
    write_polynomials("ID", "backward", pol)