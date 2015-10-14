# Script performing EXAfS scan on V, Fe, Cu, Zn, Au, Zr and Mo
 
pitch_start = -11

step_eV = 0.5
range_eV = 120.0

step = step_eV/1000.0
erange = range_eV/1000.0

pos d6filter 'IL Diode VFM' 
pos d4filter 'Scatter Diode'

#V
pos d5motor 27.8
pos energy 5.465

pos finepitch 0
pos pitch pitch_start
rscan finepitch -100 100 0.5 d6d1
inc finepitch -100
go maxval

e1 = 5.465 - erange
e2 = 5.465 + erange
setTitle("Vanadium K EXAFS")
scan energy e1 e2 step topup bragg EPICS_energy d4d2 d6d1 exafs 

#Fe
pos d5motor 49.5
pos energy 7.112

pos finepitch 0
pos pitch pitch_start
rscan finepitch -100 100 0.5 d6d1
inc finepitch -100
go maxval

e1 = 7.112 -erange
e2 = 7.112 + erange
setTitle("Iron K EXAFS")
scan energy e1 e2 step topup bragg EPICS_energy d4d2 d6d1 exafs 

#Cu
pos d5motor 70.8
pos energy 8.9789

pos finepitch 0
pos pitch pitch_start
rscan finepitch -100 100 0.5 d6d1
inc finepitch -100
go maxval

e1 = 8.9789 -erange
e2 = 8.9789 + erange
setTitle("Copper K EXAFS")
scan energy e1 e2 step topup bragg EPICS_energy d4d2 d6d1 exafs 

#Zn
pos d5motor 60.5
pos energy 9.6586

pos finepitch 0
pos pitch pitch_start
rscan finepitch -100 100 0.5 d6d1
inc finepitch -100
go maxval

e1 = 9.6586 -erange
e2 = 9.6586 + erange
setTitle("Zinc K EXAFS")
scan energy e1 e2 step topup bragg EPICS_energy d4d2 d6d1 exafs 

#Au
pos d5motor 39.2
pos energy 11.919

pos finepitch 0
pos pitch pitch_start
rscan finepitch -100 100 0.5 d6d1
inc finepitch -100
go maxval

e1 = 11.919 -erange
e2 = 11.919 + erange
setTitle("Gold L3 EXAFS")
scan energy e1 e2 step topup bragg EPICS_energy d4d2 d6d1 exafs 

#Zr
pos d5motor 6.3
pos energy 17.997

pos finepitch 0
pos pitch pitch_start
rscan finepitch -100 100 0.5 d6d1
inc finepitch -100
go maxval

e1 = 17.997 -erange
e2 = 17.997 + erange
setTitle("Zirconium K EXAFS")
scan energy e1 e2 step topup bragg EPICS_energy d4d2 d6d1 exafs 

#Mo
pos d5motor 17.5
pos energy 19.999

pos finepitch 0
pos pitch pitch_start
rscan finepitch -100 100 0.5 d6d1
inc finepitch -100
go maxval

e1 = 19.999 -erange
e2 = 19.999 + erange
setTitle("Molybdenum K EXAFS")
scan energy e1 e2 step topup bragg EPICS_energy d4d2 d6d1 exafs 

print "Exafs done"

