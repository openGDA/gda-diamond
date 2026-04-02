# By staggering the two fast shutters in time we can get over the limitations of the minimum opening time of one shutter
# We do this using the panda, controlled via Bluesky
from gdascripts.blueskyHandler import run_plan
from time import sleep

MIN_SHUTTER_OPEN_TIME = 5600
MIN_DELAY_BETWEEN_BOTH_OPEN_AND_COLLECTION = 1200

def configure_panda(groups):
	run_plan("configure_panda_triggering", profile={"repeats":1, "groups":groups})
	
def create_single_collection(collection_time_ms, wait_between_collection_ms, trigger="IMMEDIATE"):
	"""Runs a single collection using staggered opening/closing of shutters so that collections can be quicker than
	the minimum amount of time the shutters need to stay open. 
	
	For an explanation of how this works see https://jira.diamond.ac.uk/browse/I22-1469
	"""
	if collection_time_ms > MIN_SHUTTER_OPEN_TIME:
		# If the collection is long we can just open both shutters at the same time
		delay_between_shutters = 0
	else:
		delay_between_shutters = MIN_SHUTTER_OPEN_TIME-collection_time_ms-MIN_DELAY_BETWEEN_BOTH_OPEN_AND_COLLECTION
	
	if trigger != "IMMEDIATE":
		wait_between_collection_ms = 0
	
	default_group =  {"frames":1, "trigger":"IMMEDIATE", "wait_units":"MS", "run_units":"MS"}

	shutter_opens = default_group.copy()
	shutter_opens["trigger"] = trigger
	shutter_opens["wait_time"] = delay_between_shutters
	shutter_opens["wait_pulses"] = [1,0,0,0,0]
	shutter_opens["run_time"] = MIN_DELAY_BETWEEN_BOTH_OPEN_AND_COLLECTION
	shutter_opens["run_pulses"] = [1,1,0,0,0]
	
	collection = default_group.copy()
	collection["wait_time"] = 0
	collection["wait_pulses"] = [1,1,0,0,0]
	collection["run_time"] = collection_time_ms
	collection["run_pulses"] = [1,1,1,1,1]
	
	shutter_closes = default_group.copy()
	shutter_closes["wait_time"] = delay_between_shutters
	shutter_closes["wait_pulses"] = [0,1,0,0,0]
	shutter_closes["run_time"] = wait_between_collection_ms
	shutter_closes["run_pulses"] = [0,0,0,0,0]
	
	return [shutter_opens, collection, shutter_closes]

def collect_on_no_trigger(run_wait_times_ms):
	"""
	Runs arbitrary length data collections with arbitrary wait times between them.
	
	Expects a list of tuples of (run_time, wait_time) with both being in ms.
	
	e.g. to run a collection of 50 ms, then wait a second and run a 100ms collection you can do:
	collect_on_no_trigger([(50, 1000), (100, 0)])
	"""
	groups = []
	for run, wait in run_wait_times_ms:
		groups.extend(create_single_collection(run, wait))
	configure_panda(groups)
	sleep(0.5)
	return run_plan("run_panda_triggering")

def collect_on_ext_trigger(run_times_ms, trigger="BITA_1"):
	"""
	Runs arbitrary length data collections triggered on the specified input.
	
	Expects:
	     run_times_ms: a list of run times in ms
	     trigger: The trigger that we start each collection on, options are:
	         BITA_1: EH Panda TTL In 1 going high
	         BITA_0: EH Panda TTL In 1 going low
	         BITB_1: EH Panda TTL In 2 going high
	         BITB_0: EH Panda TTL In 2 going low
	
	e.g. to wait for a trigger on TTL1, run a collection of 50 ms, then wait for another trigger and run a collection of 100ms:
	collect_on_ext_trigger([50, 100], "BITA_1")
	"""
	groups = []
	for run in run_times_ms:
		groups.extend(create_single_collection(run, 0, trigger))
	configure_panda(groups)
	sleep(0.5)
	return run_plan("run_panda_triggering")

def example_staggered_shutters():
	collections = [(500, 5000), (2000, 5000), (6000, 0)]
	collect_on_no_trigger(collections)
	