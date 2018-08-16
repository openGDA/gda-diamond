
## setting the temperature
pos tset 400

for likecake in frange(1.0,-0.2,-0.05 ):#this change temperature by changing the power input 
	pos x20_anout likecake
	for huk in range(0,5,1):
		scancn th2th [0.015 0.03] 101 Tc t 1
		go maxpos
tset.hrange(4)
for huk in range (0,10,1):
	scancn th2th [0.015 0.03] 101 Tc t 1
	go maxpos
tset.hrange(5)
pos x20_anout 1
while (0==0): #infinate loop!!!
	scancn th2th [0.015 0.03] 101 Tc t 1
	go maxpos
