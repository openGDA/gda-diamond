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
import java.util.Arrays;
import java.util.List;

import org.apache.commons.io.FilenameUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.DetectorHdfFunctions;
import gda.device.detector.NXDetector;
import gda.device.detector.areadetector.v17.NDPluginBase;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.detector.nxdetector.NXPluginBase;
import gda.device.detector.nxdetector.roi.ImutableRectangularIntegerROI;
import gda.device.detector.nxdetector.roi.MutableRectangularIntegerROI;
import gda.device.detector.xmap.TfgXMapFFoverI0;
import gda.device.detector.xmap.Xmap;
import gda.device.scannable.TopupChecker;
import gda.epics.CAClient;
import gda.exafs.scan.ExafsScanPointCreator;
import gda.exafs.scan.XanesScanPointCreator;
import uk.ac.gda.beamline.i20.scannable.MonoMoveWithOffsetScannable;
import uk.ac.gda.beamline.i20.scannable.MonoOptimisation;
import uk.ac.gda.beans.exafs.DetectorGroup;
import uk.ac.gda.beans.exafs.DetectorParameters;
import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.IonChamberParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
import uk.ac.gda.beans.exafs.i20.I20OutputParameters;
import uk.ac.gda.beans.medipix.MedipixParameters;
import uk.ac.gda.beans.medipix.ROIRegion;
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

	private String medipixDefaultBasePvName="BL20I-EA-DET-05";
	private String roiPvName = "ROI1:";
	private String medipixHdfPathTemplate = "";

	// Full path to xml folder containing experiment xml files
	private String experimentXmlFullPath;
	private String hdfFilePathBeforeScan;

	// Plugins for setting ROI on medipix
	private boolean configureMedipixRois = true;
	private List<NXPluginBase> originalMedipixPlugins = null;
	private List<NXPluginBase> pluginsForMutableRoi = null;
	private MutableRectangularIntegerROI mutableRoi = null;

	private boolean xesMode = false;

	private MonoOptimisation monoOptimiser;

	private IOutputParameters outputBean;

	private DetectorPreparerFunctions detectorPreparerFunctions = new DetectorPreparerFunctions();

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
//		detectors.add(ffI0);
		return detectors;
	}

	public void setI1TimeFormatRequired(boolean timeRequired) {
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
		if (detectorParams instanceof XspressParameters && outputParams instanceof I20OutputParameters) {
			XspressParameters xspressParameters = (XspressParameters) detectorParams;
			I20OutputParameters outParams = (I20OutputParameters) outputParams;

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

		if (configuredDetector instanceof Xmap) {
			vortex = (Xmap) configuredDetector;
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

		String experimentType = detectorBean.getExperimentType();
		xesMode = experimentType.startsWith(DetectorParameters.XES_TYPE);
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
			// See if detector group to be used contains medipix - this is configured differently to FluorescenceDetector

			// name of detector group to use - this is the detectorType field in the xes/transmission/fluorescence bean
			String detGroupToUse = fluorescenceParameters.getDetectorType();
			boolean useMedipixDetector = false;
			// see if detectors listed in detector group contains medipix
			for(DetectorGroup detGroup : detectorBean.getDetectorGroups()) {
				if (detGroup.getName().equalsIgnoreCase(detGroupToUse) ) {
					for(String detName : detGroup.getDetector()) {
						if (detName.toUpperCase().contains(FluorescenceParameters.MEDIPIX_DET_TYPE.toUpperCase())) {
							useMedipixDetector = true;
						}
					}
				}
			}

			// Configure the detector
			medipixHdfPathTemplate = "";
			String xmlFileName = Paths.get(experimentFullPath, fluorescenceParameters.getConfigFileName()).toString();
			if (useMedipixDetector) {
				setupMedipixHdfPaths();
				if (configureMedipixRois) {
					configureMedipix(xmlFileName);
				}
			} else {
				configureFluoDetector(xmlFileName);
			}
		}
		List<IonChamberParameters> ionChamberParamsArray = detectorBean.getIonChambers();
		if (ionChamberParamsArray != null) {
			for (IonChamberParameters ionChamberParams : ionChamberParamsArray) {
				int index = getIonChamberIndex(ionChamberParams);
				detectorPreparerFunctions.setupAmplifierSensitivity(ionChamberParams, index);
			}
		}
	}
	/**
	 * Setup medipix ROI using values from xml file.
	 * The medipix detector 'additional plugin' list is set to use one with mutable ROI.
	 * Original plugin list is restored at end of the scan.
	 *
	 * @param xmlFileName
	 * @throws Exception
	 */
	private void configureMedipix(String xmlFileName) throws Exception {
		// Create bean from XML
		MedipixParameters param = XMLHelpers.createFromXML(MedipixParameters.mappingURL, MedipixParameters.class, MedipixParameters.schemaURL, new File(xmlFileName));

		// Create region using first ROI only - currently camera uses only one ROI
		ROIRegion region1 = param.getRegionList().get(0);
		int xstart = region1.getXRoi().getRoiStart();
		int xsize = region1.getXRoi().getRoiEnd() - xstart;
		int ystart = region1.getYRoi().getRoiStart();
		int ysize = region1.getYRoi().getRoiEnd() - ystart;

		// Save the original additional plugin list, so it can be restored at end of the scan
		originalMedipixPlugins = medipix.getAdditionalPluginList();

		// Set the plugin list to use one with a mutable ROI
		medipix.setAdditionalPluginList(pluginsForMutableRoi);

		// Set the ROI
		mutableRoi.setROI(new ImutableRectangularIntegerROI(xstart, ystart, xsize, ysize, region1.getRoiName() ));

		// Set ROI min callback time to zero (otherwise might start to miss frames if acquisition time is < callback time)
		CAClient.put(medipixDefaultBasePvName+":"+roiPvName+NDPluginBase.MinCallbackTime, 0);

		// Set medipix acquisition time for XES scan in dummy mode - so scans work properly and frames stay in sync with scan.
		// Readout time should also be set to zero, so that exposure time = acquisition time. 12/7/2017
		if (LocalProperties.isDummyModeEnabled()){
			double xesIntegrationTime = getXesIntegrationTime();
			if (xesIntegrationTime>0) {
				medipix.setCollectionTime(xesIntegrationTime);
			}
		}
	}

	private void setupMedipixHdfPaths() throws DeviceException {
		String newPathTemplate = experimentXmlFullPath.replaceFirst("(.*)xml", "\\$datadir\\$") + "nexus/";
		medipixHdfPathTemplate = DetectorHdfFunctions.setHdfFilePath(medipix, newPathTemplate);
	}

	@Override
	public void beforeEachRepetition() throws Exception {
		doMonoOptimisation();

		// Make sure timeframes, dark current collection time are set on ionchambers before each rep. of main scan
		setUpIonChambers();
	}

	@Override
	public Detector[] getExtraDetectors() {
		return null;
	}

	@Override
	public void completeCollection() {
		topupChecker.setCollectionTime(0.0);
		setI1TimeFormatRequired(true);

		// Set the hdf directory back to the 'before scan' value
		if (selectedXspressDetector != null) {
			setDetectorHdfPath(selectedXspressDetector, hdfFilePathBeforeScan);
		}

		// Return NXPlugin list back to original state (i.e. the one using plotserver ROI plugin)
		if ( originalMedipixPlugins != null ) {
			medipix.setAdditionalPluginList(originalMedipixPlugins);
			originalMedipixPlugins = null;
		}

		// Set the file path template back to its original state.
		if (!medipixHdfPathTemplate.isEmpty()) {
			setDetectorHdfPath(medipix, medipixHdfPathTemplate);
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

	private int getWholeNumSteps(double rangeFloat, double stepSize) {
		int wholeNumber = (int) Math.floor(rangeFloat / stepSize);
		double remainder = rangeFloat % stepSize;
		// Increment count if remainder is very similar in size to to stepsize
		if (Math.abs(remainder - stepSize) < 1e-6) {
			wholeNumber += 1;
		}
		return wholeNumber;
	}

	private double getXesIntegrationTime() {
		if (scanBean instanceof XesScanParameters) {
			XesScanParameters xesParams = (XesScanParameters) scanBean;
			return xesParams.getXesIntegrationTime();
		} else {
			return 0;
		}
	}

	private int getNumStepsXes(XesScanParameters xesParams) {
		double xesEnergyRange = xesParams.getXesFinalEnergy() - xesParams.getXesInitialEnergy();
		return 1 + getWholeNumSteps(xesEnergyRange, xesParams.getXesStepSize());
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
			Object monoScanBean = getXesMonoScanBean(xesParams);
			if (monoScanBean instanceof XasScanParameters && scanType==XesScanParameters.FIXED_XES_SCAN_XAS) {
				timeValues = ExafsScanPointCreator.getScanTimeArray((XasScanParameters)monoScanBean);
			} else if (monoScanBean instanceof XasScanParameters && scanType==XesScanParameters.FIXED_XES_SCAN_XANES) {
				timeValues = XanesScanPointCreator.getScanTimeArray((XanesScanParameters)monoScanBean);
			}
		} else {
			// 2d scans, same integration time for all points
			double collectionTime = xesParams.getXesIntegrationTime();

			int numStepsXes = getNumStepsXes(xesParams);
			int numStepsMono = getNumStepsMono(xesParams);

			timeValues = new Double[numStepsMono * numStepsXes];
			Arrays.fill(timeValues, collectionTime);
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

		if (scanBean instanceof XanesScanParameters) {
			XanesScanParameters xanesParams = (XanesScanParameters) scanBean;
			tfgFrameTimes = XanesScanPointCreator.getScanTimeArray(xanesParams);
		}
		else if (scanBean instanceof XasScanParameters) {
			XasScanParameters xasParams = (XasScanParameters) scanBean;
			tfgFrameTimes = ExafsScanPointCreator.getScanTimeArray(xasParams);
		}
		else if ( scanBean instanceof XesScanParameters ) {
			XesScanParameters xesParams = (XesScanParameters) scanBean;
			tfgFrameTimes = getScanTimeArray(xesParams);
		}

		// Determine max collection time
		double maxTime = 0;
		for(int i=0; i<tfgFrameTimes.length; i++) {
			if (tfgFrameTimes[i]>maxTime) {
				maxTime = tfgFrameTimes[i];
			}
		}

		ionchambers.setDarkCurrentRequired(true);
		i1.setDarkCurrentRequired(true);

		// set dark current time and handle any errors here
		if (maxTime > 0) {
			ionchambers.setDarkCurrentCollectionTime(maxTime);
			i1.setDarkCurrentCollectionTime(maxTime);
			topupChecker.setCollectionTime(maxTime);
		}

		if (tfgFrameTimes != null) {
			if (xesMode) {
				i1.clearFrameSets();
				i1.setTimes(tfgFrameTimes);
				if (scanBean instanceof XasScanParameters || scanBean instanceof XanesScanParameters) {
					setI1TimeFormatRequired(false);
				} else {
					setI1TimeFormatRequired(true);
				}
			} else {
				ionchambers.clearFrameSets();
				ionchambers.setTimes(tfgFrameTimes);
			}
		}
	}

	public boolean getConfigureMedipixRois() {
		return configureMedipixRois;
	}

	public void setConfigureMedipixRois(boolean configureMedipixRois) {
		this.configureMedipixRois = configureMedipixRois;
	}

	public String getRoiPvName() {
		return roiPvName;
	}

	public void setRoiPvName(String roiPvName) {
		this.roiPvName = roiPvName;
	}

	public String getMedipixDefaultBasePvName() {
		return medipixDefaultBasePvName;
	}

	public void setMedipixDefaultBasePvName(String medipixDefaultBasePvName) {
		this.medipixDefaultBasePvName = medipixDefaultBasePvName;
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
			logger.error("Problem loading XML file {} for XesScan : {}", bean.getScanFileName(),e.getMessage(), e);
			throw e;
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
			Object monoScanBean = getXesMonoScanBean(bean);;
			if (monoScanBean instanceof XasScanParameters) {
				return getMonoRange((XasScanParameters)monoScanBean);
			}else if (monoScanBean instanceof XanesScanParameters) {
				return getMonoRange((XanesScanParameters)monoScanBean);
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
		if (monoOptimiser.getBraggScannable() instanceof MonoMoveWithOffsetScannable) {
			MonoMoveWithOffsetScannable monoWithOffset = (MonoMoveWithOffsetScannable)monoOptimiser.getBraggScannable();
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
		switch (scanType) {
		case XesScanParameters.SCAN_XES_SCAN_MONO:
		case XesScanParameters.FIXED_XES_SCAN_XANES:
		case XesScanParameters.FIXED_XES_SCAN_XAS:
			return true;
		default:
			return false;
		}
	}

	private boolean xesMoves(int scanType) {
		switch (scanType) {
		case XesScanParameters.SCAN_XES_SCAN_MONO:
		case XesScanParameters.SCAN_XES_FIXED_MONO:
			return true;
		default:
			return false;
		}
	}

	/**
	 * Set 2D XES num steps per inner loop on MonoMoveWithOffset scannable
	 * @param xesParams
	 */
	private void setLoopSizes(XesScanParameters xesParams) {
		if (monoOptimiser.getBraggScannable() instanceof MonoMoveWithOffsetScannable) {
			MonoMoveWithOffsetScannable monoWithOffset = (MonoMoveWithOffsetScannable)monoOptimiser.getBraggScannable();

			int numStepsXes = getNumStepsXes(xesParams);
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
			monoWithOffset.setTimePerStepInnerLoop(xesParams.getXesIntegrationTime());
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
		if (monoOptimiser != null) {

			// Set the ionchamber to use to make measurement
			if (xesMode) {
				monoOptimiser.setScannableToMonitor(i1);
				setI1TimeFormatRequired(true); // always include time, even if not used for main XES scan
			} else {
				monoOptimiser.setScannableToMonitor(ionchambers);
			}

			MonoEnergyRange monoEnergyRange = null;
			boolean is2dScan = false;
			if (scanBean instanceof XanesScanParameters) {
				monoEnergyRange = getMonoRange((XanesScanParameters) scanBean);
			} else if (scanBean instanceof XasScanParameters) {
				monoEnergyRange = getMonoRange((XasScanParameters) scanBean);
			} else if (scanBean instanceof XesScanParameters) {
				monoEnergyRange = getMonoRange((XesScanParameters) scanBean);
				is2dScan = ((XesScanParameters) scanBean).getScanType() == XesScanParameters.SCAN_XES_SCAN_MONO;
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

			if (scanBean instanceof XesScanParameters) {
				setScanLoopType((XesScanParameters)scanBean);
				setLoopSizes((XesScanParameters)scanBean);
			}
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

	public boolean getXesMode() {
		return xesMode;
	}

	public void setXesMode(boolean xesMode) {
		this.xesMode = xesMode;
	}

	public void setPluginsForMutableRoi(List<NXPluginBase> pluginsForMutableRoi) {
		this.pluginsForMutableRoi = pluginsForMutableRoi;
	}

	public void setMutableRoi(MutableRectangularIntegerROI mutableRoi) {
		this.mutableRoi = mutableRoi;
	}
}
