/*-
 * Copyright © 2015 Diamond Light Source Ltd.
 *
 * This file is part of GDA.
 *
 * GDA is free software: you can redistribute it and/or modify it under the
 * terms of the GNU General Public License version 3 as published by the Free
 * Software Foundation.
 *
 * GDA is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
 * details.
 *
 * You should have received a copy of the GNU General Public License along
 * with GDA. If not, see <http://www.gnu.org/licenses/>.
 */
package uk.ac.gda.server.exafs.scan.preparers;

import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;

import org.apache.commons.io.FilenameUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.DetectorHdfFunctions;
import gda.device.detector.NXDetector;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.detector.nxdetector.NXPluginBase;
import gda.device.detector.nxdetector.roi.MutableRectangularIntegerROI;
import gda.device.detector.xmap.TfgXMapFFoverI0;
import gda.device.detector.xmap.Xmap;
import gda.device.scannable.TopupChecker;
import gda.exafs.scan.ExafsScanPointCreator;
import gda.exafs.scan.XanesScanPointCreator;
import uk.ac.gda.beans.exafs.DetectorConfig;
import uk.ac.gda.beans.exafs.DetectorParameters;
import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.IonChamberParameters;
import uk.ac.gda.beans.exafs.SpectrometerScanParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
import uk.ac.gda.beans.exafs.i20.I20OutputParameters;
import uk.ac.gda.beans.xspress.XspressParameters;
import uk.ac.gda.devices.detector.FluorescenceDetectorParameters;
import uk.ac.gda.server.exafs.scan.DetectorPreparer;
import uk.ac.gda.server.exafs.scan.DetectorPreparerDelegate;
import uk.ac.gda.server.exafs.scan.DetectorPreparerFunctions;
import uk.ac.gda.util.beans.xml.XMLHelpers;

public class I20DetectorPreparer extends DetectorPreparerDelegate implements DetectorPreparer {

	private static final Logger logger = LoggerFactory.getLogger(I20DetectorPreparer.class);

	private Detector selectedXspressDetector;

	private TfgScalerWithFrames ionchambers;
	private TfgScalerWithFrames i1;
	private TfgXMapFFoverI0 ffI1;

	private Xmap xmap;
	private NXDetector medipix;
	private TopupChecker topupChecker;
	private IScanParameters scanBean;

	private String experimentXmlFullPath;
	private String hdfFilePathBeforeScan;

	private IOutputParameters outputBean;

	private DetectorPreparerFunctions detectorPreparerFunctions = new DetectorPreparerFunctions();

	private boolean correctForDarkCurrent = true;

	public I20DetectorPreparer(Scannable[] sensitivities, Scannable[] sensitivity_units,
			Scannable[] offsets, Scannable[] offset_units, TfgScalerWithFrames ionchambers, TfgScalerWithFrames I1,
			NXDetector medipix, TopupChecker topupChecker) {
		selectedXspressDetector = null;
		detectorPreparerFunctions.setSensitivities(sensitivities);
		detectorPreparerFunctions.setSensitivityUnits(sensitivity_units);
		detectorPreparerFunctions.setOffsets(offsets);
		detectorPreparerFunctions.setOffsetUnits(offset_units);
		this.ionchambers = ionchambers;
		this.i1 = I1;
		this.medipix = medipix;
		this.topupChecker = topupChecker;
	}

	public List<Detector> getDetectors() {
		ArrayList<Detector> detectors = new ArrayList<Detector>();
		detectors.add(selectedXspressDetector);
		detectors.add(ionchambers);
		detectors.add(i1);
		detectors.add(xmap);
		detectors.add(medipix);
		return detectors;
	}

	private void setI1TimeFormatRequired(boolean timeRequired) {
		if (timeRequired) {
			logger.debug("Switching time values ON for I1");
			i1.setTimeChannelRequired(true);
			i1.setOutputFormat(new String[]{"%.4f", "%.4f", "%.2f"});
			i1.setExtraNames(new String[]{"Time", "I1"});
			ffI1.setI0_channel(1);
		} else {
			logger.debug("Switching time values OFF for I1");
			i1.setTimeChannelRequired(false);
			i1.setOutputFormat(new String[]{"%.4f", "%.4f"});
			i1.setExtraNames(new String[]{"I1"});
			ffI1.setI0_channel(0);
		}
	}

	/**
	 * Set Xspress parameterParameters options using values from I20OutputParameters options.
	 * (save raw spectrum, only show FF, show deadtime correction values, save raw spectrum)
	 * @param detectorParams
	 * @param outputParams
	 */
	public void setXspressOutputOptions(FluorescenceDetectorParameters detectorParams, IOutputParameters outputParams) {
		if (detectorParams instanceof XspressParameters xspressParameters && outputParams instanceof I20OutputParameters outParams) {
			xspressParameters.setSaveRawSpectrum(outParams.isXspressSaveRawSpectrum());
			xspressParameters.setOnlyShowFF(outParams.isXspressOnlyShowFF());
			xspressParameters.setShowDTRawValues(outParams.isXspressShowDTRawValues());
			xspressParameters.setSaveRawSpectrum(outParams.isXspressSaveRawSpectrum());
		}
	}

	private String getNexusDataFullPath() {
		String folder = experimentXmlFullPath.replace("/xml/", "/");
		return FilenameUtils.getFullPathNoEndSeparator(folder)+"/nexus/";
	}

	private void configureFluoDetector(String xmlFileName) throws Exception {
		FluorescenceDetectorParameters params = detectorPreparerFunctions.getDetectorParametersBean(xmlFileName);
		setXspressOutputOptions(params, outputBean);
		Detector configuredDetector = detectorPreparerFunctions.configureDetector(params);
		detectorPreparerFunctions.setConfigFilename(configuredDetector, xmlFileName);

		if (configuredDetector instanceof Xmap xmap) {
			this.xmap = xmap;
		} else {
			selectedXspressDetector = configuredDetector;
			hdfFilePathBeforeScan = DetectorHdfFunctions.setHdfFilePath(selectedXspressDetector, getNexusDataFullPath());
		}
	}

	@Override
	public void configure(IScanParameters scanBean, IDetectorParameters detectorBean, IOutputParameters outputBean,
			String experimentFullPath) throws Exception {

		this.scanBean = scanBean;
		this.experimentXmlFullPath = experimentFullPath;
		this.outputBean = outputBean;

		runConfigure(scanBean, detectorBean, outputBean, experimentFullPath);

		detectorPreparerFunctions.clear();

		if (useNewDetectorConfiguration(detectorBean)) {
			prepareDetectors(detectorBean.getDetectorConfigurations());
			return;
		}

		String experimentType = detectorBean.getExperimentType();
		selectedXspressDetector = null;

		// Get the detector parameters
		FluorescenceParameters fluorescenceParameters = null;
		if (experimentType.equals(DetectorParameters.FLUORESCENCE_TYPE)) {
			fluorescenceParameters = detectorBean.getFluorescenceParameters();
		} else if (experimentType.equals(DetectorParameters.XES_TYPE)) {
			fluorescenceParameters = detectorBean.getXesParameters();
		}

		// No fluorescence parameters for Transmission experiments
		if (fluorescenceParameters != null) {
			String xmlFileName = Paths.get(experimentFullPath, fluorescenceParameters.getConfigFileName()).toString();
				configureFluoDetector(xmlFileName);
		}
		List<IonChamberParameters> ionChamberParamsArray = detectorBean.getIonChambers();
		if (ionChamberParamsArray != null) {
			for (IonChamberParameters ionChamberParams : ionChamberParamsArray) {
				int index = getIonChamberIndex(ionChamberParams);
				detectorPreparerFunctions.setupAmplifierSensitivity(ionChamberParams, index);
			}
		}
	}

	private boolean useNewDetectorConfiguration(IDetectorParameters detectorParams) {
		return detectorParams != null &&
				detectorParams.getDetectorConfigurations() != null &&
				!detectorParams.getDetectorConfigurations().isEmpty();
	}

	/**
	 * Configure the detectors using new detector parameter settings
	 *
	 * @param detectorConfigs
	 */
	private void prepareDetectors(List<DetectorConfig> detectorConfigs) {
		detectorPreparerFunctions.setConfigFileDirectory(experimentXmlFullPath);
		detectorPreparerFunctions.setDataDirectory(experimentXmlFullPath.replace("/xml/", "/"));
		detectorPreparerFunctions.configure(detectorConfigs);
	}

	@Override
	public void beforeEachRepetition() throws Exception {
		if (isXesMode()) {
			setI1TimeFormatRequired(true);
		}

		runBeforeEachRepetition();

		// Make sure timeframes, dark current collection time are set on ionchambers before each rep. of main scan
		setUpIonChambers();
	}

	@Override
	public Detector[] getExtraDetectors() {
		return null;
	}

	@Override
	public void completeCollection() {

		runCompleteCollection();

		topupChecker.setCollectionTime(0.0);
		setI1TimeFormatRequired(true);

		// restore detector states configured using new detector parameters
		detectorPreparerFunctions.restoreDetectorState();

		// Set the hdf directory back to the 'before scan' value
		if (selectedXspressDetector != null) {
			setDetectorHdfPath(selectedXspressDetector, hdfFilePathBeforeScan);
		}

		i1.setDarkCurrentRequired(true);
		ionchambers.setDarkCurrentRequired(true);
	}

	/**
	 * Set hdf path on a detector by calling {@link DetectorHdfFunctions#setHdfFilePath(Detector, String)}.
	 * Catches any exception thrown and logs the error message.
	 * @param detector
	 * @param path
	 */
	private void setDetectorHdfPath(Detector detector, String path) {
		try {
			DetectorHdfFunctions.setHdfFilePath(detector, path);
		} catch (DeviceException e) {
			logger.error("Problem setting hdf directory to {} for detector {}", path, detector.getName(), e);
		}
	}

	private int getIonChamberIndex(IonChamberParameters ionChamberParams) throws Exception {
		String ionChamberName = ionChamberParams.getName();
		int index = 0;
		if (ionChamberName.equalsIgnoreCase("It")) {
			index = 1;
		} else if (ionChamberName.equalsIgnoreCase("Iref")) {
			index = 2;
		} else if (ionChamberName.equalsIgnoreCase("I1")) {
			index = 3;
		}
		return index;
	}

	private Double[] createTimeArray(XesScanParameters xesParams) throws Exception {
		if (xesParams.scanUsesXasXanesFile()) {
			var scanFileBean = (IScanParameters) XMLHelpers.getBean(Paths.get(experimentXmlFullPath).resolve(xesParams.getXasXanesFileName()).toFile());
			return createTimeArray(scanFileBean);
		} else {
			// Scan using spectrometer : SCAN_XES_FIXED_MONO, (SCAN_XES_REGION?), or (2d) SCAN_XES_SCAN_MONO/
			SpectrometerScanParameters scanParams = xesParams.getPrimarySpectrometerScanParams();
			return  new Double[]{scanParams.getIntegrationTime()};
		}
	}

	private boolean scanUsesXasXanesFile() {
		if (scanBean instanceof XanesScanParameters || scanBean instanceof XasScanParameters) {
			return true;
		} else if (scanBean instanceof XesScanParameters xesParams) {
			return xesParams.scanUsesXasXanesFile();
		}
		return false;
	}

	private Double[] createTimeArray(IScanParameters scanParams) throws Exception {
		if (scanParams instanceof XanesScanParameters p) {
			return XanesScanPointCreator.getScanTimeArray(p);
		}
		else if (scanParams instanceof XasScanParameters p) {
			return ExafsScanPointCreator.getScanTimeArray(p);
		}
		return new Double[] {};
	}

	/**
	 * Setup time frames required for scan and dark current collection time from max time per point, and apply to
	 * ion chambers (I1 for xes mode, ionchambers for XAS mode).
	 * Also set mono optimiser with correct ionchamber to use during bragg offset optimisation scans.
	 * @throws Exception
	 */
	private void setUpIonChambers() throws Exception {
		Double[] tfgFrameTimes = null;

		if (scanBean instanceof XanesScanParameters || scanBean instanceof XasScanParameters) {
			tfgFrameTimes = createTimeArray(scanBean);
		} else if (scanBean instanceof XesScanParameters p) {
			tfgFrameTimes = createTimeArray(p);
		}

		if (tfgFrameTimes == null) {
			throw new IllegalArgumentException("Could not generate Tfg frame times for scan bean of type "+scanBean.getClass().getCanonicalName());
		}

		// Determine max collection time
		double maxTime = Stream.of(tfgFrameTimes).mapToDouble(d->d).max().orElse(0.0);

		ionchambers.setDarkCurrentRequired(correctForDarkCurrent);
		i1.setDarkCurrentRequired(correctForDarkCurrent);

		// set dark current time and handle any errors here
		if (maxTime > 0) {
			ionchambers.setDarkCurrentCollectionTime(maxTime);
			i1.setDarkCurrentCollectionTime(maxTime);
			topupChecker.setCollectionTime(maxTime);
		}

		// Always want time switched off if doing Xas/Xanes/Region scans
		// These use XasScannable includes the Time field already
		if (scanUsesXasXanesFile()) {
			setI1TimeFormatRequired(false);
		} else {
			setI1TimeFormatRequired(true);
		}

		if (isXesMode()) {
			i1.clearFrameSets();
			if (tfgFrameTimes.length>1) {
				i1.setTimes(tfgFrameTimes);
			} else {
				i1.setCollectionTime(tfgFrameTimes[0]);
			}
		} else {
			ionchambers.clearFrameSets();
			ionchambers.setTimes(tfgFrameTimes);
		}

	}

	public void setFFI1(TfgXMapFFoverI0 ffI1) {
		this.ffI1 = ffI1;
	}

	public TfgXMapFFoverI0 getFFI1() {
		return ffI1;
	}

	public Detector getSelectedXspressDetector() {
		return selectedXspressDetector;
	}

	public Xmap getXMap() {
		return xmap;
	}

	public void setXMap(Xmap xmap) {
		this.xmap = xmap;
	}

	public boolean isXesMode() {
		return scanBean instanceof XesScanParameters;
	}

	public void setPluginsForMutableRoi(NXDetector detector, List<NXPluginBase> pluginsForMutableRoi) {
		detectorPreparerFunctions.setMutableRoiPluginList(detector, pluginsForMutableRoi);
	}

	public void setMutableRoi(NXDetector detector, MutableRectangularIntegerROI mutableRoi) {
		detectorPreparerFunctions.setMutableRoiForMedipix(detector, mutableRoi);
	}

	public boolean isCorrectForDarkCurrent() {
		return correctForDarkCurrent;
	}

	public void setCorrectForDarkCurrent(boolean correctForDarkCurrent) {
		this.correctForDarkCurrent = correctForDarkCurrent;
	}
}
