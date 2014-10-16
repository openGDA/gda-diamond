import h5py


fname='/dls/i16/data/2014/cm4968-3/processing/tmp1.h5'

outfile = h5py.File(fname,'w') 
mydat=outfile.create_dataset('mydat',(100,100))
mydat[...]=rand(100,100)
outfile.close()


indat = h5py.File(fname,'r')
dat=indat['mydat'][...]
indat.close()





'''
datapath='/dls/i16/data/2014/cm4968-3/'
h5infmt=datapath+'processing/two_photon_%i.h5'

scan=450745
infile = h5py.File(h5infmt % scan,'r') 
imsum=infile['sum'][...] #copy data from h5 dataset
#corr2=infile['corr2'][...]
infile.close()

print 'max sum:',imsum.max()
#print 'max corr2:',corr2.max()


#figure(); pcolor(isum[...]); axis('tight');
'''




