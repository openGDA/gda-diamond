print("\nRunning blueapi_control.py")

run 'gdascripts/blueskyHandler.py'

# get blueapi url from BlueskyCOntroller service so we can use it when creating BlueApiControl instance
blueapi_url=ServiceProvider.getService(BlueskyController).getClientBasePathUrl()

from gda.util import BlueApiControl
blueapi_control = BlueApiControl(blueapi_url)

def pretty_print(obj) :
    print(blueapi_control.getPrettyString(obj))

def show_plans() :
    pretty_print(blueapi_control.getPlans())

def show_plan(plan_name) :
    pretty_print(blueapi_control.getPlan(plan_name))

def show_devices() :
    pretty_print(blueapi_control.getDevices())

def show_device(device_name) :
    pretty_print(blueapi_control.getDevice(device_name))