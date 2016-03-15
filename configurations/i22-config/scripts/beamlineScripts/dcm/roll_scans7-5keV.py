from gda.data import NumTracker
from gda.data import PathConstructor
i22NumTracker = NumTracker("i22");
i22NumTracker.getCurrentFileNumber()

'''
The purpose of this script is to determine Mono roll position that doesn't impart a lateral shift on the beam when changing energy
'''

file = open(PathConstructor.createFromDefaultProperty()+"roll_parameters_7-5keV_"+time.strftime("%Y-%m-%d")+".csv","a")
file.write("File, Roll, edge_position\n")
file.close()


for rollpos in (1000, 750, 500, 250, 0, -250, -500, -750, -1000):
    pos dcm_roll rollpos
    rollposition = dcm_roll.getPosition()
    scan s3_xplus 15 3 0.5 topup d4d1
    go edge
    rscan s3_xplus -2 2 0.02 topup d4d1
    edgePos = edge.result.pos
    pos s3_xplus 15
    fileNumber = int(i22NumTracker.getCurrentFileNumber())
    file = open(PathConstructor.createFromDefaultProperty()+"roll_parameters_7-5keV_"+time.strftime("%Y-%m-%d")+".csv","a")
    file.write("%6.0f, %f, %f\n" % (fileNumber, rollposition, edgePos))
    file.close()

print "All done" 
