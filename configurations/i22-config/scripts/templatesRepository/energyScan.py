title = "Toluene"

samples= []
samples.append(8.0)
samples.append(9.373)
samples.append(9.573)
samples.append(9.673)
samples.append(10.0)

print "Start collecting data"

pos shutter "Open"

energies=samples.keys()
energies.sort()

for e in energies:
    sample=samples[position]
    print "Position "+position.__str__()+" sample "+sample.__str__()
    finder.find("GDAMetadata").setMetadataValue("title", sample.__str__()+", basex "+position.__str__())
    pos basex position
    staticscan ncddetectors
    pause

pos shutter "Close"
pos pxyy 22.89
pos basex 122.2

print "Script done"


pos energy 8.0
staticscan ncddetectors
pos energy 9.373
staticscan ncddetectors
pos energy 9.573
staticscan ncddetectors
pos energy 8.0
staticscan ncddetectors
pos energy 8.0
staticscan ncddetectors

