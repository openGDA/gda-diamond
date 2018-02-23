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
import gda.device.detector.NXDetector;
import gda.device.detector.TfgFFoverI0;
import gda.device.detector.addetector.triggering.AbstractADTriggeringStrategy;
import gda.device.detector.areadetector.v17.NDPluginBase;
import gda.device.detector.areadetector.v17.impl.ADBaseImpl;
import gda.device.detector.areadetector.v18.NDStatsPVs.BasicStat;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.detector.nxdetector.NXCollectionStrategyPlugin;
import gda.device.detector.nxdetector.NXPluginBase;
import gda.device.detector.nxdetector.plugin.areadetector.ADRoiStatsPair;
import gda.device.detector.nxdetector.plugin.areadetector.ADRoiStatsPairFactory;
import gda.device.detector.nxdetector.roi.ImutableRectangularIntegerROI;
import gda.device.detector.nxdetector.roi.RectangularROI;
import gda.device.detector.nxdetector.roi.SimpleRectangularROIProvider;
import gda.device.detector.xmap.NexusXmapFluorescenceDetectorAdapter;
import gda.device.detector.xmap.Xmap;
import gda.device.detector.xspress.Xspress2Detector;
import gda.device.scannable.MonoMoveWithOffsetScannable;
import gda.device.scannable.MonoOptimisation;
import gda.device.scannable.TopupChecker;
import gda.epics.CAClient;
import gda.exafs.scan.ExafsScanPointCreator;
import gda.exafs.scan.XanesScanPointCreator;
import gda.factory.Finder;
import gda.util.Element;
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
import uk.ac.gda.beans.exafs.i20.MedipixParameters;
import uk.ac.gda.beans.exafs.i20.ROIRegion;
import uk.ac.gda.beans.xspress.XspressParameters;
import uk.ac.gda.devices.detector.FluorescenceDetector;
import uk.ac.gda.devices.detector.FluorescenceDetectorParameters;
import uk.ac.gda.devices.detector.xspress4.Xspress4Detector;
import uk.ac.gda.server.exafs.scan.BeamlinePreparer;
import uk.ac.gda.server.exafs.scan.DetectorPreparer;
import uk.ac.gda.util.beans.xml.XMLHelpers;

public class I20DetectorPreparer implements DetectorPreparer {
	private static final Logger logger = LoggerFactory.getLogger(I20DetectorPreparer.class);

//	private Xspress2Detector xspress2system;
	private Detector selectedXspressDetector;

	private Scannable[] sensitivities;
	private Scannable[] sensitivity_units;
	private Scannable[] offsets;
	private Scannable[] offset_units;
	private TfgScalerWithFrames ionchambers;
	private TfgScalerWithFrames i1;
	private TfgFFoverI0 ffI0;

	private Xmap vortex;
	private NXDetector medipix;
	private TopupChecker topupChecker;
	private IScanParameters scanBean;
	private Double[] tfgFrameTimes;
	private List<NXPluginBase> originalMedipixPlugins;

	private String medipixDefaultBasePvName="BL20I-EA-DET-05";
	private String roiPvName = "ROI1:";
	private String statPvName = "STAT1:";
	private boolean configureMedipixRois = true;

	private boolean xesMode = false;

	private MonoOptimisation monoOptimiser;

	public I20DetectorPreparer(Scannable[] sensitivities, Scannable[] sensitivity_units,
			Scannable[] offsets, Scannable[] offset_units, TfgScalerWithFrames ionchambers, TfgScalerWithFrames I1,
			Xmap vortex, NXDetector medipix, TopupChecker topupChecker) {
		selectedXspressDetector = null;
		this.sensitivities = sensitivities;
		this.sensitivity_units = sensitivity_units;
		this.offsets = offsets;
		this.offset_units = offset_units;
		this.ionchambers = ionchambers;
		this.i1 = I1;
		this.vortex = vortex;
		this.medipix = medipix;
		this.topupChecker = topupChecker;
		sensitivities = sensitivity_units;
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
			i1.setOutputFormat(new String[]{"%.4f", "%.4f", "%.2f"});
			i1.setExtraNames(new String[]{"Time", "I1"});
			i1.setTimeChannelRequired(true);
		} else {
			i1.setOutputFormat(new String[]{"%.4f", "%.4f"});
			i1.setExtraNames(new String[]{"I1"});
			i1.setTimeChannelRequired(false);
		}
	}

	public FluorescenceDetectorParameters getDetectorParametersBean(String xmlFileName) throws Exception {
		return (FluorescenceDetectorParameters) XMLHelpers.getBean(new File(xmlFileName));
	}

	/**
	 * Configure a Fluorescence detector on server by getting the name from the xml file and using the Finder.
	 * @param xmlFileName
	 * @return Xspress2Detector object on server
	 * @throws Exception if detector could not be found or there was a problem creating bean from XML.
	 */
	public Detector configureFluorescenceDetector(FluorescenceDetectorParameters params) throws Exception {

		String detName = params.getDetectorName();

		// Use fluorescence detector interface so can configure it with param bean from xml bean
		// Expected detector types for i20 are currently Xspress2Detector, Xspress4Detector, NexusXmapFluorescenceDetectorAdapter
		FluorescenceDetector det = Finder.getInstance().find(detName);
		if (det==null) {
			throw new Exception("Unable to find detector called "+detName+" on server\n");
		}
		det.applyConfigurationParameters(params);

		// For Xmap, return NexusXmap object since is what is used as detector during scans.
		if (det instanceof NexusXmapFluorescenceDetectorAdapter) {
			return ((NexusXmapFluorescenceDetectorAdapter)det).getXmap();
		}
		return (Detector) det;
	}

	private void setConfigFilename(Detector det, String xmlFilename) {
		if (det instanceof Xspress2Detector) {
			((Xspress2Detector) det).setConfigFileName(xmlFilename);
		} else if (det instanceof Xspress4Detector) {
			((Xspress4Detector) det).setConfigFileName(xmlFilename);
		} else if (det instanceof Xmap) {
			((Xmap)det).setConfigFileName(xmlFilename);
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

	// Full path to xml folder containing experiment xml files
	private String experimentXmlFullPath;
	private String hdfFilePathBeforeScan;

	private String getNexusDataFullPath() {
		String folder = experimentXmlFullPath.replace("/xml/", "/");
		return FilenameUtils.getFullPathNoEndSeparator(folder)+"/nexus/";
	}

	private void setHdfPathBeforeScan(Detector detector) throws DeviceException {
		if (detector != null && detector instanceof Xspress4Detector) {
			Xspress4Detector det = (Xspress4Detector) detector;
			hdfFilePathBeforeScan = det.getDetector().getController().getFilePath();
			det.getDetector().setFilePath(getNexusDataFullPath());
		}
	}

	private void setHdfPathAfterScan(Detector detector) {
		if (detector != null && detector instanceof Xspress4Detector) {
			try {
				Xspress4Detector det = (Xspress4Detector) detector;
				det.getDetector().getController().setFilePath(hdfFilePathBeforeScan);
				det.getDetector().setFilePath(hdfFilePathBeforeScan);
			} catch (DeviceException e) {
				logger.error("Problem setting hdf directory to {} for {} at end of scan",  hdfFilePathBeforeScan, detector.getName(), e);
			}
		}
	}

	@Override
	public void configure(IScanParameters scanBean, IDetectorParameters detectorBean, IOutputParameters outputBean,
			String experimentFullPath) throws Exception {

		this.scanBean = scanBean;
		this.experimentXmlFullPath = experimentFullPath;

		String experimentType = detectorBean.getExperimentType();
		xesMode = experimentType.equals(DetectorParameters.XES_TYPE);

		_setUpIonChambers();

		if (experimentType.equals(DetectorParameters.FLUORESCENCE_TYPE)) {
			FluorescenceParameters fluoresenceParameters = detectorBean.getFluorescenceParameters();
			String xmlFileName = experimentFullPath + fluoresenceParameters.getConfigFileName();
			String detType = fluoresenceParameters.getDetectorType();
			FluorescenceDetectorParameters params = getDetectorParametersBean(xmlFileName);
			setXspressOutputOptions(params, outputBean);
			Detector configuredDetector = configureFluorescenceDetector(params);
			setConfigFilename(configuredDetector, xmlFileName);
			if (configuredDetector instanceof Xmap) {
				vortex = (Xmap) configuredDetector;
			} else {
				setXspressCorrectionParameters();
				selectedXspressDetector = configuredDetector;
				setHdfPathBeforeScan(selectedXspressDetector);
			}

		} else if (experimentType.equals(DetectorParameters.XES_TYPE)) {
			FluorescenceParameters fluoresenceParameters = detectorBean.getXesParameters();
			String detType = fluoresenceParameters.getDetectorType();
			String xmlFileName = experimentFullPath + fluoresenceParameters.getConfigFileName();
			if (detType.equals(FluorescenceParameters.SILICON_DET_TYPE)) {
				vortex.setConfigFileName(xmlFileName);
				vortex.configure();
			}
			else if ( detType.toLowerCase().contains(FluorescenceParameters.MEDIPIX_DET_TYPE.toLowerCase())) {
				if	(configureMedipixRois) {
					configureMedipix( xmlFileName);
				}
			}
		}

		List<IonChamberParameters> ionChamberParamsArray = null;
		if (experimentType.equals(DetectorParameters.FLUORESCENCE_TYPE)) {
			ionChamberParamsArray = detectorBean.getFluorescenceParameters().getIonChamberParameters();
		} else if (experimentType.equals(DetectorParameters.TRANSMISSION_TYPE)) {
			ionChamberParamsArray = detectorBean.getTransmissionParameters().getIonChamberParameters();
		} else if (experimentType.equals(DetectorParameters.XES_TYPE)) {
			ionChamberParamsArray = detectorBean.getXesParameters().getIonChamberParameters();
		}
		if (ionChamberParamsArray != null) {
			for (IonChamberParameters ionChamberParams : ionChamberParamsArray) {
				_setup_amp_sensitivity(ionChamberParams);
			}
		}
	}

	/**
	 * Create ROI using parameters from XML file, setup Medipix NXPlugin list to use new ROI rather than the one from plotserver.
	 *
	 * @param xmlFileName
	 * @throws Exception
	 * @since 24/8/2016
	 */
	private void configureMedipix( String xmlFileName ) throws Exception {
		// --- Create ROI using parameters from XML file :

		// Create bean from XML
		MedipixParameters param = (MedipixParameters) XMLHelpers.createFromXML(MedipixParameters.mappingURL, MedipixParameters.class, MedipixParameters.schemaURL, new File(xmlFileName));

		// Create region using first ROI only - currently camera uses only one ROI
		ROIRegion region1 = param.getRegionList().get(0);
		int xstart = region1.getXRoi().getRoiStart(),
			xsize = region1.getXRoi().getRoiEnd() - xstart;

		int ystart = region1.getYRoi().getRoiStart(),
			ysize = region1.getYRoi().getRoiEnd() - ystart;

		RectangularROI<Integer> roi = new ImutableRectangularIntegerROI(xstart, ystart, xsize, ysize, region1.getRoiName() ) ;

		// --- Create new NXPlugin for ROI :

		// First try to get plotserver ROI NXPlugin from detector - so we can extract PV names necessary to create the new plugin
		ADRoiStatsPair plotserverRoiPlugin = getRoiPlugin("roistats1");

		if ( plotserverRoiPlugin == null ) {
			logger.warn("Not able to set up ROI for scan - could not find ADRoiStatsPair NXPlugin for detector ",medipix.getName() );
			return;
		}

		String arrayPortName = plotserverRoiPlugin.getRoiInputPort();

		// Try to get camera base PV name from collection strategy

		String basePvName = medipixDefaultBasePvName;
		NXCollectionStrategyPlugin collectionStrategy = medipix.getCollectionStrategy();
		if ( collectionStrategy!=null && collectionStrategy instanceof AbstractADTriggeringStrategy ) {
			ADBaseImpl baseImpl = (ADBaseImpl) ( (AbstractADTriggeringStrategy) collectionStrategy ).getAdBase();
			basePvName = baseImpl.getBasePVName();
		}
		basePvName = basePvName.replace(":CAM:", ":");


		// Create new NXPlugin with ROI from XML settings (same PV names as plotserver ROI).
		// use same enabled stats as original plugin
		List<BasicStat> enabledStats = plotserverRoiPlugin.getEnabledBasicStats();
		ADRoiStatsPair roistatPair = getNXRoiStatPair( basePvName, arrayPortName, roi, enabledStats );

		// --- Setup additionalPluginList : copy old list but replace plotserver ROI plugin with new one with ROI from XML settings :

		// Store current NXPlugin list so we can return it to the original state at the end of the scan
		originalMedipixPlugins = medipix.getAdditionalPluginList();

		// Make new plugin list
		List<NXPluginBase> newPluginList = new ArrayList<NXPluginBase>();
		for(NXPluginBase plugin : originalMedipixPlugins ) {
			if( plugin == plotserverRoiPlugin ) {
				newPluginList.add( roistatPair );
			} else
				newPluginList.add( plugin );
		}
		medipix.setAdditionalPluginList(newPluginList);

		// Set medipix acquisition time for XES scan in dummy mode - so scans work properly and frames stay in sync with scan.
		// Readout time should also be set to zero, so that exposure time = acquisition time. 12/7/2017
		if (LocalProperties.isDummyModeEnabled()){
			double xesIntegrationTime = getXesIntegrationTime();
			if (xesIntegrationTime>0) {
				medipix.setCollectionTime(xesIntegrationTime);
			}
		}
		// Set ROI min callback time to zero (otherwise might start to miss frames if acquisition time is < callback time)
		CAClient.put(basePvName+roiPvName+NDPluginBase.MinCallbackTime, 0);
	}

	/**
	 * Get ADRoiStatPair plugin with given name from detector.
	 * @param searchName
	 * @return
	 */
	private ADRoiStatsPair getRoiPlugin( String searchName ) {
		for( NXPluginBase plugin : medipix.getAdditionalPluginList() ) {
			if ( plugin instanceof ADRoiStatsPair && plugin.getName().equals( searchName ))
				return (ADRoiStatsPair) plugin;
		}
		return null;
	}

	/**
	 * Make a new ADRoiStatsPair NXPlugin using provided ROI and PV names; 'MaxValue' and 'Total' basic stats enabled.
	 *
	 * @param basePvName
	 * @param arrayPortName
	 * @param roi
	 * @return
	 * @throws Exception
	 */
	private ADRoiStatsPair getNXRoiStatPair( String basePvName, String arrayPortName, RectangularROI<Integer> roi, List<BasicStat> stats ) throws Exception {

		ADRoiStatsPairFactory fac = new ADRoiStatsPairFactory();
		fac.setPluginName("roistats");
		fac.setBaseRoiPVName(basePvName+roiPvName);
		fac.setBaseStatsPVName(basePvName+statPvName);
		fac.setRoiInputNdArrayPort(arrayPortName);

		fac.setEnabledBasicStats(stats);
		fac.setOneTimeSeriesCollectionPerLine(false);

		SimpleRectangularROIProvider roiProvider = new SimpleRectangularROIProvider();
		roiProvider.setRoi(roi);

		fac.setRoiProvider(roiProvider);

		return fac.getObject();

	}
	@Override
	public void beforeEachRepetition() throws Exception {
		doMonoOptimisation();

		// Make sure timeframes, dark current collection time are set on ionchambers before each rep. of main scan
		_setUpIonChambers();
	}

	@Override
	public Detector[] getExtraDetectors() {
		return null;
	}

	@Override
	public void completeCollection() {
		topupChecker.setCollectionTime(0.0);
		ionchambers.setOutputLogValues(false);
		setI1TimeFormatRequired(true);

		// Set the hdf directory back to the 'before scan' value
		setHdfPathAfterScan(selectedXspressDetector);

		// Return NXPlugin list back to original state (i.e. the one using plotserver ROI plugin)
		if ( originalMedipixPlugins != null )
			medipix.setAdditionalPluginList(originalMedipixPlugins);
	}

	private void _setup_amp_sensitivity(IonChamberParameters ionChamberParams) throws Exception {
		if (ionChamberParams.getChangeSensitivity()) {
			String ionChamberName = ionChamberParams.getName();
			if (ionChamberParams.getGain() == null || ionChamberParams.getGain().isEmpty()) {
				return;
			}
			String[] gainStringParts = ionChamberParams.getGain().split(" ");
			String[] ampStringParts = ionChamberParams.getOffset().split(" ");
			int index = 0;
			if (ionChamberName.equalsIgnoreCase("It")) {
				index = 1;
			} else if (ionChamberName.equalsIgnoreCase("Iref")) {
				index = 2;
			} else if (ionChamberName.equalsIgnoreCase("I1")) {
				index = 3;
			}
			try {
				// print "Changing sensitivity of",ionChamberName,"to",ionChamberParams.getGain()
				sensitivities[index].moveTo(gainStringParts[0]);
				sensitivity_units[index].moveTo(gainStringParts[1]);
				offsets[index].moveTo(ampStringParts[0]);
				offset_units[index].moveTo(ampStringParts[1]);
			} catch (Exception e) {
				// InterfaceProvider.getTerminalPrinter().print(
				// "Exception while trying to change the sensitivity of ion chamber" + ionChamberParams.getName());
				// InterfaceProvider
				// .getTerminalPrinter()
				// .print("Set the ion chamber sensitivity manually, uncheck the box in the Detector Parameters editor and restart the scan");
				// InterfaceProvider.getTerminalPrinter().print("Please report this problem to Data Acquisition");
				throw e;
			}
		}
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

	/**
	 * Set output format to remove time column for Xas, Xanes scans.
	 */
	private void setupI1ForXes() {
		if (scanBean instanceof XesScanParameters) {
			setI1TimeFormatRequired(true);
		} else {
			// XAS, XANES - no time channel required for I1
			setI1TimeFormatRequired(false);
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
	private void _setUpIonChambers() throws Exception {
		tfgFrameTimes = null;

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

		// # set dark current time and handle any errors here
		if (maxTime > 0) {
			// InterfaceProvider.getTerminalPrinter().print(
			// "Setting ionchambers dark current collectiom time to" + maxTime + "s.");
			ionchambers.setDarkCurrentCollectionTime(maxTime);
			i1.setDarkCurrentCollectionTime(maxTime);

			// double topupPauseTime = maxTime + topupChecker.getTolerance();
			// InterfaceProvider.getTerminalPrinter().print(
			// "Setting the topup checker to pause scans for" + topupPauseTime + "s before topup");
			topupChecker.setCollectionTime(maxTime);
		}

		if (tfgFrameTimes != null) {
			if (xesMode) {
				i1.clearFrameSets();
				i1.setTimes(tfgFrameTimes);
				monoOptimiser.setScannableToMonitor(i1);
			} else {
				ionchambers.clearFrameSets();
				ionchambers.setTimes(tfgFrameTimes);
				monoOptimiser.setScannableToMonitor(ionchambers);
			}
		}

	}

	private void setXspressCorrectionParameters() throws DeviceException {
		double dtEnergy = 0.0;
		// # Use the fluo (emission) energy of the nearest transition based on the element and excitation edge
		// # to calculate the energy dependent deadtime parameters.
		if ((scanBean instanceof XasScanParameters) || (scanBean instanceof XanesScanParameters)) {
			String element;
			String edge;
			if (scanBean instanceof XasScanParameters) {
				element = ((XasScanParameters) scanBean).getElement();
				edge = ((XasScanParameters) scanBean).getEdge();
			} else {
				element = ((XanesScanParameters) scanBean).getElement();
				edge = ((XanesScanParameters) scanBean).getEdge();
			}
			Element elementObj = Element.getElement(element);
			dtEnergy = _getEmissionEnergy(elementObj, edge);
			dtEnergy /= 1000; // # convert from eV to keV;

			// this apparently does nothing for xspress2 (never implemented?)
//			xspress2system.setDeadtimeCalculationEnergy(dtEnergy);
		}

	}

	private double _getEmissionEnergy(Element elementObj, String edge) {
		if (edge.equals("K")) {
			return elementObj.getEmissionEnergy("Ka1");
		} else if (edge.equals("L1")) {
			return elementObj.getEmissionEnergy("La1");
		} else if (edge.equals("L2")) {
			return elementObj.getEmissionEnergy("La1");
		} else if (edge.equals("L3")) {
			return elementObj.getEmissionEnergy("La1");
		} else if (edge.equals("M1")) {
			return elementObj.getEmissionEnergy("Ma1");
		} else if (edge.equals("M2")) {
			return elementObj.getEmissionEnergy("Ma1");
		} else if (edge.equals("M3")) {
			return elementObj.getEmissionEnergy("Ma1");
		} else if (edge.equals("M4")) {
			return elementObj.getEmissionEnergy("Ma1");
		} else if (edge.equals("M5")) {
			return elementObj.getEmissionEnergy("Ma1");
		} else {
			return elementObj.getEmissionEnergy("Ka1");
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

	public String getStatPvName() {
		return statPvName;
	}

	public void setStatPvName(String statPvName) {
		this.statPvName = statPvName;
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

	private MonoEnergyRange getMonoRange(XanesScanParameters bean) {
		return new MonoEnergyRange(bean.getInitialEnergy(), bean.getFinalEnergy());
	}

	private Object getXesMonoScanBean(XesScanParameters bean) throws Exception {
		Object monoScanBean = null;
		try {
			monoScanBean = XMLHelpers.getBean(new File(bean.getScanFileName()));
		} catch (Exception e) {
			logger.error("Problem loading XML file {} for XesScan : {}", bean.getScanFileName(),e.getMessage(), e);
			throw new Exception(e);
		}
		return monoScanBean;
	}

	private MonoEnergyRange getMonoRange(XesScanParameters bean) throws Exception {
		int scanType = bean.getScanType();
		if (scanType == XesScanParameters.SCAN_XES_FIXED_MONO) {
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
		private double lowEnergy;
		private double highEnergy;

		public MonoEnergyRange(double lowEnergy, double highEnergy) {
			this.lowEnergy = lowEnergy;
			this.highEnergy = highEnergy;
		}

		public double getLowEnergy() {
			return lowEnergy;
		}
		public void setLowEnergy(double lowEnergy) {
			this.lowEnergy = lowEnergy;
		}
		public double getHighEnergy() {
			return highEnergy;
		}
		public void setHighEnergy(double highEnergy) {
			this.highEnergy = highEnergy;
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

//			((MultipleExposureHardwareTriggeredStrategy)medipix.getCollectionStrategy()).setNumExtraPointsPerInnerLoop(monoOptimiser.getOffsetNumPoints());
			monoOptimiser.getOffsetNumPoints();

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

			MonoEnergyRange monoEnergyRange = null;
			boolean is2dScan = false;
			if (scanBean instanceof XanesScanParameters) {
				monoEnergyRange=getMonoRange((XanesScanParameters)scanBean);
			} else if (scanBean instanceof XasScanParameters) {
				monoEnergyRange=getMonoRange((XasScanParameters)scanBean);
			} else if (scanBean instanceof XesScanParameters) {
				monoEnergyRange = getMonoRange((XesScanParameters)scanBean);
				is2dScan = ((XesScanParameters)scanBean).getScanType() == XesScanParameters.SCAN_XES_SCAN_MONO;
			}

			setScanLoopType(null); // reset scan and loop type on the bragg1WIthOffset before doing optimisation scan

			if (monoEnergyRange!=null && monoOptimiser.getAllowOptimisation()) {
				if (!is2dScan) {

					monoOptimiser.getBraggScannable().moveTo(monoEnergyRange.getLowEnergy());

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

	public void setFFI0(TfgFFoverI0 ffI0) {
		this.ffI0 = ffI0;
	}

	public TfgFFoverI0 getFfI0() {
		return ffI0;
	}

	public Detector getSelectedXspressDetector() {
		return selectedXspressDetector;
	}

	public void setSelectedXspressDetector(Detector selectedXspressDetector) {
		this.selectedXspressDetector = selectedXspressDetector;
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

}
