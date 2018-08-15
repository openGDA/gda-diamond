"""
This script will set up a run to collect data for a series of capilliaries in a ladder
The centres of the capilliaries need to be scanned first and input into the red values
""""


samples= {  
    23.0 : "xxx",
	27.6 : "a ",
	31.3 : "b ",
	35.5 : "c ",
	39.1 : "d ",
	43.5 : "e ",
	47.2 : "f ",
	51.5 : "g ",
	54.2 : "h ",
	59.3 : "i ",
	63.2 : "j ",
	67.5 : "k ",
	71.3 : "l ",
	75.5 : "m ",
	79.0 : "n ",
	83.5 : "o ",
	87.2 : "p ",                       }

temperatures= {  
    90.0 : "90 K",
    100.0 : "100 K"
    110.0 : "110 K"
    120.0 : "120 K"
    130.0 : "130 K"
    140.0 : "140 K"
    150.0 : "150 K"
    160.0 : "160 K"
    170.0 : "170 K"
    180.0 : "180 K"
    190.0 : "190 K"
    200.0 : "200 K"
    210.0 : "210 K"
    220.0 : "220 K"
    230.0 : "230 K"
    240.0 : "240 K"
    250.0 : "250 K"
    260.0 : "260 K"
    270.0 : "270 K"
    280.0 : "280 K"
    290.0 : "290 K"
    300.0 : "300 K"}

print "Start collecting data"

positions=samples.keys()
positions.sort()

temperatures=temperatures.keys()
temperatures.sort()

for position in positions:
	sample=samples[position]
	print "Position "+position.__str__()+" sample "+sample.__str__()
    for temperature in temperatures:
        temperature=temperatures[temperature]
        print "Temperature "+temperature.__str__()+" K"
        pos pxyy(position)
        pos cryojet(temperature)
        cryojet.wait(3600, 10)
        finder.find("GDAMetadata").setMetadataValue("title", sample.__str__()+", pxyy "+position.__str__()+", Temperature "+temperature.__str__()+" K")
	scan pxyy position position 1 ncddetectors
	pause

print "Script done"

