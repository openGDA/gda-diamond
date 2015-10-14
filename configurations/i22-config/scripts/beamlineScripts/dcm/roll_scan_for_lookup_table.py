from gda.data import NumTracker
from gda.data import PathConstructor
i22NumTracker = NumTracker("i22");
i22NumTracker.getCurrentFileNumber()

'''
The purpose of this script is to determine Mono roll position that doesn't impart a lateral shift on the beam when changing energy
'''

file = open(PathConstructor.createFromDefaultProperty()+"roll_parameters_"+time.strftime("%Y-%m-%d")+".csv","a")
file.write("File, Energy , Roll, edge_position\n")
file.close()

for energyPos in (7.5, 15.0):
    pos energy energyPos
    pos finepitch 0
    pos pitch 0 #this is a value that is close to the optimum pitch position at 12.4keV currently 
    scan finepitch -150 150 0.5 topup d4d1
    go maxval
    
    for rollpos in (1000, 750, 500, 250, 0, -250, -500, -750, -1000):
        pos roll rollpos
        rollposition = roll.getPosition()
        scan s3_xplus 15 3 0.5 topup d4d1
        go edge
        rscan s3_xplus -2 2 0.02 topup d4d1
        edgePos = edge.result.pos
        pos s3_xplus 15
        fileNumber = int(i22NumTracker.getCurrentFileNumber())
        file = open(PathConstructor.createFromDefaultProperty()+"roll_parameters_"+time.strftime("%Y-%m-%d")+".csv","a")
        file.write("%6.0f, %f , %f, %f\n" % (fileNumber, energyPos, rollposition, edgePos))
        file.close()

print "All done" 
