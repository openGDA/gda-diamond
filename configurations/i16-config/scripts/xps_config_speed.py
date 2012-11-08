def xps_setSpeed(motor,speed):
	mot = finder.find(motor+'_motor')
	mot.setSpeed(speed)

def xps_getSpeed(motor):
	mot = finder.find(motor+'_motor')
	return mot.getSpeed()

# motor must be given as string. e.g.: 'delta'
# usual delta speed: 4
# long detector arm delta speed: 0.5

