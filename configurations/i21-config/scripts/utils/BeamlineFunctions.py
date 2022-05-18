# Define a list of useful functions for beamline control

import __main__ as gdamain  # @UnresolvedImport
import sys
from time import gmtime, strftime
import os
import cPickle as pickle
from gda.factory import Finder
from gda.configuration.properties import LocalProperties
from gda.util import ElogEntry
from gda.data.metadata import GDAMetadataProvider
from gda.jython.commands import GeneralCommands
from gda.jython import JythonServerFacade
from gda.jython import InterfaceProvider
from utils.ScriptLogger import ScriptLoggerClass

logger = ScriptLoggerClass()


class BeamlineFunctionClass(object):
	ELOG_IDs = {  # beamline_name: log book ID
			'i06': 'BLI06',
			'i06-1': 'BLI06-1',
			'i06-2': 'BLI06-2',
			'i10': 'BLI10',
			'i21': 'BLI21',
			'i09': 'BLI09',
			'i09-1': 'BLI09-1',
			'i09-2': 'BLI09-2',
			'i05': 'BLI05',
			'i05-1': 'BLI05-1',
			'b07': 'BLB07-2',
			'b07-1': 'BLB07-1'
			}
	
	def __init__(self, beamline_name=None):
		self.set_beamline_name(beamline_name)
			
		self.nsh = vars(gdamain);

		self.cs = self.nsh['command_server'];
		self.pickle_file_name = '/dls_sw/' + beamline_name + '/software/gda_versions/var/defaultList.txt';

	def set_beamline_name(self, beamline_name):
		if beamline_name in BeamlineFunctionClass.ELOG_IDs.keys():
			self.beamline_name = beamline_name;
			self.elog_id = BeamlineFunctionClass.ELOG_IDs[beamline_name];

	def swap(self, a, b):
		return b, a
	
	def get_scan_number(self):
		'''get current scan number
		'''
		from gda.data import NumTracker
		nt = NumTracker(self.beamline_name)
		scan_number = nt.getCurrentFileNumber();
		del nt;
		return scan_number
	
	def inc_scan_number(self):
		'''increment scan number by 1
		'''
		from gda.data import NumTracker
		nt = NumTracker(self.beamline_name)
		nt.incrementNumber();
		del nt;
	
	# To setup an 'interruptable()' function which can be used to make for-loop interruptable in GDA."
	# To use this, place 'interruptable()' call as the 1st or last line inside a for-loop."
	def interruptable(self):
		'''check for interrupt, add this in a loop to ensure the loop can be interrupted.
		'''
		GeneralCommands.pause()
	
	def remove_devices(self, name_list):
		''' remove all devices from the give list
		'''
		exec("try:\n	del " + ', '.join(name_list) + "\nexcept:\n	pass;\n")
	
	def get_device(self, device_name):
		'''return device from jython namespace
		'''
		return JythonServerFacade.getInstance().getFromJythonNamespace(device_name)
	
	def is_default_deive(self, device_name):
		'''check if a given device name in the default list in GDA
		'''
		device = self.get_device(device_name)
		if device is None:
			print("device %s does not exist" % device_name)
			return False
			
		default_list = self.cs.getDefaultScannables()
		return device in default_list
	
	def remove_defaults(self, name_list):
		'''remove all devices in the given list from GDA server default list
		'''
		for device_name in name_list:
			self.cs.removeDefault(self.nsh[device_name])

	def pickle_it(self, pickle_file_name, content):
		try:
			out_stream = file(pickle_file_name, 'wb')
			pickle.dump(content, out_stream)
			out_stream.close()
		except IOError:
			print("IOError: Can not preserve the content.")
		
	def restore_it(self, pickle_file_name):
		content = None
		try:
			in_stream = file(pickle_file_name, 'rb')
			content = pickle.load(in_stream)
			in_stream.close()
		except IOError:
			print("IOError: Can not restore the pickled content.")
		return content;
		
	def backup_defaults(self):
		'''manually back-up current GDA default scannable list into a cached file
		'''
		default_list = []
		default_list.extend(self.get_default_scannable_names())
		self.pickle_it(self.pickle_file_name, default_list)
			
	def get_default_scannable_names(self):
		'''return scannable names in the GDA default scannable list
		'''
		scannables = self.cs.getDefaultScannables()
		default_scannable_names = []
		for each in scannables:
			default_scannable_names.append(each.getName())
		return default_scannable_names
		
	def restore_defaults(self):
		'''Restore GDA's default scannable list from cached file.
		'''	
		fileconetent = self.restore_it(self.pickle_file_name);
	
		if fileconetent is None:
			print("Nothing to restore")
			return
		
		for device_name in fileconetent:
			self.cs.addDefault(self.nsh[device_name])
	
	def get_last_terminal_command(self):
		'''return last terminal command from history 
		'''
		jsf = JythonServerFacade.getInstance()
		
		history_file_path = LocalProperties.get("gda.jythonTerminal.commandHistory.path", jsf.getDefaultScriptProjectFolder());
		history_file_name = os.path.join(history_file_path, ".cmdHistory.txt")
		
		if not os.path.exists(history_file_name):
			print("No history found")
			str_cmd = ''
		else:
			with open(history_file_name,'r') as history_file:
				str_cmd=(history_file.readlines())[-1]			
		return str_cmd
	
	def get_last_scan_point(self):
		'''return last scan data point
		'''
		jsf = JythonServerFacade.getInstance()
		lsdp = jsf.getLastScanDataPoint()
		return lsdp

	def get_last_scan_command(self):
		'''return last scan command used
		'''
		lsdp = self.get_last_scan_point()
		str_cmd = lsdp.getCommand()
		return str_cmd

	def get_last_scan_file(self):
		'''return last scan file URI
		'''
		lsdp = self.get_last_scan_point()
		last_scan_file = lsdp.getCurrentFilename()
		return last_scan_file
		
	def set_sub_dir(self, new_sub_dir_name):
		'''set sub-directory where data to be save to
		'''
		sd = Finder.find("subdirectory")
		sd.setValue(str(new_sub_dir_name))
		print("New data path: %s" % (self.get_data_path()))

	def set_terminal_logger(self, new_logger_name="gda_terminal.log"):
		'''set terminal logger file name
		'''
		terminal_logger_path = InterfaceProvider.getPathConstructor().createFromDefaultProperty()		
		tl_file = os.path.join(terminal_logger_path, new_logger_name)
		tlpp = Finder.find("terminallog_path_provider")
		tlpp.setTemplate(str(tl_file))

	def get_data_path(self):
		'''return data path where collected data to be stored under
		'''
		data_path = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
		return data_path
	
	def register_for_path_update(self, observer_object):
		observable_subdirectory = Finder.find("observable_subdirectory");
		observable_subdirectory.addIObserver(observer_object);
		
	def set_title(self, title):
		GDAMetadataProvider.getInstance().setMetadataValue("title", title)
	
	def get_title(self):
		return GDAMetadataProvider.getInstance().getMetadataValue("title")
	
	def set_visit(self, visit):
		'''set visit ID.
		'''
		oldvisit = GDAMetadataProvider.getInstance().getMetadataValue("visit")
		GDAMetadataProvider.getInstance().setMetadataValue("visit", visit)
	
		user = GDAMetadataProvider.getInstance().getMetadataValue("federalid")
		if "user" in user:  # to get rid of the beamline user account  "ixxuser"
			log_title = "visit changed"
			log_content = "visit manually changed from %s to %s by %s" % (oldvisit, visit, user)
			if self.elog_post(log_title, log_content):
				logger.simple_log("Changes logged in eLog"); 
			else:
				logger.simple_log("eLog failed"); 
	
	def get_visit(self):
		'''return current visit ID
		'''
		return GDAMetadataProvider.getInstance().getMetadataValue("visit")
		
	def elog_post(self, log_title, log_content):
		'''post entry to elog database
		'''
		log_user_id = "gda"  # The user ID e.g. epics or gda or abc12345 
		visit = self.get_visit()  # The visit number;
		log_id = self.elog_id  # The logbook ID, such as BLI07
		log_group_id = log_id + "-USER"
		# Since GroupIDs are limited to 10 characters, I06-1 had to be a special case:
		if "-" in log_id:
			log_group_id = log_id + "-UE" #'UE' Stands for User Experiment
		try:
			ElogEntry(log_title, log_user_id, visit, log_id, log_group_id).addHtml(log_content).post()
		except:
			exception_type, exception, traceback = sys.exc_info()
			print("eLog post failed.")
			logger.dump("---> ", exception_type, exception, traceback)
			return False
		return True

	def get_current_time(self):
		'''return GM time
		'''
		ct = strftime("%Y-%m-%d %H:%M:%S", gmtime());
		return ct
		
	def log_scan(self, time_of_scan, formated_extra_info):
		'''log scan information to elog entry
		'''
		scan_number = self.get_scan_number();	
		log_title = "scan " + str(scan_number);
		log_content = '<table style="border:1px solid black;border-collapse:collapse;"><tbody>'
		log_content += '<tr><th colspan="2" style="color: rgb(0,51,102);">Automatic scan logging</th></tr>'
		log_content += '<tr style="border:1px solid black;"><td style="border:1px solid black;">Time</td><td>%s</td></tr>' % (time_of_scan)
		log_content += '<tr style="border:1px solid black;"><td style="border:1px solid black;">Command</td><td>%s</td></tr>' % (self.get_last_scan_command())
		log_content += '<tr style="border:1px solid black;"><td style="border:1px solid black;">Data File</td><td>%s</td></tr>' % (self.get_last_scan_file())
		log_content += '<tr style="border:1px solid black;"><td style="border:1px solid black;" width=60><p>Beamline Parameters</p></td><td>%s</td></tr>' % (formated_extra_info)
		log_content += '</tbody></table>'
		
		if self.elog_post(log_title, log_content):
			logger.simple_log("Scan %d posted to ELog." % (scan_number))


	def stop_archiving(self):
		'''remove file archiving from data writer
		'''
		ddwf = Finder.find("DefaultDataWriterFactory");
		fr = Finder.find("file_registrar")
		ddwf.removeDataWriterExtender(fr);
		
	def restore_archiving(self):
		'''restore file archiving in data writer
		'''
		ddwf = Finder.find("DefaultDataWriterFactory");
		fr = Finder.find("file_registrar")
		ddwf.addDataWriterExtender(fr);

	def register_file_for_archiving(self, file_name):
		'''register the named file for archiving
		'''
		fr = Finder.find("file_registrar")
		if os.path.exists(file_name) and os.path.isfile(file_name):
			fr.registerFile(file_name);
		else:
			print("%s is either not exist or it is not a file" % file_name)

