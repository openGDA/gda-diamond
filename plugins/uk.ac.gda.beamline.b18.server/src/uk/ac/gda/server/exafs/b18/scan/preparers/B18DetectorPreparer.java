package uk.ac.gda.server.exafs.b18.scan.preparers;

import java.io.File;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.stream.Collectors;

import org.apache.commons.io.FilenameUtils;
import org.apache.commons.lang.ArrayUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.scan.datawriter.DataWriter;
import gda.data.scan.datawriter.DataWriterFactory;
import gda.data.scan.datawriter.DefaultDataWriterFactory;
import gda.data.scan.datawriter.XasAsciiNexusDataWriter;
import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.BufferedDetector;
import gda.device.detector.DetectorHdfFunctions;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.detector.mythen.MythenDetectorImpl;
import gda.device.detector.nxdetector.NXPluginBase;
import gda.device.detector.nxdetector.roi.MutableRectangularIntegerROI;
import gda.exafs.scan.ExafsScanPointCreator;
import gda.exafs.scan.XanesScanPointCreator;
import gda.jython.InterfaceProvider;
import gda.scan.StaticScan;
import uk.ac.gda.beans.exafs.DetectorConfig;
import uk.ac.gda.beans.exafs.DetectorGroup;
import uk.ac.gda.beans.exafs.DetectorParameters;
import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IExperimentDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.IonChamberParameters;
import uk.ac.gda.beans.exafs.TransmissionParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.server.exafs.scan.DetectorPreparerFunctions;
import uk.ac.gda.server.exafs.scan.QexafsDetectorPreparer;
import uk.ac.gda.util.beans.xml.XMLHelpers;

public class B18DetectorPreparer implements QexafsDetectorPreparer {

	private static final Logger logger = LoggerFactory.getLogger(B18DetectorPreparer.class);

	private Scannable energy_scannable;
	private MythenDetectorImpl mythen_scannable;

	private List<Scannable> ionc_gas_injector_scannables;

	protected Detector selectedDetector;
	private String experimentXmlFullPath;
	private String hdfFilePath;

	private IScanParameters scanBean;
	private TfgScalerWithFrames ionchambers;
	private IDetectorParameters detectorBean;

	// QEXAFS options
	private boolean gmsd_enabled;
	private boolean additional_channels_enabled;
	private String experimentFullPath;
	private IOutputParameters outputBean;
	private B18SamplePreparer samplePreparer;

	/** Map to go from name of detector to name of corresponding buffered detector object to use in QExafs scans */
	private Map<String, String> bufferedDetectorNameMap = new LinkedHashMap<>();
	private DetectorPreparerFunctions detectorPreparerFunctions = new DetectorPreparerFunctions();

	public B18DetectorPreparer(Scannable energy_scannable, MythenDetectorImpl mythen_scannable,
			Scannable[] sensitivities, Scannable[] sensitivity_units, Scannable[] offsets, Scannable[] offset_units,
			List<Scannable> ionc_gas_injector_scannables, TfgScalerWithFrames ionchambers) {
		this.energy_scannable = energy_scannable;
		this.mythen_scannable = mythen_scannable;
		detectorPreparerFunctions.setSensitivities(sensitivities);
		detectorPreparerFunctions.setSensitivityUnits(sensitivity_units);
		detectorPreparerFunctions.setOffsets(offsets);
		detectorPreparerFunctions.setOffsetUnits(offset_units);
		this.ionc_gas_injector_scannables = ionc_gas_injector_scannables;
		this.ionchambers = ionchambers;
		bufferedDetectorNameMap = getDefaultBufferedDetectorNameMap();
	}

	@Override
	public void configure(IScanParameters scanBean, IDetectorParameters detectorBean, IOutputParameters outputBean,
			String experimentFullPath) throws Exception {

		this.experimentXmlFullPath = experimentFullPath;

		this.scanBean = scanBean;
		this.detectorBean = detectorBean;
		this.experimentFullPath = experimentFullPath;
		this.outputBean = outputBean;

		if (useNewDetectorConfiguration()) {
			prepareDetectors(detectorBean.getDetectorConfigurations());
			return;
		}

		if (detectorBean.getExperimentType().equalsIgnoreCase(DetectorParameters.FLUORESCENCE_TYPE)) {
			FluorescenceParameters fluorescenceParameters = detectorBean.getFluorescenceParameters();
			String xmlFileName = Paths.get(experimentXmlFullPath, fluorescenceParameters.getConfigFileName()).toString();
			selectedDetector = detectorPreparerFunctions.configureDetector(xmlFileName);
			logger.info("Configuring {} using parameter file {}", selectedDetector.getName(), xmlFileName);
			String dirForHdfFile = Paths.get(getDataFolderFullPath(), selectedDetector.getName()).toString();
			hdfFilePath = DetectorHdfFunctions.setHdfFilePath(selectedDetector, dirForHdfFile);
			control_all_ionc(fluorescenceParameters.getIonChamberParameters());
		} else if (detectorBean.getExperimentType().equalsIgnoreCase(DetectorParameters.TRANSMISSION_TYPE)) {
			selectedDetector = null;
			TransmissionParameters transmissionParameters = detectorBean.getTransmissionParameters();
			control_all_ionc(transmissionParameters.getIonChamberParameters());
		}
	}

	private boolean useNewDetectorConfiguration() {
		return detectorBean != null &&
				detectorBean.getDetectorConfigurations() != null &&
				!detectorBean.getDetectorConfigurations().isEmpty();
	}

	private void prepareDetectors(List<DetectorConfig> detectorConfigs) {
		detectorPreparerFunctions.setConfigFileDirectory(experimentFullPath);
		detectorPreparerFunctions.setDataDirectory(experimentFullPath.replace("/xml/", "/"));
		detectorPreparerFunctions.configure(detectorConfigs);
	}

	private String getDataFolderFullPath() {
		String folder = experimentXmlFullPath.replace("/xml/", "/");
		return FilenameUtils.getFullPath(folder);
	}

	/**
	 * Collected Mythen diffraction data (if 'collect' checkbox is ticked in Detector params.)
	 * Refactored from 'configure' function
	 * @since 26/5/2016
	 * @throws Exception
	 */
	public void collectMythenData() throws Exception {
		IExperimentDetectorParameters detParams = getDetectorParameters();
		if ( detParams != null && detParams.isCollectDiffractionImages() == true ){
			control_mythen(detParams, outputBean, experimentFullPath);
		}
	}

	private IExperimentDetectorParameters getDetectorParameters() {
		if (detectorBean.getExperimentType().equalsIgnoreCase(DetectorParameters.FLUORESCENCE_TYPE)) {
			return detectorBean.getFluorescenceParameters();
		} else if (detectorBean.getExperimentType().equalsIgnoreCase(DetectorParameters.TRANSMISSION_TYPE)) {
			return detectorBean.getTransmissionParameters();
		}
		else
			return null;
	}

	@Override
	public void beforeEachRepetition() throws Exception {
		if (isFirstRepetition()) {
			beforeFirstRepetition();
		}
		setupIonchamberFrameTimes();
	}

	private void beforeFirstRepetition() throws Exception {
		if (useNewDetectorConfiguration()) {
			Optional<DetectorConfig> mythenConfig = detectorBean.getDetectorConfigurations()
					.stream()
					.filter(conf -> conf.getDetectorName().equals(mythen_scannable.getName()))
					.findFirst();
			if (mythenConfig.isPresent() && mythenConfig.get().isUseDetectorInScan()) {
				File mythenFile = Paths.get(experimentFullPath, mythenConfig.get().getConfigFileName()).toFile();
				IExperimentDetectorParameters mythenBean = (IExperimentDetectorParameters) XMLHelpers.getBean(mythenFile);
				control_mythen(mythenBean, outputBean, experimentFullPath);
			}
		} else {
			collectMythenData();
		}
	}

	private boolean isFirstRepetition() {
		// Use SampleEnvironmentIterator to determine if doing first repetition of scan, or first of loop over sample environment.
		if (samplePreparer != null) {
			B18SampleEnvironmentIterator iter = samplePreparer.getCurrentSampleEnvironmentIterator();
			return iter.getCurrentScanRepetitionNumber() == 1;
		}
		return true;
	}


	private void setupIonchamberFrameTimes() throws Exception {
		Double[] times = new Double[] {};
		if (scanBean instanceof XasScanParameters) {
			times = ExafsScanPointCreator.getScanTimeArray((XasScanParameters) scanBean);
		} else if (scanBean instanceof XanesScanParameters) {
			times = XanesScanPointCreator.getScanTimeArray((XanesScanParameters) scanBean);
		}
		if (times.length > 0) {
			ionchambers.setTimes(times);
			InterfaceProvider.getTerminalPrinter().print("Setting detector frame times, using array of length " + times.length + "...");
		}
	}

	@Override
	public void completeCollection() {
		try {
			// Set filepath for hdf file writer back to the original value
			DetectorHdfFunctions.setHdfFilePath(selectedDetector, hdfFilePath);
			detectorPreparerFunctions.restoreDetectorState();
		} catch (DeviceException e) {
			logger.error("Problem setting xspress3 path to {} at end of scan", hdfFilePath);
		}
	}

	protected void control_all_ionc(List<IonChamberParameters> ion_chambers_bean) throws Exception {
		for (int index = 0; index < ion_chambers_bean.size(); index++) {
			control_ionc(ion_chambers_bean, index);
		}
	}

	protected void control_ionc(List<IonChamberParameters> ion_chambers_bean, int ion_chamber_num) throws Exception {
		IonChamberParameters ion_chamber = ion_chambers_bean.get(ion_chamber_num);
		detectorPreparerFunctions.setupAmplifierSensitivity(ion_chamber, ion_chamber_num);
		boolean autoGas = ion_chamber.getAutoFillGas();
		if (autoGas) {
			double gas_fill1_pressure = ion_chamber.getPressure() * 1000.0;
			double gas_fill1_period = ion_chamber.getGas_fill1_period_box();
			double gas_fill2_pressure = ion_chamber.getTotalPressure() * 1000.0;
			double gas_fill2_period = ion_chamber.getGas_fill2_period_box();
			String flushString = ion_chamber.getFlush().toString();
			String purge_pressure = "25.0";
			String purge_period = "120.0";

			String gas_select = ion_chamber.getGasType();
			String gas_select_val = "-1";
			String gas_report_string = "He";
			if (gas_select.equals("Kr")) {
				gas_select_val = "0";
				gas_report_string = "He + Kr";
			} else if (gas_select.equals("N")) {
				gas_select_val = "1";
				gas_report_string = "He + N2";
			} else if (gas_select.equals("Ar")) {
				gas_select_val = "2";
				gas_report_string = "He + Ar";
			}

			InterfaceProvider.getTerminalPrinter().print(
					"Changing gas of " + ion_chamber.getName() + " to " + gas_report_string + " for "
							+ ion_chamber.getPercentAbsorption() + " % absorption");
			ionc_gas_injector_scannables.get(ion_chamber_num).moveTo(
					new Object[] { purge_pressure, purge_period, gas_fill1_pressure, gas_fill1_period,
							gas_fill2_pressure, gas_fill2_period, gas_select_val, flushString });
		}
	}

	protected void control_mythen(IExperimentDetectorParameters fluorescenceParameters, IOutputParameters outputBean,
			String experimentFullPath) throws Exception {

		String experimentFolderName = experimentFullPath.substring(experimentFullPath.indexOf("xml") + 4,
				experimentFullPath.length());
		String nexusSubFolder = experimentFolderName + "/" + outputBean.getNexusDirectory();
		String asciiSubFolder = experimentFolderName + "/" + outputBean.getAsciiDirectory();
		String mythenSubFolder = Paths.get(experimentFolderName, "mythen").toString();

		InterfaceProvider.getTerminalPrinter().print("Moving DCM for Mythen image...");

		// Save currently set mythen subdirectory - so it can be set back to original value after the scan
		String mythenSubdirectoryBeforeScan = mythen_scannable.getSubDirectory();

		energy_scannable.moveTo(fluorescenceParameters.getMythenEnergy());

		mythen_scannable.setCollectionTime(fluorescenceParameters.getMythenTime());
		mythen_scannable.setSubDirectory(mythenSubFolder);

		StaticScan staticscan = new StaticScan(new Scannable[] { mythen_scannable, energy_scannable});

		// use the Factory to enable unit testing - which would use a DummyDataWriter
		DataWriterFactory datawriterFactory = new DefaultDataWriterFactory();
		DataWriter datawriter = datawriterFactory.createDataWriter();
		if (datawriter instanceof XasAsciiNexusDataWriter) {
			((XasAsciiNexusDataWriter) datawriter).setRunFromExperimentDefinition(false);
			((XasAsciiNexusDataWriter) datawriter).setNexusFileNameTemplate(nexusSubFolder + "/%d-mythen.nxs");
			((XasAsciiNexusDataWriter) datawriter).setAsciiFileNameTemplate(asciiSubFolder + "/%d-mythen.dat");
			staticscan.setDataWriter(datawriter);
		}

		//LocalProperties.setScanSetsScanNumber(true);
		//staticscan.setScanNumber(1); // need to do this here to prevent the scan trying to use a numtracker to derive
										// the scan number
		try {
			InterfaceProvider.getTerminalPrinter().print("Collecting a diffraction image...");
			staticscan.run();
			InterfaceProvider.getTerminalPrinter().print("Diffraction scan complete.");
		} finally{
			//set mythen subdirectory back to its original value
			mythen_scannable.setSubDirectory(mythenSubdirectoryBeforeScan);
		}
	}

	@Override
	public BufferedDetector[] getQEXAFSDetectors() throws Exception {
		List<String> bufferedDetectorNames;
		if (useNewDetectorConfiguration()) {
			logger.debug("Getting QEXafs detectors from new detector settings");
			bufferedDetectorNames = getQxafsDetectorNames();
		} else {
			logger.debug("Getting QExafs detectors from old detector settings");
			bufferedDetectorNames = getQexafsDetectorNamesForExperimentType();
		}

		logger.debug("Detectors to use in scan : {}", bufferedDetectorNames);
		return createBufferedDetArray(bufferedDetectorNames);
	}

	private List<String> getQxafsDetectorNames() throws Exception {
		//create list of all detector names in use :
		List<String> detectorNames = detectorBean.getDetectorConfigurations()
				.stream()
				.filter(DetectorConfig::isUseDetectorInScan)
				.map(DetectorConfig::getAllDetectorNames)
				.flatMap(Collection::stream)
				.collect(Collectors.toList());

		return getBufferedDetectorNames(detectorNames);
	}

	private List<String> getQexafsDetectorNamesForExperimentType() {
		String experimentType = detectorBean.getExperimentType();
		logger.debug("Getting QEXafs detectors for experiment type '{}'", experimentType);

		List<String> bufferedDetectorNames;
		if (experimentType.equals(DetectorParameters.TRANSMISSION_TYPE)) {
			// Detectors for transmission measurement
			if (gmsd_enabled) {
				bufferedDetectorNames = Arrays.asList("qexafs_counterTimer01_gmsd");
			} else if (additional_channels_enabled) {
				bufferedDetectorNames = Arrays.asList("qexafs_counterTimer01", "qexafs_counterTimer01_gmsd");
			} else {
				String detectorGroup = detectorBean.getTransmissionParameters().getDetectorType();
				bufferedDetectorNames = getBufferedDetectorsForGroup(detectorGroup);
			}
		} else {
			// Detectors for fluorescence measurement
			String detectorGroup = detectorBean.getFluorescenceParameters().getDetectorType();
			bufferedDetectorNames = getBufferedDetectorsForGroup(detectorGroup);
		}

		if (bufferedDetectorNames.isEmpty()) {
			logger.warn("Couldn't determine buffered detector names to use for detector group {}", experimentType);
		}
		return bufferedDetectorNames;
	}

	/**
	 * Generate a list of names of buffered detectors for a detector group.
	 * i.e. Loop over the detector names in the named group and replace each with corresponding
	 * one from {@link #bufferedDetectorNameMap}
	 *
	 * @param detectorGroupName
	 * @return list of names of buffered detectors
	 */
	private List<String> getBufferedDetectorsForGroup(String detectorGroupName) {
		logger.debug("Getting buffered detectors for detector group {}", detectorGroupName);
		Optional<String[]> detectors = detectorBean.getDetectorGroups().stream().
			filter(detGroup -> detGroup.getName().equalsIgnoreCase(detectorGroupName)).
			map(DetectorGroup::getDetector).
			findFirst();

		if (detectors.isPresent()) {
			List<String> detectorList = Arrays.asList(detectors.get());
			// Create list of buffered detector name in same order as stored in the map
			// (i.e. ionchambers first, FFI0s last)
			return getBufferedDetectorNames(detectorList);

		} else {
			return Collections.emptyList();
		}
	}

	/**
	 *  Create list of buffered detector names from detectorList in same order as stored in the map
	 * (i.e. ionchambers first, FFI0s last)
	 * @param detectorList
	 * @return buffered detector names
	 */
	private List<String> getBufferedDetectorNames(List<String> detectorList) {
		// Create list of buffered detector name in same order as stored in the map
		// (i.e. ionchambers first, FFI0s last)
		return bufferedDetectorNameMap.entrySet().stream().
				filter(bufDet -> detectorList.contains(bufDet.getKey())).
				map(Entry::getValue).
				collect(Collectors.toList());
	}

	protected BufferedDetector[] createBufferedDetArray(List<String> names) throws Exception {
		BufferedDetector[] dets = new BufferedDetector[] {};
		for (String name : names) {
			Object detector = InterfaceProvider.getJythonNamespace().getFromJythonNamespace(name);
			if (detector == null) {
				throw new Exception("detector named " + name + " not found!");
			}
			dets = (BufferedDetector[]) ArrayUtils.add(dets, detector);
		}
		return dets;
	}

	public boolean isGmsd_enabled() {
		return gmsd_enabled;
	}

	public void setGmsd_enabled(boolean gmsd_enabled) {
		this.gmsd_enabled = gmsd_enabled;
	}

	public boolean isAdditional_channels_enabled() {
		return additional_channels_enabled;
	}

	public void setAdditional_channels_enabled(boolean additional_channels_enabled) {
		this.additional_channels_enabled = additional_channels_enabled;
	}

	@Override
	public Detector[] getExtraDetectors() {
		// not required for this beamline
		return null;
	}

	public void setSamplePreparer(B18SamplePreparer samplePreparer) {
		this.samplePreparer = samplePreparer;
	}

	/**
	 * @return Default map from detector name to buffered detector name
	 */
	private Map<String, String> getDefaultBufferedDetectorNameMap() {
		Map<String, String> map = new LinkedHashMap<>();
		map.put("counterTimer01", "qexafs_counterTimer01");
		map.put("xmapMca", "qexafs_xmap");
		map.put("xspress2system", "qexafs_xspress");
		map.put("xspress3", "qexafs_xspress3");
		map.put("xspress4", "qexafs_xspress4");
		map.put("medipix", "qexafs_medipix");
		map.put("FFI0", "QexafsFFI0");
		map.put("FFI0_vortex", "VortexQexafsFFI0");
		map.put("FFI0_xspress3", "qexafs_FFI0_xspress3");
		map.put("xspress4FFI0", "qexafs_FFI0_xspress4");
		return map;
	}

	/**
	 * Add mapping from detector name to name of corresponding buffered detector
	 *
	 * @param detName name of detector
	 * @param bufferedDetName name of buffered detector
	 */
	public void addDetectorNameMapping(String detName, String bufferedDetName) {
		bufferedDetectorNameMap.put(detName, bufferedDetName);
	}

	/**
	 * Add mapping from detector name to name of corresponding buffered detector
	 *
	 * @param det detector object
	 * @param bufferedDet buffered detector object
	 */
	public void addDetectorNameMapping(Scannable det, Scannable bufferedDet) {
		bufferedDetectorNameMap.put(det.getName(), bufferedDet.getName());
	}

	public Map<String, String> getDetectorNameMap() {
		return bufferedDetectorNameMap;
	}

	public void setDetectorNameMap(Map<String, String> map) {
		bufferedDetectorNameMap = new LinkedHashMap<>(map);
	}

	public Detector getSelectedDetector() {
		return selectedDetector;
	}

	public void setMedipixPlugins(List<NXPluginBase> mutableRoiPluginList) {
		detectorPreparerFunctions.setMutableRoiPluginList(mutableRoiPluginList);
	}

	public void setMedipixMutableRoi(MutableRectangularIntegerROI mutableRoiForMedipix) {
		detectorPreparerFunctions.setMutableRoiForMedipix(mutableRoiForMedipix);
	}
}