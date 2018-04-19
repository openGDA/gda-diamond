from gda.epics import CAClient

def caput(pv, val):
    CAClient.put(pv, val)

def caget(pv):
    return CAClient.get(pv)

def prep_xsp3():
    """We enable callbacks in the array plugin, then acquire a single frame"""
    from gdaserver import Xspress3A
    caput(Xspress3A.getNdArray().getBasePVName() + "EnableCallbacks", "Enable")
    ad_base_pv = Xspress3A.getAdBase().getBasePVName()
    prev_img_mode = caget(ad_base_pv + "ImageMode")
    mode_changed = prev_img_mode != "Single"
    if (mode_changed):
        caput(ad_base_pv + "ImageMode", "Single")
    caput(ad_base_pv + "Acquire", "Acquire")
    if (mode_changed):
        caput(ad_base_pv + "ImageMode", prev_img_mode)
