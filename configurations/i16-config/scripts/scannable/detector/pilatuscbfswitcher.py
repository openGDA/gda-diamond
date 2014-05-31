from gda.analysis.io import  PilatusTiffLoader
from gda.analysis.io import  CBFLoader

TEMPLATE =    '%s%s%05d.'
HW_TEMPLATE = '%s00000_%s%05d.'

FILEWRITERS = {'tif': PilatusTiffLoader,
               'cbf': CBFLoader}
def dump(pilatus_wrapper):
    d = pilatus_wrapper
    
    lines = []
    lines.append("%s.detector.tifwriter.fileTemplate = '%s'" % (d.name, d.detector.tifwriter.fileTemplate))
    lines.append("%s.detector.tifwriter.fileTemplateForReadout = '%s'" % (d.name, d.detector.tifwriter.fileTemplateForReadout))
    lines.append("\n")
    
    lines.append("%s.detector_for_snaps.tifwriter.fileTemplate = '%s'" % (d.name, d.detector_for_snaps.tifwriter.fileTemplate))
    lines.append("%s.detector_for_snaps.tifwriter.fileTemplateForReadout = '%s'" % (d.name, d.detector_for_snaps.tifwriter.fileTemplateForReadout))
    lines.append("\n")
    
    lines.append("%s.hardware_triggered_detector.tifwriter.fileTemplate = '%s'" % (d.name, d.hardware_triggered_detector.tifwriter.fileTemplate))
    lines.append("%s.hardware_triggered_detector.tifwriter.fileTemplateForReadout = '%s'" % (d.name, d.hardware_triggered_detector.tifwriter.fileTemplateForReadout))
    lines.append("\n")
    lines.append("%s.iFileLoader = %s" % (d.name, d.iFileLoader))
    print "\n".join(lines)


def set(pilatus_wrapper, extension):
    if extension not in ('tif', 'cbf'):
        raise Exception("extension '%s' must be 'tif' or 'cbf'" % extension)
    print "*** switching %s to write .%s files ***" % (pilatus_wrapper.name, extension)
    d = pilatus_wrapper
    d.detector.tifwriter.fileTemplate = TEMPLATE + extension
    d.detector_for_snaps.tifwriter.fileTemplate = TEMPLATE + extension
    d.hardware_triggered_detector.tifwriter.fileTemplate = TEMPLATE + extension
    d.hardware_triggered_detector.tifwriter.fileTemplateForReadout = HW_TEMPLATE + extension
    
    d.iFileLoader = FILEWRITERS[extension]
    
