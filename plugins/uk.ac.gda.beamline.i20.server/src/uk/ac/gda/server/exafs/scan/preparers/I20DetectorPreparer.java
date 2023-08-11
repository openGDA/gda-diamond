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

import java.io.File;
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
import uk.ac.gda.beamline.i20.scannable.MonoMoveWithOffsetScannable;
import uk.ac.gda.beamline.i20.scannable.MonoOptimisation;
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
import uk.ac.gda.server.exafs.scan.BeamlinePreparer;
import uk.ac.gda.server.exafs.scan.DetectorPreparer;
import uk.ac.gda.server.exafs.scan.DetectorPreparerFunctions;
import uk.ac.gda.util.beans.xml.XMLHelpers;

public class I20DetectorPreparer implements DetectorPreparer {

	private static final Logger logger = LoggerFactory.getLogger(I20DetectorPreparer.class);

	private Detector selectedXspressDetector;

	private TfgScalerWithFrames ionchambers;
	private TfgScalerWithFrames i1;
	private TfgXMapFFoverI0 ffI1;

	private Xmap vortex;
	private NXDetector medipix;
	private TopupChecker topupChecker;
	private IScanParameters scanBean;

	private String experimentXmlFullPath;
	private String hdfFilePathBeforeScan;

	private boolean xesMode = false;

	private MonoOptimisation monoOptimiser;

	private IOutputParameters outputBean;

	private DetectorPreparerFunctions detectorPreparerFunctions = new DetectorPreparerFunctions();

	private boolean correctForDarkCurrent = true;

	private Scannable ionchamberChecker = null;

	private boolean runIonchamberChecker;

	public I20DetectorPreparer(Scannable[] sensitivities, Scannable[] sensitivity_units,
			Scannable[] offsets, Scannable[] offset_units, TfgScalerWithFrames ionchambers, TfgScalerWithFrames I1,
			Xmap vortex, NXDetector medipix, TopupChecker topupChecker) {
		selectedXspressDetector = null;
		detectorPreparerFunctions.setSensitivities(sensitivities);
		detectorPreparerFunctions.setSensitivityUnits(sensitivity_units);
		detectorPreparerFunctions.setOffsets(offsets);
		detectorPreparerFunctions.setOffsetUnits(offset_units);
		this.ionchambers = ionchambers;
		this.i1 = I1;
		this.vortex = vortex;
		this.medipix = medipix;
		this.topupChecker = topupChecker;
	}

	public List<Detector> getDetectors() {
		ArrayList<Detector> detectors = new ArrayList<Detector>();
		detectors.add(selectedXspressDetector);
		detectors.add(ionchambers);
		detectors.add(i1);
		detectors.add(vortex);
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
			vortex = xmap;
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
		try {
			runIonchamberChecker();
		} catch (Exception e) {
			// catch any exceptions so we can attempt the rest of the setup
			logger.warn("Problem encountered running ion chamber checker {}. Continuing with the rest of the setup as normal.", e.getMessage(), e);
		}

		doMonoOptimisation();

		// Make sure timeframes, dark current collection time are set on ionchambers before each rep. of main scan
		setUpIonChambers();
	}

	public void runIonchamberChecker() throws DeviceException {
		if (!isRunIonchamberChecker()) {
			return;
		}
		if (ionchamberChecker == null) {
			logger.warn("Cannot run ionchamber checker - the checker object has not been set");
			return;
		}
		logger.info("Running ionchamber check using {} object", ionchamberChecker.getName());
		ionchamberChecker.atScanStart();
	}

	@Override
	public Detector[] getExtraDetectors() {
		return null;
	}

	@Override
	public void completeCollection() {
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
		xesMode = false;
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

	private int getWholeNumSteps(double rangeFloat, double stepSize) {
		int wholeNumber = (int) Math.floor(rangeFloat / stepSize);
		double remainder = rangeFloat % stepSize;
		// Increment count if remainder is very similar in size to to stepsize
		if (Math.abs(remainder - stepSize) < 1e-6) {
			wholeNumber += 1;
		}
		return wholeNumber;
	}

	private int getNumStepsXes(SpectrometerScanParameters xesParams) {
		double xesEnergyRange = xesParams.getFinalEnergy() - xesParams.getInitialEnergy();
		return 1 + getWholeNumSteps(xesEnergyRange, xesParams.getStepSize());
	}

	private int getNumStepsMono(XesScanParameters xesParams) {
		if (xesParams.getScanType() == XesScanParameters.SCAN_XES_FIXED_MONO) {
			return 1;
		} else {
			double monoEnergyRange = xesParams.getMonoFinalEnergy() - xesParams.getMonoInitialEnergy();
			return 1 + getWholeNumSteps(monoEnergyRange, xesParams.getMonoStepSize());
		}
	}

	private Double[] getScanTimeArray(XesScanParameters xesParams) throws Exception {
		Double[] timeValues = null;

		int scanType = xesParams.getScanType();

		if (scanType == XesScanParameters.FIXED_XES_SCAN_XANES || scanType == XesScanParameters.FIXED_XES_SCAN_XAS) {
			// Fixed XES, scan mono : Load bean with Xas, Xanes settings, create time array values from it
			Object bean = getXesMonoScanBean(xesParams);
			if (bean instanceof XasScanParameters monoScanBean) {
				timeValues = ExafsScanPointCreator.getScanTimeArray(monoScanBean);
			} else if (bean instanceof XanesScanParameters monoScanBean) {
				timeValues = XanesScanPointCreator.getScanTimeArray(monoScanBean);
			}
		} else {
			// Scan using spectrometer : SCAN_XES_FIXED_MONO, (SCAN_XES_REGION?), or (2d) SCAN_XES_SCAN_MONO/
			SpectrometerScanParameters scanParams = xesParams.getPrimarySpectrometerScanParams();
			Double collectionTime = scanParams.getIntegrationTime();
			int numStepsXes = getNumStepsXes(scanParams);
			int numStepsMono = getNumStepsMono(xesParams);
			return new Double[]{collectionTime};

//			timeValues = new Double[numStepsMono * numStepsXes];
//			Arrays.fill(timeValues, collectionTime);
		}

		return timeValues;
	}

	/**
	 * Setup time frames required for scan and dark current collection time from max time per point, and apply to
	 * ion chambers (I1 for xes mode, ionchambers for XAS mode).
	 * Also set mono optimiser with correct ionchamber to use during bragg offset optimisation scans.
	 * @throws Exception
	 */
	private void setUpIonChambers() throws Exception {
		Double[] tfgFrameTimes = null;

		if (scanBean instanceof XanesScanParameters p) {
			tfgFrameTimes = XanesScanPointCreator.getScanTimeArray(p);
		}
		else if (scanBean instanceof XasScanParameters p) {
			tfgFrameTimes = ExafsScanPointCreator.getScanTimeArray(p);
		}
		else if (scanBean instanceof XesScanParameters p) {
			tfgFrameTimes = getScanTimeArray(p);
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
		// (XasScannable includes the Time field already)
		if (scanBean instanceof XasScanParameters || scanBean instanceof XanesScanParameters) {
			setI1TimeFormatRequired(false);
		} else {
			setI1TimeFormatRequired(true);
		}
		if (xesMode) {
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

	public MonoOptimisation getMonoOptimiser() {
		return monoOptimiser;
	}

	public void setMonoOptimiser(MonoOptimisation monoOptimiser) {
		this.monoOptimiser = monoOptimiser;
	}

	private MonoEnergyRange getMonoRange(XasScanParameters bean) {
		return new MonoEnergyRange(bean.getInitialEnergy(), bean.getFinalEnergy());
	}

	private MonoEnergyRange getMonoRange(XanesScanParameters bean) throws DeviceException {
		if (xesMode) {
			if (bean.getScannableName().equals(monoOptimiser.getBraggScannable().getName())) {
				return new MonoEnergyRange(bean.getInitialEnergy(), bean.getFinalEnergy());
			} else {
				// Xes mode with Energy region scan for spectrometer energy : mono is already in correct position
				double braggEnergy = (double) monoOptimiser.getBraggScannable().getPosition();
				return new MonoEnergyRange(braggEnergy, braggEnergy);
			}
		}
		return new MonoEnergyRange(bean.getInitialEnergy(), bean.getFinalEnergy());
	}

	private Object getXesMonoScanBean(XesScanParameters bean) throws Exception {
		Object monoScanBean = null;
		try {
			monoScanBean = XMLHelpers.getBean(new File(bean.getScanFileName()));
		} catch (Exception e) {
			throw new Exception("Problem loading XML file "+bean.getScanFileName()+" for XesScan", e);
		}
		return monoScanBean;
	}

	private MonoEnergyRange getMonoRange(XesScanParameters bean) throws Exception {
		int scanType = bean.getScanType();
		if (scanType == XesScanParameters.SCAN_XES_FIXED_MONO || scanType == XesScanParameters.SCAN_XES_REGION_FIXED_MONO) {
			return new MonoEnergyRange(bean.getMonoEnergy(), bean.getMonoEnergy());
		}else if (scanType == XesScanParameters.SCAN_XES_SCAN_MONO) {
			return new MonoEnergyRange(bean.getMonoInitialEnergy(), bean.getMonoFinalEnergy());
		}else{
			// XAS or XANES mono scan
			// load the xml bean of scan settings
			Object monoScanBean = getXesMonoScanBean(bean);
			if (monoScanBean instanceof XasScanParameters p) {
				return getMonoRange(p);
			}else if (monoScanBean instanceof XanesScanParameters p) {
				return getMonoRange(p);
			}
		}

		return null;
	}

	private static class MonoEnergyRange {
		private final double lowEnergy;
		private final double highEnergy;

		public MonoEnergyRange(double lowEnergy, double highEnergy) {
			this.lowEnergy = lowEnergy;
			this.highEnergy = highEnergy;
		}

		public double getLowEnergy() {
			return lowEnergy;
		}
		public double getHighEnergy() {
			return highEnergy;
		}
	}

	/**
	 * Set loop and scan type on MonoMoveWithOffset scannable - for XES mode scans.
	 * @param scanBean , XesScanParameters; use null to set scantype = 0 and looptype="" (back to defaults)
	 */
	private void setScanLoopType(XesScanParameters scanBean) {
		if (monoOptimiser.getBraggScannable() instanceof MonoMoveWithOffsetScannable monoWithOffset) {
			if (scanBean!=null) {
				monoWithOffset.setScanType(scanBean.getScanType());
				monoWithOffset.setLoopType(scanBean.getLoopChoice());
			}else {
				monoWithOffset.setScanType(0);
				monoWithOffset.setLoopType("");
			}
		}
	}

	private boolean monoMoves(int scanType) {
		return scanType == XesScanParameters.SCAN_XES_SCAN_MONO || scanType == XesScanParameters.FIXED_XES_SCAN_XANES
				|| scanType == XesScanParameters.FIXED_XES_SCAN_XAS;
	}

	private boolean xesMoves(int scanType) {
		return scanType == XesScanParameters.SCAN_XES_SCAN_MONO || scanType == XesScanParameters.SCAN_XES_FIXED_MONO;
	}

	/**
	 * Set 2D XES num steps per inner loop on MonoMoveWithOffset scannable
	 * @param xesParams
	 */
	private void setLoopSizes(XesScanParameters xesParams) {
		if (monoOptimiser.getBraggScannable() instanceof MonoMoveWithOffsetScannable monoWithOffset) {

			SpectrometerScanParameters specParams = xesParams.getActiveSpectrometerParameters().values().iterator().next();
			int numStepsXes = getNumStepsXes(specParams);
			int numStepsMono = getNumStepsMono(xesParams);

			int numStepsPerInnerLoop = 0, numStepsPerOuterLoop = 0;
			int scanType = xesParams.getScanType();
			if (xesParams.getScanType()==XesScanParameters.SCAN_XES_SCAN_MONO) {
				String loopType = xesParams.getLoopChoice();
				if (loopType.equals(XesScanParameters.EF_OUTER_MONO_INNER)) {
					numStepsPerOuterLoop = numStepsXes;
					numStepsPerInnerLoop = numStepsMono;
				} else if (loopType.equals(XesScanParameters.MONO_OUTER_EF_INNER)) {
					numStepsPerOuterLoop = numStepsMono;
					numStepsPerInnerLoop = numStepsXes;
				}
			} else {
				if (monoMoves(scanType)) {
					numStepsPerInnerLoop = numStepsMono;
				}else if (xesMoves(scanType)) {
					numStepsPerInnerLoop = numStepsXes;
				}
			}
			// set time per step (all same length for 2d scans)
			monoWithOffset.setTimePerStepInnerLoop(specParams.getIntegrationTime());
			monoWithOffset.setNumStepsPerInnerLoop(numStepsPerInnerLoop);
		}
	}


	/**
	 * Run mono optimisation scan (i.e. adjust bragg offset for start and end scan energies to maximise signal
	 * on the detector and set appropriate fitting parameters to be used to adjust the offset during an energy scan).<p>
	 * This is not really a 'detector preparer' type of method, but need to do it here since it should (optionally) be run
	 * at the start of each scan/repetition and there are currently no beforeRepetition methods in the {@link BeamlinePreparer} interface.
	 * @throws Exception
	 */
	private void doMonoOptimisation() throws Exception {
		if (monoOptimiser == null) {
			return;
		}

		// Set the ionchamber to use to make measurement
		if (xesMode) {
			monoOptimiser.setScannableToMonitor(i1);
			setI1TimeFormatRequired(true); // always include time, even if not used for main XES scan
		} else {
			monoOptimiser.setScannableToMonitor(ionchambers);
		}

		MonoEnergyRange monoEnergyRange = null;
		boolean is2dScan = false;
		if (scanBean instanceof XanesScanParameters params) {
			monoEnergyRange = getMonoRange(params);
		} else if (scanBean instanceof XasScanParameters params) {
			monoEnergyRange = getMonoRange(params);
		} else if (scanBean instanceof XesScanParameters params) {
			monoEnergyRange = getMonoRange(params);
			is2dScan = params.getScanType() == XesScanParameters.SCAN_XES_SCAN_MONO;
		}

		setScanLoopType(null); // reset scan and loop type on the bragg1WIthOffset before doing optimisation scan

		if (monoEnergyRange!=null && monoOptimiser.getAllowOptimisation()) {
			if (!is2dScan) {

				if (Math.abs(monoEnergyRange.getLowEnergy() - monoEnergyRange.getHighEnergy()) < 1e-3) {
					logger.info("Running monochromator optimisation for single mono energy : low energy = high energy = {}",
							monoEnergyRange.getLowEnergy());
					monoOptimiser.optimise(monoEnergyRange.getLowEnergy(), monoEnergyRange.getLowEnergy());
				} else if (monoEnergyRange.getLowEnergy() > 0
						&& monoEnergyRange.getHighEnergy() > monoEnergyRange.getLowEnergy()) {
					logger.info("Running monochromator optimisation for XAS/XANES scan : low energy = {}, high energy = {}",
							monoEnergyRange.getLowEnergy(), monoEnergyRange.getHighEnergy());
					monoOptimiser.optimise(monoEnergyRange.getLowEnergy(), monoEnergyRange.getHighEnergy());
				}
				// move to low energy again, with optimised bragg offset
				monoOptimiser.getBraggScannable().moveTo(monoEnergyRange.getLowEnergy());
			}
			else {
				// move to near low energy, so that first moveTo also calls optimisation
				monoOptimiser.getBraggScannable().moveTo(monoEnergyRange.getLowEnergy()+0.2);
			}
		}
		// Set the scan type and inner/outer loop sizes on monoOptimiser, so that
		// optimisation can be done at correct time.
		if (scanBean instanceof XesScanParameters scanParams) {
			setScanLoopType(scanParams);
			setLoopSizes(scanParams);
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

	public Xmap getVortex() {
		return vortex;
	}

	public void setVortex(Xmap vortex) {
		this.vortex = vortex;
	}

	public void setXesMode(boolean xesMode) {
		this.xesMode = xesMode;
	}

	public boolean isXesMode() {
		return xesMode;
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

	public Scannable getIonchamberChecker() {
		return ionchamberChecker;
	}

	public void setIonchamberChecker(Scannable ionchamberChecker) {
		this.ionchamberChecker = ionchamberChecker;
	}

	public boolean isRunIonchamberChecker() {
		return runIonchamberChecker;
	}

	public void setRunIonchamberChecker(boolean runIonchamberChecker) {
		this.runIonchamberChecker = runIonchamberChecker;
	}
}
