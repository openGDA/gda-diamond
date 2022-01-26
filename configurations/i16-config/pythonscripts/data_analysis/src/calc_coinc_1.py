import h5py

datapath='/dls/i16/data/2014/cm4968-3/processing/'
h5in=datapath+'twophoton_sum_b%i_%i.h5' % (450745, 450754)
infile = h5py.File(h5in,'r')
incorr2=infile['corr2']
insum=infile['sum']

def circ(centre,radius,anglerad):
    #anglerad or radius can be vectors
    anglerad=array(anglerad)
    radius=array(radius)
    x=centre[0]+radius*sin(anglerad)
    y=centre[1]+radius*cos(anglerad)
    return array([x,y]).transpose().round()

ni, nj=195, 487

#ijvals=circ([70,350],20,pi*2*arange(0,1,.02))
ijvals=circ([70,350],50,pi*2*arange(0,1,.005))

#add up images with these pixels from corr2 data
#load corr2 then
imdat=zeros((ni,nj),'Int32')
maskdat=zeros((ni,nj),'Int32')
imsum=insum[...]
nin=0;nout=0;sum_mask=0
for ij in ijvals:
    print ij
    try:
        imdat+=incorr2[ij[0], ij[1]]
        maskdat[ij[0], ij[1]]+=1
        sum_mask+=incorr2[ij[0], ij[1], ij[0], ij[1]]
        nin+=1
    except:
        nout+=1
print '%i pixels inside image, %i pixels outside image' % (nin, nout)
figure(); pcolor(imdat); axis('tight'); 
bg=imsum*1.*(imdat.sum()-sum_mask)/imsum.sum()
bg_corrected=1.0*(imdat-bg)
figure(); pcolor(bg_corrected); axis('tight'); clim(bg_corrected.min(), bg_corrected.max()); colorbar()
#bg_corrected=(imdat-imdat.sum()/imsum.sum()*imsum)
med=median(bg_corrected); minmax=(0.9*med, 1.1*med); clim(min(minmax),max(minmax))