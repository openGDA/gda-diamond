from tomo.tomoAlignment import moveToModule

scanEndt3M1z = 2220

print "Module 1"
moveToModule(1)

pos t3_m1z 220

scan t3_x 1340.22 1353 1 pco 0.05

scan t3_m1z 220 scanEndt3M1z 100 pco 0.05


#At module 2
print "Module 2"
moveToModule(2)

pos t3_m1z 220

scan t3_x 1347.5 1353 0.5 pco 0.5

scan t3_m1z 220 scanEndt3M1z 100 pco 0.5

#At module 3
print "Module 3"
moveToModule(3)

pos t3_m1z 220

scan t3_x 1350 1353 0.25 pco 1

scan t3_m1z 220 scanEndt3M1z 100 pco 1

#At module 4
print "Module 4"
moveToModule(4)

pos t3_m1z 220

scan t3_x 1351.5 1353 0.1 pco 2

scan t3_m1z 220 scanEndt3M1z 100 pco 2


