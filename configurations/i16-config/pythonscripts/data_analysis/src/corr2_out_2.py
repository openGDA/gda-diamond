import h5py

datapath='/dls/i16/data/2014/cm4968-3/'
#h5infmt=datapath+'processing/twophoton_%i.h5'
h5infmt=datapath+'processing/twophoton_%i_%03i_%03i.h5'

scans=range(450745,450755)  # pdc etazero+0.056 atten 0
#scans=[450747, 450748, 450750, 450751, 450752, 450753, 450754]  # pdc etazero+0.056 atten 0
ni, nj=195, 487

h5out=datapath+'processing/twophoton_sum_c%i_%i.h5' % (scans[0], scans[-1])
print '=== Summed data will be saved to '+ h5out
outfile = h5py.File(h5out,'w')
outcorr2 = outfile.create_dataset("corr2",(ni, nj, ni, nj), int16, chunks=(1, nj, ni, nj), compression='gzip', compression_opts=1) #two-event correlations
outsum = outfile.create_dataset("sum",(ni, nj), int32, compression='gzip', compression_opts=1) #two-event correlations

corr_2_chunk=0
sum_sum=0
goodscans=[]; badscans=[];
for scan in scans:
    for start in range(1,1002,100):
        end=start+99
        try:
            h5in=h5infmt % (scan, start, end)
            infile = h5py.File(h5in,'r')
            incorr2=infile['corr2']
            insum=infile['sum']
            for ichunk in range(ni):
                print '=== Adding scan %i %i:%i chunk %i to dataset' % (scan, start, end, ichunk)
                outcorr2[ichunk]+=incorr2[ichunk]
                outsum[...] += insum[...]
            infile.close()
            goodscans+=[scan]
        except:
            badscans+=[scan]

outfile.close()
print '=== Elvis has left the building'
print '=== Good scans: ', goodscans
print '=== Bad scans: ', badscans
print '=== Output file: %s' % h5out