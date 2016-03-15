"""
This script will set up a run to collect data for a series of capillaries in a ladder
The centres of the capillaries need to be scanned first and input as the red values to the left of the colon
Capillary diameters/sample thickness need to be determined and input as the red values inside parentheses (default 1.0) 
""""


capillaries = {  
    	23.0 : ("xxx", 1.0),
	27.6 : ("a ", 1.0),
	31.3 : ("b ", 1.0),
	35.5 : ("c ", 1.0),
	39.1 : ("d ", 1.0),
	43.5 : ("e ", 1.0),
	47.2 : ("f ", 1.0),
	51.5 : ("g ", 1.0),
	54.2 : ("h ", 1.0),
	59.3 : ("i ", 1.0),
	63.2 : ("j ", 1.0),
	67.5 : ("k ", 1.0),
	71.3 : ("l ", 1.0),
	75.5 : ("m ", 1.0),
	79.0 : ("n ", 1.0),
	83.5 : ("o ", 1.0),
	87.2 : ("p ", 1.0)
              		         }

print "Start collecting data"

positions=capillaries.keys()
positions.sort()

for position in positions:
	sample=capillaries[position][0]
    sample_thickness(capillaries[position][1])
	print "Position "+position.__str__()+" sample "+sample.__str__()
	setTitle(sample.__str__()+", pxyy "+position.__str__()+", sample thickness "+sample_thickness.__str__())
	pos pxy_y position
    staticscan ncddetectors
	
print "Script done"

