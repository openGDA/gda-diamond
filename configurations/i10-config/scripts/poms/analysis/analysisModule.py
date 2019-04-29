""" version 1 """

import h5py
import numpy as np



# analyse collections of XMCD scans
def loadXMCD(directory, scansA, scansB):
	data = {}

	f = h5py.File(directory+"/i10-%06d.nxs" % (scansA ) ,'r')
	grp = f['entry1']['instrument']

	egyStrings = ["egy_g_idu_circ_pos_energy", "egy_g_idu_circ_neg_energy", "egy_g_idd_circ_pos_energy", "egy_g_idd_circ_neg_energy"]

	for egyStr in egyStrings:
		if egyStr in grp:
			data['energy'] = grp[egyStr]['demand'][:]
			data['a_energy'] = grp[egyStr]['pgm_energy'][:]

	data['a_macr17']  = grp['mcsr17_g']['data'][:] / grp['mcsr16_g']['data'][:]
	data['a_macr18']  = grp['mcsr18_g']['data'][:] / grp['mcsr16_g']['data'][:]
	data['a_macr19']  = grp['mcsr19_g']['data'][:] / grp['mcsr16_g']['data'][:]
	f.close()


	f = h5py.File(directory+"/i10-%06d.nxs" % (scansB) ,'r')
	grp = f['entry1']['instrument']

	for egyStr in egyStrings:
		if egyStr in grp:
			data['energy'] = grp[egyStr]['demand'][:]
			data['b_energy'] = grp[egyStr]['pgm_energy'][:]

	data['b_macr17'] = grp['mcsr17_g']['data'][:] / grp['mcsr16_g']['data'][:]
	data['b_macr18'] = grp['mcsr18_g']['data'][:] / grp['mcsr16_g']['data'][:]
	data['b_macr19'] = grp['mcsr19_g']['data'][:] / grp['mcsr16_g']['data'][:]
	f.close()

	data['m17'] = {}
	data['m18'] = {}
	data['m19'] = {}

	data['m17']['a'] = np.interp(data['energy'], data['a_energy'], data['a_macr17'])
	data['m17']['b'] = np.interp(data['energy'], data['b_energy'], data['b_macr17'])

	data['m18']['a'] = np.interp(data['energy'], data['a_energy'], data['a_macr18'])
	data['m18']['b'] = np.interp(data['energy'], data['b_energy'], data['b_macr18'])

	data['m19']['a'] = np.interp(data['energy'], data['a_energy'], data['a_macr19'])
	data['m19']['b'] = np.interp(data['energy'], data['b_energy'], data['b_macr19'])



	# find the energies of the maximum and minimum differences
	
	for m in ['m17', 'm18', 'm19']:
		minIndex = np.argmin(data[m]['a']-data[m]['b'])
		data[m]['min'] = data['energy'][minIndex]

		maxIndex = np.argmax(data[m]['a']-data[m]['b'])
		data[m]['max'] = data['energy'][maxIndex]

	return data









def loadXMLD(directory, scans):
	data = {}
	data['scans'] = []

	for s in scans:
		f = h5py.File(directory+"/i10-%06d.nxs" % (s) ,'r')
		grp = f['entry1']['instrument']
		energy = grp['egy_g_idu_lin_arbitrary_energy']['demand'][:]
		raw_energy = grp['egy_g_idu_lin_arbitrary_energy']['pgm_energy'][:]
		sig  = grp['mcsr17_g']['data'][:] / grp['mcsr16_g']['data'][:]
		f.close()

		sig = np.interp(energy, raw_energy, sig) # interpolate to get regular energy points
		data['scans'] = np.append(data['scans'], {'energy':energy, 'sig':sig})

	return data





