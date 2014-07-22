import h5py
import os

datapath='/dls/i16/data/2014/cm4968-3/processing/'
#h5in_name=datapath+'twophoton_450747.h5'    #single scan
h5in_name=datapath+'twophoton_sum_%i_%i.h5' % (450745, 450754)


infile = h5py.File(h5in_name,'r')
incorr2=infile['corr2']
insum=infile['sum'][...]

print insum.sum()

os.system('python corr2_submit_jobs.py /dls/i16/data/2014/cm4968-3/ 450745 1 10') 

