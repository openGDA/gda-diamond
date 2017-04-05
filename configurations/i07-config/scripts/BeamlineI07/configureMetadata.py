from gda.configuration.properties import LocalProperties
from gda.data.scan.datawriter import NexusDataWriter
from gdascripts.metadata.metadata_commands import \
        setTitle, getTitle, meta_add, meta_ll, meta_ls, meta_rm,\
        meta_clear_alldynamical
from gdascripts.scannable.installStandardScannableMetadataCollection import meta

from BeamlineI07.regiontracker import ADRegionTracker

# defined in mt-config required_at_start.xml
LocalProperties.set(NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME, "metashop")

blList = [beamenergy, ringcurrent]
qcaList = [adcqca]
idList = [idgap]
energyList = [dcm1energy]

dcmList = [dcm1bragg, dcm1lambda, dcm1offset, dcm1xtalchange, dcm1xtal1roll,
        dcm1xtal2roll, dcm1xtal2pitch, dcm1sep, dcm1xtal1roll,
        dcm1xtal1roll_lvdt, dcm1xtal2pitch, dcm1xtal2pitch_lvdt, dcm1xtal2roll,
        dcm1xtal2roll_lvdt, dcm1xtalchange]

slitList = [dets1xcentre, dets1xsize, dets1ycentre, dets1ysize, dets2xcentre,
        dets2xsize, dets2ycentre, dets2ysize, mbs1xcentre, mbs1xsize,
        mbs1ycentre, mbs1ysize, mbs2xcentre, mbs2xsize, mbs2ycentre, mbs2ysize,
        mbs3xcentre, mbs3xsize, mbs3ycentre, mbs3ysize, s1xcentre, s1xsize,
        s1ycentre, s1ysize, jj1xpos, jj1xsize, jj1ypos, jj1ysize, jj2xpos,
        jj2xsize, jj2ypos, jj2ysize]

diffList = [diff1x, diff1y, diff1z, diff1basex, diff1basey, diff1basepitch,
        diff1cchi, diff1cphi, diff1vomega, diff1valpha, diff1vdelta,
        diff1vgamma, diff1homega, diff1halpha]

diffDetList = [diff1detdist,diff1dets1rot,diff1dets2rot,diff1detselect,
        diff1prot]

diffOffsetList = [diff1halphaoffset, diff1homegaoffset, diff1valphaoffset,
        diff1vdeltaoffset, diff1vgammaoffset, diff1vomegaoffset]

dcdList = [dcdc1pitch, dcdc1roll, dcdc1rad, dcdc2pitch, dcdc2roll, dcdc2rad,
        dcdomega, dcddrad, dcdyaw, dcdjack]

hex1List = [hex1x, hex1y, hex1z, hex1rx, hex1ry, hex1rz, hex1pivotx,
        hex1pivoty, hex1pivotz]

deviceList = [d4dx, d4x, ftx, fty, dpsx, dpsy, dpsz, hfmpitch, hfmstripe,
        hfmx, hfmx1, hfmx2, hfmy, hfmy1, hfmy2, hfmyaw, vfmpitch, vfmx, vfmy,
        vfmy1, vfmy2, filterset]


#EH2
hex2List=[hex2x, hex2y, hex2z, hex2rx, hex2ry, hex2rz, hex2pivotx, hex2pivoty,
        hex2pivotz]

dets4List=[dets4hall, dets4ring, dets4top, dets4bottom, dets4xsize,
        dets4xcentre, dets4ysize, dets4ycentre]

dets3List=[dets3hall, dets3ring, dets3top, dets3bottom, dets3xsize,
        dets3xcentre, dets3ysize, dets3ycentre]

mbs4List=[mbs4xsize, mbs4xcentre, mbs4ysize, mbs4ycentre]

diff2List=[diff2omega, diff2alpha, diff2delta, diff2gamma, diff2detselect,
        diff2prot, diff2dets4rot, diff2dets3rot, diff2basex, diff2basey,
        diff2basey1, diff2basey2, diff2basepitch]

pil1_region_tracker = ADRegionTracker(
        "pil1_region_tracker", fastpil1, "Pilatus 1 Array")
pil2_region_tracker = ADRegionTracker(
        "pil2_region_tracker", fastpil2, "Pilatus 2 Array")
pil3_region_tracker = ADRegionTracker(
        "pil3_region_tracker", fastpil3, "Pilatus 3 Array")

metadata = []
metadata += blList
metadata += qcaList
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
metadata += hex2List
metadata += dets4List
metadata += dets3List
metadata += mbs4List
metadata += diff2List
metadata += [pil1_region_tracker, pil2_region_tracker, pil3_region_tracker]

meta_clear_alldynamical()
for _m in metadata:
    meta_add(_m)

meta.readFromNexus = True
meta.rootNamespaceDict = globals()
meta.prepend_keys_with_scannable_names = False

try_execfile("BeamlineI07/diffcalcmeta.py") # requires globals
diffcalc_lattice = diffcalc_xtal_metadata("diffcalc_lattice", "diffcalc_object._ubcalc.getState()")
diffcalc_u = diffcalc_matrix_metadata("diffcalc_u", "u", "diffcalc_object._ubcalc.getUMatrix().array")
diffcalc_ub = diffcalc_matrix_metadata("diffcalc_ub", "ub", "diffcalc_object._ubcalc.getUBMatrix().array")

meta_add(diffcalc_lattice)
meta_add(diffcalc_u)
meta_add(diffcalc_ub)

from gdascripts.scannable.dummy import SingleInputStringDummy
note = SingleInputStringDummy('note')

meta_add(note)

try:
    remove_default(fileHeader)
except:
    pass

add_default(meta)
