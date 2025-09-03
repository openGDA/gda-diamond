from gda.configuration.properties import LocalProperties
from gda.data.scan.datawriter import NexusDataWriter
from gdascripts.metadata.metadata_commands import \
        setTitle, getTitle, meta_add, meta_ll, meta_ls, meta_rm, \
        meta_clear_alldynamical
from gdascripts.scannable.installStandardScannableMetadataCollection import meta, lsmeta, addmeta, rmmeta

# Configure metadata and add the required devices
# If any device doesn't exist, no devices will be added at all

# defined in i07-config required_at_start.xml
LocalProperties.set(NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME, "metashop")

meta.readFromNexus = True
meta.rootNamespaceDict = globals()
meta.prepend_keys_with_scannable_names = False
meta.quiet = True

add_default(meta)

blList = [beamenergy, ringcurrent]
idList = [idgap]
energyList = [dcm1energy]

dcmList = [dcm1bragg, dcm1lambda, dcm1offset, dcm1xtalroll, dcm1xtalpitch,
        dcm1sep, dcm1t1h, dcm1t1, dcm1tgap, dcm1t2h, dcm1t2]

slitList = [dsxcentre, dsxsize, dsycentre, dsysize, ssxcentre,
        ssxsize, ssycentre, ssysize, mbs1xcentre, mbs1xsize,
        mbs1ycentre, mbs1ysize, mbs2xcentre, mbs2xsize, mbs2ycentre, mbs2ysize,
        mbs3xcentre, mbs3xsize, mbs3ycentre, mbs3ysize, s1xcentre, s1xsize,
        s1ycentre, s1ysize, jj1xpos, jj1xsize, jj1ypos, jj1ysize, jj2xpos,
        jj2xsize, jj2ypos, jj2ysize]

diffList = [diff1basex, diff1basey, diff1basepitch, diff1vomega, diff1vdelta,
        diff1vgamma, diff1homega, diff1chi]

diffDetList = [diff1detdist, diff1prot]

diffOffsetList = [diff1chioffset, diff1homegaoffset,
        diff1vdeltaoffset, diff1vgammaoffset, diff1vomegaoffset]

dcdList = [dcdc1pitch, dcdc1roll, dcdc1rad, dcdc2pitch, dcdc2roll, dcdc2rad,
        dcdomega, dcddrad, dcdyaw, dcdjack]

hex1List = [hex1x, hex1y, hex1z, hex1rx, hex1ry, hex1rz, hex1pivotx,
        hex1pivoty, hex1pivotz]

deviceList = [d4dx, d4x, dbsx, dbsy, dpsx, dpsy, dpsz, dpsz2, fatt, fatt_filters,
        hfmpitch, hfmstripe, hfmx, hfmx1, hfmx2, hfmy, hfmy1, hfmy2, hfmyaw, 
        vfmpitch, vfmx, vfmy, vfmy1, vfmy2]

hexapodList = [hx, hy, hz, hrx, hry, hrz]

# EH2
hex2List = [hex2x, hex2y, hex2z, hex2rx, hex2ry, hex2rz, hex2pivotx, hex2pivoty,
        hex2pivotz]

dets4List = [dets4hall, dets4ring, dets4top, dets4bottom, dets4xsize,
        dets4xcentre, dets4ysize, dets4ycentre]

dets3List = [dets3hall, dets3ring, dets3top, dets3bottom, dets3xsize,
        dets3xcentre, dets3ysize, dets3ycentre]

mbs4List = [mbs4xsize, mbs4xcentre, mbs4ysize, mbs4ycentre]

diff2List = [diff2omega, diff2alpha, diff2delta, diff2gamma, diff2prot, diff2dets3rot, diff2basex, diff2basey,
        diff2basey1, diff2basey2, diff2basepitch]

tabList = [tab1x, tab1y]

qbpmList = [d4range, ionc1range, ionc2range, qbpm1y, qbpm2y, qbpm2dx, qbpm2dy, qbpm3x,
        qbpm1range, qbpm2range, qbpm3range]

miscList = [note, dpsx_zero, dpsy_zero, dpsz_zero, dpsz2_zero, dps_cpx, dps_cpy,
            diff1_cpx, diff1_cpy, diff2_cpx, diff2_cpy]

metadata = []
metadata += blList
metadata += idList
metadata += energyList
metadata += dcmList
metadata += slitList
metadata += diffList
metadata += diffDetList
metadata += diffOffsetList
metadata += dcdList
metadata += hex1List
metadata += deviceList
metadata += hexapodList
metadata += hex2List
metadata += dets4List
metadata += dets3List
metadata += mbs4List
metadata += diff2List
metadata += tabList
metadata += qbpmList
metadata += miscList

meta_clear_alldynamical()
for _m in metadata:
    meta_add(_m)
    del _m
