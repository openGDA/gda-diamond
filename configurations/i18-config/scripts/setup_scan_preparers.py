from uk.ac.gda.server.exafs.scan.preparers import I18BeamlinePreparer, I18SamplePreparer, I18OutputPreparer
from uk.ac.gda.server.exafs.scan.preparers import I18DetectorPreparer, IonchamberCollectionPreparer

sensitivities = [I0_stanford_sensitivity, It_stanford_sensitivity]
sensitivity_units = [I0_stanford_sensitivity_units, It_stanford_sensitivity_units]
detectorPreparer = I18DetectorPreparer(sensitivities, sensitivity_units)
conversion_map = { "counterTimer01":"qexafs_counterTimer01",
                  "xspress3Odin":"qexafs_xspress3Odin",
                  "FFI0_xspress3Odin":"qexafs_FFI0_xspress3Odin",
                  "panda_scalers":"qexafs_panda",
                  "FFI0_xspress3Odin_panda" : "qexafs_FFI0_xspress3Odin_panda"}

detectorPreparer.setBufferedDetectorNameMap(conversion_map)

ionchamber_collection_preparer = IonchamberCollectionPreparer()
ionchamber_collection_preparer.setPandaDetector(panda_scalers)
ionchamber_collection_preparer.setTfgScalers(counterTimer01)

#ionchamber_checker_preparer is created in 'ionchamber-checker-scannables.py' (run earlier on in 'localStation.py')
detectorPreparer.getPreparerDelegates().setPreparers([ionchamber_checker_preparer, ionchamber_collection_preparer])

samplePreparer = I18SamplePreparer()

outputPreparer = I18OutputPreparer(datawriterconfig, Finder.find("metashop"))

auto_mDeg_idGap_mm_converter = Finder.find("auto_mDeg_idGap_mm_converter_Si111")
beamlinePreparer = I18BeamlinePreparer(topupMonitor, beamMonitor, detectorFillingMonitor, energy, energy_nogap, auto_mDeg_idGap_mm_converter)  # @UndefinedVariable
