from gda.data import PathConstructor

filters= {
	13.75 : "Clear",
	26.25 : "0.05mm Al",
	31.05 : "0.1mm Al",
	35.75 : "0.25mm Al",
	43.10 : "0.5mm Al",
	48.25 : "0.015mm Mo",
	52.75 : "0.05mm Mo",
	59.85: "0.1mm Mo", 
                      }
energyStart = 8.0
energyEnd = 21.0
energyStep=1.0
energyC=energyStart

print "Script started"

positions=filters.keys()
positions.sort()
results=[]

while (energyC <= energyEnd):
	pos energy energyC
	for position in positions:
		filter=filters[position]
		pos d3motor position
		diode = da.getPosition()
		results += [diode]
		print "Energy "+energyC.__str__()+" position "+position.__str__()+", filter "+filter.__str__()+", diode "+diode.__str__()
		
	nResults = len(results)
	file = open(PathConstructor.createFromDefaultProperty()+"filterind3.csv","a")
	file.write("%f ," % (energyC) )
	for i in range(nResults) :
		file.write("%f , " % (results[i]) )
	file.write("\n")
	file.close()
	
	energyC = energyC + energyStep


print "Script done"
