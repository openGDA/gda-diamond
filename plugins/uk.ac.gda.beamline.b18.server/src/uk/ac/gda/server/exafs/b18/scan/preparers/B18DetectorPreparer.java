package uk.ac.gda.server.exafs.b18.scan.preparers;

import java.nio.file.Paths;
import java.util.Arrays;
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
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.detector.mythen.MythenDetectorImpl;
import gda.device.detector.xmap.Xmap;
import gda.device.detector.xspress.Xspress2Detector;
import gda.exafs.scan.ExafsScanPointCreator;
import gda.exafs.scan.XanesScanPointCreator;
import gda.jython.InterfaceProvider;
import gda.scan.StaticScan;
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
import uk.ac.gda.devices.detector.xspress3.Xspress3Detector;
import uk.ac.gda.server.exafs.scan.QexafsDetectorPreparer;

public class B18DetectorPreparer implements QexafsDetectorPreparer {

	private static final Logger logger = LoggerFactory.getLogger(B18DetectorPreparer.class);

	private Scannable energy_scannable;
	private MythenDetectorImpl mythen_scannable;
	private Scannable[] sensitivities;
	private Scannable[] sensitivity_units;
	private Scannable[] offsets;
	private Scannable[] offset_units;
	private List<Scannable> ionc_gas_injector_scannables;
	private Xspress2Detector xspressSystem;
	private Xmap vortexConfig;
	private Xspress3Detector xspress3Detector;
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

	public B18DetectorPreparer(Scannable energy_scannable, MythenDetectorImpl mythen_scannable,
			Scannable[] sensitivities, Scannable[] sensitivity_units, Scannable[] offsets, Scannable[] offset_units,
			List<Scannable> ionc_gas_injector_scannables, TfgScalerWithFrames ionchambers,
			Xspress2Detector xspressSystem, Xmap vortexConfig, Xspress3Detector xspress3Config) {
		this.energy_scannable = energy_scannable;
		this.mythen_scannable = mythen_scannable;
		this.sensitivities = sensitivities;
		this.sensitivity_units = sensitivity_units;
		this.offsets = offsets;
		this.offset_units = offset_units;
		this.ionc_gas_injector_scannables = ionc_gas_injector_scannables;
		this.ionchambers = ionchambers;
		this.xspressSystem = xspressSystem;
		this.vortexConfig = vortexConfig;
		this.xspress3Detector = xspress3Config;
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

		if (detectorBean.getExperimentType().equalsIgnoreCase("Fluorescence")) {
			FluorescenceParameters fluoresenceParameters = detectorBean.getFluorescenceParameters();
		//  Mythen data is now collected just before first repetition, i.e. after sample environment has been set up.
//			if (fluoresenceParameters.isCollectDiffractionImages()) {
//				control_mythen(fluoresenceParameters, outputBean, experimentFullPath);
//			}
			String detType = fluoresenceParameters.getDetectorType();
			String xmlFileName = experimentFullPath + fluoresenceParameters.getConfigFileName();
			if (detType.equals("Germanium")) {
				xspressSystem.setConfigFileName(xmlFileName);
				xspressSystem.configure();
			} else if (detType.equals("Silicon")) {
				vortexConfig.setConfigFileName(xmlFileName);
				vortexConfig.configure();
			} else if (detType.equals("Xspress3")) {
				xspress3Detector.setConfigFileName(xmlFileName);
				xspress3Detector.loadConfigurationFromFile();
				// save current file path (so can set it back at end of scan)
				xspress3HdfPath = xspress3Detector.getController().getFilePath();

				// set the file path to the new location
				String dirForXspress3 = Paths.get(getDataFolderFullPath(), "xspress3").toString();
				xspress3Detector.setFilePath(dirForXspress3);
				xspress3Detector.getController().setFilePath(dirForXspress3);
			}
			control_all_ionc(fluoresenceParameters.getIonChamberParameters());
		} else if (detectorBean.getExperimentType().equalsIgnoreCase("Transmission")) {
			TransmissionParameters transmissionParameters = detectorBean.getTransmissionParameters();
//			if (transmissionParameters.isCollectDiffractionImages()) {
//				control_mythen(transmissionParameters, outputBean, experimentFullPath);
//			}
			control_all_ionc(transmissionParameters.getIonChamberParameters());
		}
	}

	private String experimentXmlFullPath;
	private String xspress3HdfPath;

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
		if (detectorBean.getExperimentType().equalsIgnoreCase("Fluorescence")) {
			return detectorBean.getFluorescenceParameters();
		} else if (detectorBean.getExperimentType().equalsIgnoreCase("Transmission")) {
			return detectorBean.getTransmissionParameters();
		}
		else
			return null;
	}

	@Override
	public void beforeEachRepetition() throws Exception {

		boolean collectMythenData = true;

		// Use SampleEnvironmentIterator to determine if doing first repetition of scan, or first of loop over sample environment.
		if ( samplePreparer != null ) {
			B18SampleEnvironmentIterator iter = samplePreparer.getCurrentSampleEnvironmentIterator();
			boolean firstSampleRep = iter.getCurrentSampleRepetitionNumber() == 1;
			boolean firstScanRep = iter.getCurrentScanRepetitionNumber() == 1;
			if (firstScanRep) {
				collectMythenData = true;
			}
		}

		// collect Mythen data
		if ( collectMythenData ) {
			collectMythenData();
		}

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
		return;
	}

	@Override
	public void completeCollection() {
		try {
			// Set filepath for hdf file writer back to the original value
			xspress3Detector.setFilePath(xspress3HdfPath);
			xspress3Detector.getController().setFilePath(xspress3HdfPath);
		} catch (DeviceException e) {
			logger.error("Problem setting xspress3 path to {} at end of scan", xspress3HdfPath);
		}
	}

	protected void control_all_ionc(List<IonChamberParameters> ion_chambers_bean) throws Exception {
		for (int index = 0; index < ion_chambers_bean.size(); index++) {
			control_ionc(ion_chambers_bean, index);
		}
	}

	protected void control_ionc(List<IonChamberParameters> ion_chambers_bean, int ion_chamber_num) throws Exception {
		IonChamberParameters ion_chamber = ion_chambers_bean.get(ion_chamber_num);
		setup_amp_sensitivity(ion_chamber, ion_chamber_num);
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

	protected void setup_amp_sensitivity(IonChamberParameters ionChamberParams, int index) throws Exception {
		if (ionChamberParams.getChangeSensitivity()) {
			if (ionChamberParams.getGain() == null || ionChamberParams.getGain().equals("")) {
				return;
			}
			String[] gainStringParts = ionChamberParams.getGain().split(" ");
			String[] ampStringParts = ionChamberParams.getOffset().split(" ");
			try {
				InterfaceProvider.getTerminalPrinter().print(
						"Changing sensitivity of " + ionChamberParams.getName() + " to " + ionChamberParams.getGain());

				sensitivities[index].moveTo(gainStringParts[0]);
				sensitivity_units[index].moveTo(gainStringParts[1]);
				offsets[index].moveTo(ampStringParts[0]);
				offset_units[index].moveTo(ampStringParts[1]);
			} catch (Exception e) {
				InterfaceProvider.getTerminalPrinter().print(
						"Exception while trying to change the sensitivity of ion chamber" + ionChamberParams.getName());
				InterfaceProvider
						.getTerminalPrinter()
						.print("Set the ion chamber sensitivity manually, uncheck the box in the Detector Parameters editor and restart the scan");
				InterfaceProvider.getTerminalPrinter().print("Please report this problem to Data Acquisition");
				throw e;
			}
		}
	}

	protected void control_mythen(IExperimentDetectorParameters fluoresenceParameters, IOutputParameters outputBean,
			String experimentFullPath) throws Exception {

		String experimentFolderName = experimentFullPath.substring(experimentFullPath.indexOf("xml") + 4,
				experimentFullPath.length());
		String nexusSubFolder = experimentFolderName + "/" + outputBean.getNexusDirectory();
		String asciiSubFolder = experimentFolderName + "/" + outputBean.getAsciiDirectory();
		String mythenSubFolder = Paths.get(experimentFolderName, "mythen").toString();

		InterfaceProvider.getTerminalPrinter().print("Moving DCM for Mythen image...");

		// Save currently set mythen subdirectory - so it can be set back to original value after the scan
		String mythenSubdirectoryBeforeScan = mythen_scannable.getSubDirectory();

		energy_scannable.moveTo(fluoresenceParameters.getMythenEnergy());

		mythen_scannable.setCollectionTime(fluoresenceParameters.getMythenTime());
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
		logger.debug("Detectors to use in scan : {}", bufferedDetectorNames);
		return createBufferedDetArray(bufferedDetectorNames);
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
			return bufferedDetectorNameMap.entrySet().stream().
					filter(bufDet -> detectorList.contains(bufDet.getKey())).
					map(Entry::getValue).
					collect(Collectors.toList());

		} else {
			return Collections.emptyList();
		}
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
		map.put("medipix", "qexafs_medipix");
		map.put("FFI0", "QexafsFFI0");
		map.put("FFI0_vortex", "VortexQexafsFFI0");
		map.put("FFI0_xspress3", "qexafs_FFI0_xspress3");
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
}