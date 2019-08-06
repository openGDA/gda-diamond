
from gda.jython.commands.ScannableCommands import add_default;

from Diamond.PseudoDevices.MetadataHeaderDevice import MetadataHeaderDeviceClass

fileHeader = MetadataHeaderDeviceClass("fileHeader");

blList = [beamenergy, ringcurrent];
qcaList = [adcqca]
idList = [idgap];
energyList = [dcm1energy];

dcmList = [dcm1bragg,dcm1lambda,dcm1offset,dcm1xtalroll,dcm1xtalpitch,dcm1sep,dcm1t1h,dcm1t1,dcm1tgap,dcm1t2h,dcm1t2];

slitList = [dets1xcentre,dets1xsize,dets1ycentre,dets1ysize,dets2xcentre,dets2xsize,dets2ycentre,dets2ysize,mbs1xcentre,mbs1xsize,mbs1ycentre,mbs1ysize,mbs2xcentre,mbs2xsize,mbs2ycentre,mbs2ysize,mbs3xcentre,mbs3xsize,mbs3ycentre,mbs3ysize,s1xcentre,s1xsize,s1ycentre,s1ysize,jj1xpos, jj1xsize, jj1ypos, jj1ysize, jj2xpos, jj2xsize, jj2ypos, jj2ysize]

diffList = [diff1x, diff1y, diff1z, diff1basex, diff1basey, diff1basepitch, diff1cchi, diff1cphi, diff1vomega, diff1valpha, diff1vdelta, diff1vgamma, diff1homega, diff1halpha];
diffDetList = [diff1detdist,diff1dets1rot,diff1dets2rot,diff1detselect, diff1prot];
diffOffsetList = [diff1halphaoffset, diff1homegaoffset, diff1valphaoffset, diff1vdeltaoffset, diff1vgammaoffset, diff1vomegaoffset];

dcdList = [dcdc1pitch,dcdc1roll,dcdc1rad,dcdc2pitch,dcdc2roll, dcdc2rad, dcdomega, dcddrad, dcdyaw, dcdjack];

hex1List = [hex1x,hex1y,hex1z,hex1rx,hex1ry,hex1rz,hex1pivotx, hex1pivoty, hex1pivotz];

deviceList = [d4dx,d4x,ftx,fty,dpsx,dpsy,dpsz,hfmpitch,hfmstripe,hfmx,hfmx1,hfmx2,hfmy,hfmy1,hfmy2,hfmyaw,vfmpitch,vfmx,vfmy,vfmy1,vfmy2,filterset];

#EH2
hex2List=[hex2x, hex2y, hex2z, hex2rx, hex2ry, hex2rz, hex2pivotx, hex2pivoty, hex2pivotz];
dets4List=[dets4hall, dets4ring, dets4top, dets4bottom, dets4xsize, dets4xcentre, dets4ysize, dets4ycentre];
dets3List=[dets3hall, dets3ring, dets3top, dets3bottom, dets3xsize, dets3xcentre, dets3ysize, dets3ycentre];
mbs4List=[mbs4xsize, mbs4xcentre, mbs4ysize, mbs4ycentre]
#diff2List=[diff2omega, diff2alpha, diff2delta, diff2gamma, diff2detselect, diff2prot, diff2dets4rot, diff2dets3rot, diff2detsvrot, diff2basex, diff2basey, diff2basey1, diff2basey2, diff2basepitch];
diff2List=[diff2omega, diff2alpha, diff2delta, diff2gamma, diff2detselect, diff2prot, diff2dets4rot, diff2dets3rot, diff2basex, diff2basey, diff2basey1, diff2basey2, diff2basepitch];

tabList = [tab1x, tab1y]
qbpmList = [qbpm1y, qbpm2y, qbpm2dx, qbpm2dy, qbpm3x]


#fileHeader.remove([testMotor2]);


fileHeader.add(blList);
fileHeader.add(qcaList);
fileHeader.add(idList);
fileHeader.add(energyList);
fileHeader.add(dcmList);
fileHeader.add(slitList)
fileHeader.add(diffList);
fileHeader.add(diffDetList);
fileHeader.add(diffOffsetList);
fileHeader.add(dcdList);
fileHeader.add(hex1List);

fileHeader.add(deviceList);

fileHeader.add(hex2List);
fileHeader.add(dets4List);
fileHeader.add(dets3List);
fileHeader.add(mbs4List);
fileHeader.add(diff2List);
fileHeader.add(tabList)
fileHeader.add(qbpmList)

add_default([fileHeader]);


pilatusHeader = MetadataHeaderDeviceClass("pilatusHeader");
pilatusHeader.add( fileHeader.getDeviceList() );


from gdascripts.scannable.dummy import SingleInputStringDummy
note = SingleInputStringDummy('note')
fileHeader.add([note])
pilatusHeader.add([note])


