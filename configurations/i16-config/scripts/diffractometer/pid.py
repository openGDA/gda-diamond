#kphi_kp = CAClient('BL16I-MO-DIFF-01:SAMPLE:KPHI:KP'); kphi_kp.configure()
#kphi_ki = CAClient('BL16I-MO-DIFF-01:SAMPLE:KPHI:KI'); kphi_ki.configure()
#kphi_kd = CAClient('BL16I-MO-DIFF-01:SAMPLE:KPHI:KD'); kphi_kd.configure()
#kphi_ks = CAClient('BL16I-MO-DIFF-01:SAMPLE:KPHI:KS'); kphi_ks.configure()
#kphi_proc = CAClient('BL16I-MO-DIFF-01:SAMPLE:KPHI:UPLOAD.PROC'); kphi_proc.configure()

#def kphi_pid(kp, ki, kd, ks):
#    kphi_kp.caput(10, kp)
#    kphi_ki.caput(10, ki)
#    kphi_kd.caput(10, kd)
#    kphi_ks.caput(10, ks)
#    kphi_proc.caput(10, 1)


def caput_wait(pvstring, value):
	cli=CAClient(pvstring)
	cli.configure()
	cli.caput(60, value)
	cli.clearup()


def set_pvs(rootpv, d):
    if bool(int(caget(rootpv + 'PIDDISABLE'))):
        raise Exception('PID configuration is disabled from epics')
        
    for key in d:
        print rootpv + key.upper() + ' --> ' + str(d[key])
        caput_wait(rootpv + key.upper(), d[key])
    print rootpv + 'UPLOAD.PROC' + ' --> 1'
    caput_wait(rootpv + 'UPLOAD.PROC', 1)

def set_pid_phi(d):
    set_pvs('BL16I-MO-DIFF-01:SAMPLE:KPHI:', d)

def set_pid_kappa(d):
    set_pvs('BL16I-MO-DIFF-01:SAMPLE:KAPPA:', d)

def set_pid_ktheta(d):
    set_pvs('BL16I-MO-DIFF-01:SAMPLE:KTHETA:', d)

def set_pid_mu(d):
    set_pvs('BL16I-MO-DIFF-01:SAMPLE:MU:', d)

def set_pid_delta(d):
    set_pvs('BL16I-MO-DIFF-01:SAMPLE:DELTA:', d)

def set_pid_gamma(d):
    set_pvs('BL16I-MO-DIFF-01:SAMPLE:GAMMA:', d)

print "Created: set_pid_phi, set_pid_kappa, set_pid_ktheta, set_pid_mu, set_pid_delta, set_pid_gamma" 
print "   These take a single dictionary arg, e.g.: set_pid_phi('KP': 0)"
print "   !!! Changing these parameters could easily result in damage to the diffractometer or motor controller. RobW !!!"