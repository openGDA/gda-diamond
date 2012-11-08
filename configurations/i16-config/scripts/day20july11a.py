#look for phase plate glitches

#ppb111
for energy in frange(3.5,7,.1):
	pos ppx 22 energy enval
	harmonic=9
	if energy<10:
		harmonic=7
	if energy<7:
		harmonic=5
	if energy<4:
		harmonic=3
	pos uharmonic harmonic
	scancn idgap .005 11 w .5 diode
	go maxpos
	pos ppx 28 ppb111 [en() 0]
	scancn ppth .01 81 w .5 diode

#ppa111, ppa220
for energy in frange(6,12,.1):
	pos ppx 22 energy enval
	harmonic=9
	if energy<10:
		harmonic=7
	if energy<7:
		harmonic=5
	if energy<4:
		harmonic=3
	pos uharmonic harmonic
	scancn idgap .005 11 w .5 diode
	go maxpos
	pos ppx 14 ppa111 [en() 0]
	scancn ppth .01 81 w .5 diode
	pos ppx 14 ppa220 [en() 0]
	scancn ppth .01 81 w .5 diode