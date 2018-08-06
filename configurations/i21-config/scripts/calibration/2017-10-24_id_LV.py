#Switch on scan processor
scan_processing_on()
#pos FPSelection 24.43 # DET3
gap_filename = '/dls_sw/i21/scripts/Polarimeter/LVgap50eV.csv'
fh = open(gap_filename, 'r')
 
energy_gap = []
 
for line in fh:
    e, gap = line.split(',')
    energy_gap.append((e, gap))
     
     
     
fh.close()

print(energy_gap)
 
write_gap_file = '/dls_sw/i21/scripts/Polarimeter/LVgap50eVReal.csv'
wh = open(write_gap_file, 'w')

for e, gap in energy_gap:
    print e, gap
    dgap=1  
    pos([pgmEnergy, e])
    pos([idscannable, [gap, 'LV', 0]])
    #TODO replace polarimeter diode 'ca02sr' with beamline diode below
    dscan(idgap, -dgap, dgap, 21, ca02sr, 1)
    peak_val = scan_processor.results['peak'].scn.idgap
       
    wh.write(str(e) + ',' + str(peak_val))
  
wh.close()
               
#pos FPSelection 18.43 # through-beam
scan_processing_off()
