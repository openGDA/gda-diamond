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

        # set trigger mode to software
        prev_trigger_mode = caget(ad_base_pv + "TriggerMode")
        trigger_mode_changed = prev_trigger_mode != "Software"
        if (trigger_mode_changed):
                caput(ad_base_pv + "TriggerMode", "Software")

        # Set number of images to 1
        prev_num_images = caget(ad_base_pv + "NumImages_RBV")
        num_images_changed = prev_num_images != 1
        if num_images_changed:
                caput(ad_base_pv + "NumImages", 1)

        # acquire single frame
        caput(ad_base_pv + "Acquire", "Acquire")

        # restore trigger and image mode if necessary
        if (trigger_mode_changed):
                caput(ad_base_pv + "TriggerMode", prev_trigger_mode)
        if (num_images_changed):
                caput(ad_base_pv + "NumImages", prev_num_images)