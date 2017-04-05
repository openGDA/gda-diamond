from gdascripts.scan import concurrentScanWrapper
from gdascripts.scan.installStandardScansWithProcessing import *
from gdascripts.analysis.datasetprocessor.oned.CenFromSPEC import CenFromSPEC

scan_processor.rootNamespaceDict = globals()
scan_processor.processors.append(CenFromSPEC())
concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()
