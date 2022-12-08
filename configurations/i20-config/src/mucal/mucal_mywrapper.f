	program mucal_mywrapper
c	===uses ,mucal.f,atoms_util.for upcase.f==
c	== note this is the very basic interface to the mucal routine
c	== for a smore complex one please look at mymucalxxx.f



c	=====common=========================================
	logical errorflag
	integer errorcode,n_specie
	real energia
	real risult_x(10),risult_ene(9),risult_fluo(4),stechio(50)
	integer zeta(50)
	real cellvolume
	common/dati/energia,risult_x,risult_ene,risult_fluo,
     1	abstot,zeta,stechio,n_specie,cellvolume
c	======================================================



c	====funzioni========
c	character*2 lab_at
c	=================
	


c	note      subroutine mucal(en,mane,z,unit,xsec,energy,fly,erf,er)
c	INTRODUCTION
c	
c	
c		Mucal is a fortran subroutine that calculates and supplies xray
c	        properties of materials. It uses the coefficients listed in ref.
c	        (1) to calculate the crosssections.
c	
c	USAGE
c	
c		To call the subroutine use:
c	
c	      call mucal(en,name,z,unit,xsec,energy,fly,erf,er)
c	
c	where,
c	
c	variable	description
c	--------	-----------------------------------------------
c	en		Energy at which x-section to be calculated.  Real.
c	
c	name		Name of material. Character of length 2.
c	
c	z		Atomic number of material. Integer.
c	
c	unit		Unit to be used for x-sections. Character of length 1.
c	
c	xsec		Array of x-sections. Real, 10 elements.
c	xsec(1)		Photoelectric x-section 
c	xsec(2)		Coherent x-section	
c	xsec(3)		Incoherent x-section 
c	xsec(4)		Total x-section         
c	xsec(5)		Conversion factor       
c	xsec(6)		Absorption coefficient  
c	xsec(7)		Atomic weight           
c	xsec(8)		Density                 
c	xsec(9)		l2-edge jump            
c	xsec(10)	l3-edge jump            
c	
c	energy		Various edge energies. Real, 9 elements
c	energy(1)	k-edge energy  
c	energy(2)	l1-edge energy 
c	energy(3)	l2-edge energy 
c	energy(4)	l3-edge energy 
c	energy(5)	m-edge energy  
c	energy(6)	k-alpha1       
c	energy(7)	k-beta1        
c	energy(8)	l-alpha1       
c	energy(9)	l-beta1
c	
c	fly		Fluorescence yield. Real, 4 elements
c	fly(1)		k fluorescence yield  
c	fly(2)		l1 fluorescence yield 
c	fly(3)		l2 fluorescence yield 
c	fly(4)		l3 fluorescence yield 
c	
c	erf		error flag, logical.
c	
c	er	error code. integer. it can have the following values.
c	1	energy input is zero                                
c	2	name does not match supplied z                        
c	3	no documentation for given element (z<94)           
c	4	no documentation for given element (z>94)           
c	5	l-edge calculation may be wrong for z<30 as mcmaster uses
c	 	l1 only
c	6	energy in the middle of edge
c	7	no name or z supplied       
c	
c	
c	NOTES:
c	
c	en		en > 0 for x-sections and en < 0 for edge energy
c	name		if both name and z supplied they should match
c	z		if both name and z supplied they should match
c	unit		unit=c => cm^2/gm; unit=b => barns/atom
c	conversion	barns/atom = (conversion factor) * (cm^2/g)
c	factor	  
c#################################################################

	character c,unita 
	character*2 def_name
	real energy_in
	real energies (9),xsec(10)
	real fluo_yield(4)
	logical error_flag
	integer error_code
	integer z
c	############################################################

	write (*,*) '----------------------------------------------------'
	write (*,*) 'mucal_mywrapper                   GC 12.05.2009'
	write (*,*) 'system interface to the mucal routine'
	write (*,*) '----------------------------------------------------'



c	set default values
		unita='c' 
c	density is expected to be in cm2/g
		def_name='  '
c	default name not given, atomic number instead
	write(*,*)'Energy (keV) and element Z:'
	read (*,*) energy_in,z
	error_flag=(1.eq.1)
c	##means please printout error message if any##
	error_code=0
c	#must initialize error_code externally too

	call mucal(energy_in,def_name,z,unita,xsec,energies,fluo_yield,
     1		error_flag,error_code)
	write (*,*) error_flag,error_code

c	if (error_flag) then
c		write(*,*)'Error:',error_code
c	else
		write(*,*)	'xsec ----abssunits: cm2/g'		
		write(*,*)	'Photoelectric x-section ', xsec(1)
		write(*,*)	'Coherent x-section      ', xsec(2)	
		write(*,*)	'Incoherent x-section    ', xsec(3)
		write(*,*)	'Total x-section         ', xsec(4)
		write(*,*)	'Conversion factor       ', xsec(5)
		write(*,*)	'Absorption coefficient  ', xsec(6)
		write(*,*)	'Atomic weight           ', xsec(7)           
		write(*,*)	'Density                 ', xsec(8)            
		write(*,*)	'l2-edge jump            ', xsec(9)            
		write(*,*)	'l3-edge jump            ', xsec(10)   
		write(*,*)'Edge Energies',(energies(i),i=1,9)
c	end if
	stop
	end

c	+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



