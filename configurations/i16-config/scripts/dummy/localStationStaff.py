# Taken from localStationStaff 2020-10-09

pil3_centre_i = pd_offset.Offset('pil3_centre_i')
pil3_centre_j = pd_offset.Offset('pil3_centre_j')
ci = pil3_centre_i()
cj = pil3_centre_j()
addmeta pil3_centre_i, pil3_centre_j

roi1 = scroi=HardwareTriggerableDetectorDataProcessor('roi1', pil3, [SumMaxPositionAndValue()])
iw=13; jw=15; roi1.setRoi(int(ci-iw/2.),int(cj-jw/2.),int(ci+iw/2.),int(cj+jw/2.))

roi2 = lcroi=HardwareTriggerableDetectorDataProcessor('roi2', pil3, [SumMaxPositionAndValue()])
iw=50; jw=50; roi2.setRoi(int(ci-iw/2.),int(cj-jw/2.),int(ci+iw/2.),int(cj+jw/2.))

if USE_DIFFCALC:
#if False:
    psic = psi
    exec('psi = hklverbose.psi')
    alphac =  alpha
    exec('alpha = hklverbose.alpha')
    betac = beta
    exec('beta = hklverbose.beta')

    # Note that metadata scannables added manually will not be added in automatically if the
    # metadata scannables list is reset using either meta_std or meta_minimal
    addmeta psi psic alpha alphac beta betac

    
    # Dan's DiffCalc crystal info class
    from i16_gda_functions import CrystalInfoDiffCalc, CrystalInfoDiffCalcName
    #xtlinfo = CrystalInfoDiffCalc('xtlinfo',ubcalc)
    #addmeta xtlinfo
    xtlinfo = CrystalInfoDiffCalcName('xtlinfo',ubcalc)
    addmeta xtlinfo
