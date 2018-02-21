#def poms_default_vmag(name):
#    from poms.PomsSocketDevice import PomsSocketDeviceClass
#    return PomsSocketDeviceClass(name, hostName='172.23.110.198', hostPort=4042)

def poms_default_vflipper(name):
    from poms.PomsVflipper import FlipperDeviceClass
    return FlipperDeviceClass(name, nameMagnet='vmag',
        nameCounterTimerA='macr19',
        nameCounterTimerB='macr16', nameCounterTimerC='macr18');

def poms_default_vflipper_calc(name):
    from poms.PomsVflipperCalc import FlipperCalcDeviceClass
    return FlipperCalcDeviceClass(name, nameMagnet='vmag',
        nameCounterTimerA='macr19',
        nameCounterTimerB='macr16', nameCounterTimerC='macr18',
        nameCounterTimerD='macr20', nameCounterTimerE='macr1',
        nameCalc1='EDIF', calc1='B2/A2-B1/A1',
        nameCalc2='X2',   calc2='B2/A2+B1/A1',
        nameCalc3='EXAS', calc3='Q2/2.0',
        nameCalc4='TDIF', calc4='C1/A1-C2/A2',
        nameCalc5='X5',   calc5='C1/A1+C2/A2',
        nameCalc6='TXAS', calc6='Q5/2.0')

def poms_default_vflipper_raw(name):
    from poms.PomsVflipperRaw import FlipperRawDeviceClass
    return FlipperRawDeviceClass(name, 'vmag',
        nameCounterTimerA='macr1',  nameCounterTimerB='macr10',
        nameCounterTimerC='macr11', nameCounterTimerD='macr31',
        nameCounterTimerE='macr23'); # 20130618


#print "Note: Use object name 'vmag' for the POMS magenet control";
##vmag = PomsSocketDeviceClass('vmag','172.23.106.195', 4042 );
#vmag = PomsSocketDeviceClass('vmag','172.23.110.195', 4042 );

#print "Note: Use object name 'vflipper' for flipping magenet on POMS";
##vflipper = FlipperDeviceClass('vflipper', 'vmag', 'ca31sr', 'ca32sr', 'ca33sr');
#vflipper = FlipperDeviceClass('vflipper', 'vmag', 'mac116', 'mac117', 'mac118');

