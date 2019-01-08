from gdaserver import sim_addetector
from gda.device.detector.areadetector.v17 import ImageMode
from gov.aps.jca.dbr import DBRType
from time import sleep

def run_autofocus():
    # Set number of strips to divide the image into
    num_strips = 10

    # Save current settings
    print('Setting up detector & Python plugin')
    detector_ad_base = sim_addetector.getAdBase()
    save_image_mode = detector_ad_base.getImageMode()

    python_plugin = sim_addetector.getNdPython()
    python_plugin_base = python_plugin.getPluginBase()
    save_callbacks_enabled = python_plugin_base.isCallbacksEnabled_RBV()

    # Acquire a single image
    detector_ad_base.setImageModeWait(ImageMode.SINGLE, 500)
    python_plugin_base.enableCallbacks()
    python_plugin.putParam("strips", num_strips)

    detector_ad_base.startAcquiringWait()
    detector_ad_base.stopAcquiring()
    print('Acquired image of size: {0}, {1}, {2}'.format(python_plugin_base.getArraySize0_RBV(), python_plugin_base.getArraySize1_RBV(),python_plugin_base.getArraySize2_RBV()))

    # Get the output (FFT of each strip)
    print('Output: {0}'.format(python_plugin.readParam('output', DBRType.INT)))

    # Restore initial settings
    print('Restoring initial settings')
    detector_ad_base.setImageMode(save_image_mode)
    if not save_callbacks_enabled:
        python_plugin_base.disableCallbacks()
