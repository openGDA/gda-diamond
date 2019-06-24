from gda.epics import CAClient

choprot_PV_JVEL=CAClient("BL06J-MO-CHOP-01:ROT.JVEL");
choprot_PV_JOGF=CAClient("BL06J-MO-CHOP-01:ROT.JOGF");
choprot_PV_JVEL.configure();
choprot_PV_JOGF.configure();

def choprot_run(velocity):
    choprot_PV_JVEL.caput(velocity);
    choprot_PV_JOGF.caput(1);

def choprot_stop():
    choprot_PV_JOGF.caput(0);

def choprot_speed():
    choprot_PV_JVEL.caget();