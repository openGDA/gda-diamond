from gda.device.detector.areadetector.v17 import ImageMode
from gov.aps.jca.dbr import DBRType
from gda.configuration.properties import LocalProperties

def run_autofocus(detector):
    # Set number of strips to divide the image into
    num_strips = 10

    # Save current settings
    print('Setting up detector & Python plugin')
    detector_ad_base = detector.getAdBase()
    save_image_mode = detector_ad_base.getImageMode()
    save_colour_mode = detector_ad_base.getColorMode()

    python_plugin = detector.getNdPython()
    python_plugin_base = python_plugin.getPluginBase()
    save_callbacks_enabled = python_plugin_base.isCallbacksEnabled_RBV()

    # Load script into Python plugin
    config_dir = LocalProperties.get(LocalProperties.GDA_CONFIG)
    script_filename = config_dir + "/scripts/autofocus/fft_process.py"
    class_name = "FftProcess"

    print("Loading class {} from file {}".format(class_name, script_filename))
    python_plugin.setFilename(script_filename)
    python_plugin.setClassname(class_name)
    python_plugin.readFile()

    # Acquire a single image
    detector_ad_base.setImageModeWait(ImageMode.SINGLE, 500)
    detector_ad_base.setColorMode(0)
    python_plugin_base.enableCallbacks()
    python_plugin.putParam("strips", num_strips)

    detector_ad_base.startAcquiringWait()
    detector_ad_base.stopAcquiring()
    print('Acquired image of size: {}, {}, {}'.format(python_plugin_base.getArraySize0_RBV(), python_plugin_base.getArraySize1_RBV(), python_plugin_base.getArraySize2_RBV()))

    # Get the output (FFT of each strip)
    print('Output: {}'.format(python_plugin.readParam('output', DBRType.INT)))

    # Restore initial settings
    print('Restoring initial settings')
    detector_ad_base.setImageMode(save_image_mode)
    detector_ad_base.setColorMode(save_colour_mode)
    if not save_callbacks_enabled:
        python_plugin_base.disableCallbacks()
