
import scisoftpy as dnp
import shutil
import glob
import os

# change the folder path according to your file location
HISTORIC_FILES_PATH = "/dls/science/groups/i22/idgap_scans/historic_files/"
FOLDER_PATH = "/dls/science/groups/I22/idgap scans/"
IDGAP_SCAN_PLOT = "IDGap Scan"

def read_plot_values(file_num=None):	
	files = sorted(os.listdir(HISTORIC_FILES_PATH), key=lambda f: os.path.getctime(HISTORIC_FILES_PATH+f), reverse=True)
	for file_name in files:
		#file_name = files[i][len(HISTORIC_FILES_PATH):]
		print 'Plot file name : {}'.format(file_name)
		nexus_data=dnp.io.load(file_name)
		x = nexus_data.entry1.default.gap[...]
		if hasattr(nexus_data.entry1.default, 'd4d1'):
			y = nexus_data.entry1.default.d4d1[...]
		elif hasattr(nexus_data.entry1.default, 'd6d1'):
			y = nexus_data.entry1.default.d6d1[...]
		else:
			y = nexus_data.entry1.default.qbpm0_total[...]
		for xi, yi in zip(x, y):
			if len(str(xi)) < 6:
				print 'X {}\t\t Y {}'.format(xi, yi)
			else:
				print 'X {}\t Y {}'.format(xi, yi)

def plot_all_files(file_num=None):
	dnp.plot.clear(name='IDGap Scan')	
	if file_num is None:
		return False
	files = sorted(os.listdir(HISTORIC_FILES_PATH), key=lambda f: os.path.getctime(HISTORIC_FILES_PATH+f), reverse=True)
	nexus_ref_data=dnp.io.load(HISTORIC_FILES_PATH+"i22-{}.nxs".format(file_num))
	if hasattr(nexus_ref_data.entry1.default, 'd4d1'):
		y_ref = nexus_ref_data.entry1.default.d4d1[...]
	elif hasattr(nexus_ref_data.entry1.default, 'd6d1'):
		y_ref = nexus_ref_data.entry1.default.d6d1[...]
	else:
		y_ref = nexus_ref_data.entry1.default.qbpm0_total[...]
	for file in files:
		file = file[len(HISTORIC_FILES_PATH):]
		nexus_data=dnp.io.load(file)
		x = nexus_data.entry1.default.gap[...]
		if hasattr(nexus_data.entry1.default, 'd4d1'):
			y = nexus_data.entry1.default.d4d1[...]
		elif hasattr(nexus_data.entry1.default, 'd6d1'):
			y = nexus_data.entry1.default.d6d1[...]
		else:
			y = nexus_data.entry1.default.qbpm0_total[...]
		offset = (- y[0])
		max_y= y.max() + offset
		y= (y + offset) * y_ref.max()/max_y
		if files[0] == file:
			dnp.plot.line(x, (y, file), 'All Files', name=IDGAP_SCAN_PLOT)
		else:
			dnp.plot.addline(x, (y, file), 'All Files', name=IDGAP_SCAN_PLOT)
		print 'Plot file : {}'.format(file)

def store_latest_scanfile():	
	current_scan_file = lastScanDataPoint().currentFilename
	shutil.copy2( current_scan_file, FOLDER_PATH )
	print "Stored current scan file {} ".format(current_scan_file)

def compare_idgap_scanfiles(file_num=None):
	files_path = os.path.join(FOLDER_PATH, '*')
	files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True)
	current_data = dnp.io.load(files[0])
	print "Retrieved current scan file {} ".format(files[0])
	crr_file_name = files[0][len(FOLDER_PATH):]
	crr_x = current_data['entry1']['default']['gap'][...]
	crr_y = []
	if hasattr(current_data.entry1.default, 'd4d1'):
		crr_y = current_data.entry1.default.d4d1[...]
	elif hasattr(current_data.entry1.default, 'd6d1'):
		crr_y = current_data.entry1.default.d6d1[...]
	else:
		crr_y = current_data.entry1.default.qbpm0_total[...]
	if file_num==None:
		last_nexus_data=dnp.io.load(files[1])
		last_file_name = files[1][len(FOLDER_PATH):]
		print "Retrieved last scan file {} ".format(files[1])
	else:
		file_path = FOLDER_PATH+"i22-"+file_num+".nxs"
		last_file_name = "i22-{}.nxs".format(file_num)
		last_nexus_data=dnp.io.load(file_path)
		print "Retrieved specified scan file {} ".format(file_path)
	last_y = []
	if hasattr(last_nexus_data.entry1.default, 'd4d1'):
		last_y = last_nexus_data.entry1.default.d4d1[...]
	elif hasattr(last_nexus_data.entry1.default, 'd6d1'):
		last_y = last_nexus_data.entry1.default.d6d1[...]
	else:
		last_y = last_nexus_data.entry1.default.qbpm0_total[...]
	print "Current: {}" .format(crr_y)
	print "Last: {}" .format(last_y)
	if (len(crr_y) != len(last_y)):
		print "Lengths of current and last scan steps are not equal"
		return False
	dnp.plot.clear(name=IDGAP_SCAN_PLOT)
	dnp.plot.line(crr_x, [(crr_y, crr_file_name), (last_y, last_file_name), (crr_y - last_y, "Differences")], 'IDGap scan: current VS last', name=IDGAP_SCAN_PLOT)

def check_acceptance(crr_y, last_y, acc_value):
	if (len(crr_y) != len(last_y)):
		print "Lengths of current and last scan steps are not equal"
		return False
	# Linearly compare elements
	for i in range(0, len(crr_y)):
		diff_value = abs(crr_y[i] - last_y[i])
		if (diff_value >= acc_value) :
			return False
	# If all elements were same.
	return True
