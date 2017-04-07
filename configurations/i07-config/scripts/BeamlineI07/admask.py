import scisoftpy as dnp

from gda.epics import CAClient

class ADMaskWrapper():
    def __init__(self, cam_pv, arr_pv, arr_port, mask_location):
        self.acq_pv = CAClient(cam_pv + ":Acquire"); self.acq_pv.configure()
        self.exposure_pv = CAClient(cam_pv + ":AcquireTime"); self.exposure_pv.configure()
        self.array_pv = CAClient(arr_pv + ":ArrayData"); self.array_pv.configure()
        self.arr_input_pv = CAClient(arr_pv + ":NDArrayPort"); self.arr_input_pv.configure()
        self.arr_callbacks_pv = CAClient(arr_pv + ":EnableCallbacks"); self.arr_callbacks_pv.configure()
        self.dim0_pv = CAClient(arr_pv + ":ArraySize0_RBV"); self.dim0_pv.configure()
        self.dim1_pv = CAClient(arr_pv + ":ArraySize1_RBV"); self.dim1_pv.configure()
        self.arr_port = arr_port
        self.mask_location = mask_location

    def create_mask(self, low_clip = 0, high_clip=0x7fffffff):
        # record original values
        o_arr_port, o_exposure, o_callbacks = None, None, None
        try:
            o_arr_port = self.arr_input_pv.caget()
            o_exposure = self.exposure_pv.caget()
            o_callbacks = self.arr_callbacks_pv.caget()
            # configure required plugins
            self.arr_input_pv.caput(self.arr_port)
            self.exposure_pv.caput(0.5)
            self.arr_callbacks_pv.caput(1)
            # acquire frame
            self.acq_pv.caputWait(1)
            # restore state
        finally:
            if o_arr_port:
                self.arr_input_pv.caput(o_arr_port)
            if o_exposure:
                self.exposure_pv.caput(o_exposure)
            if o_callbacks:
                self.arr_callbacks_pv.caput(o_callbacks)

        xsize, ysize = int(self.dim0_pv.caget()), int(self.dim1_pv.caget())
        data = self.array_pv.cagetArrayInt(xsize * ysize)
        data = dnp.array(data)
        mask = (low_clip <= data) & (data <= high_clip)
        mask.shape = (ysize, xsize)
        dnp.io.save(self.mask_location, mask.astype(dnp.int32), "npy")
