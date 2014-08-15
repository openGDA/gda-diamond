def minimirrors(*pitchdeg):
	'''
	minimirrors(pitchdeg)
	position minimirrors safely to specified pitch (degrees) or zero to remove
	minimirrors() gives current positions and help

	If minimirrors need aligning (if main mirrors have been moved) then:
		minimirrors(0)
		pos m3x 0
		put diode in beam
		scancn ytable .05 81 w .5 diode
		move ytable to edge (intensity goes from high to low in scan)
		(see comments in minimirrors.py for more detailed instructions)
	'''
	'''
	advanced instructions (full alignment)
	-------- ------------ ----------------
	pos m3pitch 0 m4pitch 0
	move m3x negative to hard limit
	move m4x positive to hard limit
	gap between mirrors should be ~ 10 mm
	scan ytable looking at diode and go to centre
	pos ds [.1 4]
	slowly move in m3 till it cuts the beam then scan m3x and go to edge
	scan m3pitch and go to peak
	repeat m3x/m3pitch scans till no changes
	calcibrate m3x and m3pitch to zero
	pos m3x -3 (or as far negative as it will go)
	repeat for m4
	pos m4x +3 (or as far positive as it will go)
	final check: when mninimirrors are in check that ss.x and ds.x are the same (no tilt of beam)
	if not then use ss.x and ss.y to fine calibrate m4pitch	
	'''
	if len(pitchdeg)==0:
		print minimirrors.__doc__
		print 'Current positions:'
		print m3pitch, m4pitch, m3x, m4x
	else:
		pitchdeg=pitchdeg[0]
		mirrorlength=280
		if float(pitchdeg)<-.01:
			raise ValueError('===Pitch should be a positive angle in degrees')
		if float(pitchdeg)>.01:
			print '=== Moving minimirrors in with pitch %.3f degrees' % pitchdeg	
			if m4x()<2:
				print m4x(2)
			if m3x()>-.5:
				print m3x(0)
			pos m3pitch pitchdeg m4pitch pitchdeg
			yoffset=mirrorlength*pitchdeg*pi/180
			print m3x(0)
			print m4x(yoffset)
			print '=== Please type inc base_y %.3f if mirrors were previously out' % yoffset
			print '=== Then check base_y alignment'
		else:		
			print '=== Moving minimirrors out'	
			pitchdeg=m3pitch()
			print m4x(4)
			print m3x(-4)
			pos m3pitch 0 m4pitch 0
			yoffset=mirrorlength*pitchdeg*pi/180
			print '=== Please type inc base_y %.3f if mirrors were previously in' % -yoffset
			print '=== Then check base_y alignment'

