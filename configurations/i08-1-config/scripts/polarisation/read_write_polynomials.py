from gda.epics import CAClient

ca = CAClient()

print("Running read_write_polynomials script")

#coefficients path
inputPath='/dls_sw/i08-1/scripts/polynomials/'

def read_poly(direction,pol_list):
    rows=12
    cols=len(pol_list)
    txt = inputPath + "polyfit_coeff_" + direction + ".dat"
    
    # Commenting out unused line of code
    #arr = [[0 for i in range(cols)] for j in range(rows)]
    
    # set data to be an empty list
    data = []
    # open file in read mode
    with open(txt, 'r') as f:
        f.readline() # skip header
        for line in f:
            parts = line.split()
            parts.pop(0)  # remove first column (label)
            data.append(parts)
        
    # Commenting out unused line of code
    # coef = ['A','B','C','D','E','F','G','H','I','J','K','L']    
    return(data)
        
def write_polynomials(undulator, direction, pol):
    # Add in EPICS table the new polynomial coefficients extracted from August/Sept. 2020 analysis
    
    # Map polarisation labels to EPICS suffixes, depending on direction
    if direction == 'forward':
        pol_all = {'LH': 'VT','LV':'VT','C':'VT'}
        
    else:
        pol_all={'LH': 'BVT','LV':'BVT','C':'BVT'} # 'B' = backward direction

    # Column indices for each polarisation in the coefficient array
    cols_all = {'LH': 0, 'LV': 1, 'C': 2}
    
    rows=12 # Number of polynomial coefficients
    cols=cols_all[pol] # Get the column index for the selected polarisation
    
    # Read polynomial coefficient array (12 rows × 3 polarisation types)
    arr = read_poly(direction,['LH','LV','C'])
    
    # Write each coefficient to the corresponding EPICS PV
    for i in range(rows):
        pv = 'BL08I-OP-' + undulator + '-01:' + pol_all[pol] + ':C' + str(i + 1)
        # Example PV: BL08I-OP-ID-01:VT:C1
        #print(pv,arr[i][cols])
        ca.put(pv,arr[i][cols]) # Only writes to the selected polarisation type column

def set_ID_poly(pol):
    # Sets polynomial coefficients for both forward and backward directions
    write_polynomials("ID", "forward",  pol)
    write_polynomials("ID", "backward", pol)
    
    
    