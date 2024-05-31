from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict = globals()

from gdascripts.scannable.timerelated import TimeSinceScanStart
timerScannable = TimerSinceScanStart("timerScannable")