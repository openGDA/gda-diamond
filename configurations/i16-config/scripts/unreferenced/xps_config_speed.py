from gda.factory import Finder

def xps_setSpeed(motor,speed):
	mot = Finder.find(motor+'_motor')
	mot.setSpeed(speed)

def xps_getSpeed(motor):
	mot = Finder.find(motor+'_motor')
	return mot.getSpeed()

# motor must be given as string. e.g.: 'delta'
# usual delta speed: 4
# long detector arm delta speed: 0.5

