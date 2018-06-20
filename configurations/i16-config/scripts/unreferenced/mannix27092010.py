# First scan number 159428
#for tempset in frange(140,10,1):
#	pos tset tempset 
#	while abs(tempset-Ta()) > 0.5:
#		w(20)
#	while abs(tempset-Ta()) > 0.5:
#		w(20)
# 		print Ta	
#	scan x 1 2 1 Ta Tb tim keith
#pos tset 160
#scan x 1 1300 1 w 1 Ta Tb Tc tim keith
#pos tset 10
#scan x 1 1300 1 w 1 Ta Tb Tc tim keith

#scan hkl [xx[0]-0.2,xx[1]-0.2,xx[2]-0.2] [xx[0]+0.2,xx[1]+0.2,xx[2]+0.2] [0.001,0.001,0.001] t 1
# 4.0036 k: 4.0041 l: 4.0024
#scan hkl [4.0036-0.2,4.0041-0.2,4.0024-0.2] [4.0036+0.2,4.0041+0.2,4.0024+0.2] [0.001,0.001,0.001] t 1

def lastnight():
#	pos hkl [4,4,1]
	#lineup()
	zz=hkl()
	pos hv 0
	scan hkl [zz[0]-0.04,zz[1]-0.04,zz[2]-0.04] [zz[0]+0.04,zz[1]+0.04,zz[2]+0.04] [0.001,0.001,0.001] t 30 
	pos hv 1
	scan hkl [zz[0]-0.04,zz[1]-0.04,zz[2]-0.04] [zz[0]+0.04,zz[1]+0.04,zz[2]+0.04] [0.001,0.001,0.001] t 30 
	pos hv -1
	scan hkl [zz[0]-0.04,zz[1]-0.04,zz[2]-0.04] [zz[0]+0.04,zz[1]+0.04,zz[2]+0.04] [0.001,0.001,0.001] t 30 
	pos tset 50
	w(600)
	lineup()
	zx=hkl()
	pos hv 0
	scan hkl [zx[0]-0.04,zx[1]-0.04,zx[2]-0.04] [zx[0]+0.04,zx[1]+0.04,zx[2]+0.04] [0.001,0.001,0.001] t 30 
	pos hv 1
	scan hkl [zx[0]-0.04,zx[1]-0.04,zx[2]-0.04] [zx[0]+0.04,zx[1]+0.04,zx[2]+0.04] [0.001,0.001,0.001] t 30 
	pos hv -1
	scan hkl [zx[0]-0.04,zx[1]-0.04,zx[2]-0.04] [zx[0]+0.04,zx[1]+0.04,zx[2]+0.04] [0.001,0.001,0.001] t 30 
	