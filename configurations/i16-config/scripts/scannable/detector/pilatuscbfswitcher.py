from gda.analysis.io import  PilatusTiffLoader
from gda.analysis.io import  CBFLoader

TEMPLATE =    '%s%s%05d.'
HW_TEMPLATE = '%s00000_%s%05d.'

FILEWRITERS = {'tif': PilatusTiffLoader,
               'cbf': CBFLoader}
def dump(pilatus_wrapper):
    d = pilatus_wrapper
    
    lines = []
    lines.append("%s.detector.filewriter.fileTemplate = '%s'" % (d.name, d.detector.filewriter.fileTemplate))
    lines.append("%s.detector.filewriter.fileTemplateForReadout = '%s'" % (d.name, d.detector.filewriter.fileTemplateForReadout))
    lines.append("\n")
    
    lines.append("%s.detector_for_snaps.filewriter.fileTemplate = '%s'" % (d.name, d.detector_for_snaps.filewriter.fileTemplate))
    lines.append("%s.detector_for_snaps.filewriter.fileTemplateForReadout = '%s'" % (d.name, d.detector_for_snaps.filewriter.fileTemplateForReadout))
    lines.append("\n")
    
    lines.append("%s.hardware_triggered_detector.filewriter.fileTemplate = '%s'" % (d.name, d.hardware_triggered_detector.filewriter.fileTemplate))
    lines.append("%s.hardware_triggered_detector.filewriter.fileTemplateForReadout = '%s'" % (d.name, d.hardware_triggered_detector.filewriter.fileTemplateForReadout))
    lines.append("\n")
    lines.append("%s.iFileLoader = %s" % (d.name, d.iFileLoader))
    print "\n".join(lines)


def set(pilatus_wrapper, extension):
    if extension not in ('tif', 'cbf'):
        raise Exception("extension '%s' must be 'tif' or 'cbf'" % extension)
    print "*** switching %s to write .%s files ***" % (pilatus_wrapper.name, extension)
    d = pilatus_wrapper
    d.detector.filewriter.fileTemplate = TEMPLATE + extension
    d.detector_for_snaps.filewriter.fileTemplate = TEMPLATE + extension
    d.hardware_triggered_detector.filewriter.fileTemplate = TEMPLATE + extension
    d.hardware_triggered_detector.filewriter.fileTemplateForReadout = HW_TEMPLATE + extension
    
    d.iFileLoader = FILEWRITERS[extension]
    
