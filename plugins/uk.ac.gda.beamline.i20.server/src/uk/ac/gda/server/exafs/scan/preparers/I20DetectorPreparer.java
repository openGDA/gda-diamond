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

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.NXDetector;
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
import gda.device.detector.xmap.Xmap;
import gda.device.detector.xspress.Xspress2Detector;
import gda.device.scannable.MonoOptimisation;
import gda.device.scannable.TopupChecker;
import gda.epics.CAClient;
import gda.exafs.scan.ExafsScanPointCreator;
import gda.exafs.scan.XanesScanPointCreator;
import gda.util.Element;
import uk.ac.gda.beans.exafs.DetectorParameters;
import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.IonChamberParameters;
import uk.ac.gda.beans.exafs.Region;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
import uk.ac.gda.beans.exafs.i20.MedipixParameters;
import uk.ac.gda.beans.exafs.i20.ROIRegion;
import uk.ac.gda.server.exafs.scan.BeamlinePreparer;
import uk.ac.gda.server.exafs.scan.DetectorPreparer;
import uk.ac.gda.util.beans.xml.XMLHelpers;

public class I20DetectorPreparer implements DetectorPreparer {
	private static final Logger logger = LoggerFactory.getLogger(I20DetectorPreparer.class);

	private Xspress2Detector xspress2system;
	private Scannable[] sensitivities;
	private Scannable[] sensitivity_units;
	private Scannable[] offsets;
	private Scannable[] offset_units;
	private TfgScalerWithFrames ionchambers;
	private TfgScalerWithFrames i1;
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

	private MonoOptimisation monoOptimiser;

	public I20DetectorPreparer(Xspress2Detector xspress2system, Scannable[] sensitivities, Scannable[] sensitivity_units,
			Scannable[] offsets, Scannable[] offset_units, TfgScalerWithFrames ionchambers, TfgScalerWithFrames I1,
			Xmap vortex, NXDetector medipix, TopupChecker topupChecker) {
		this.xspress2system = xspress2system;
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
		detectors.add(xspress2system);
		detectors.add(ionchambers);
		detectors.add(i1);
		detectors.add(vortex);
		detectors.add(medipix);
		return detectors;
	}

	@Override
	public void configure(IScanParameters scanBean, IDetectorParameters detectorBean, IOutputParameters outputBean,
			String experimentFullPath) throws Exception {

		this.scanBean = scanBean;

		_setUpIonChambers();

		String experimentType = detectorBean.getExperimentType();

		// Set frame times for ionchambers
		if (tfgFrameTimes != null) {
			if (experimentType.equals(DetectorParameters.XES_TYPE)) {
				i1.clearFrameSets();
				i1.setTimes(tfgFrameTimes);
			} else {
				ionchambers.clearFrameSets();
				ionchambers.setTimes(tfgFrameTimes);
			}
		}

		if (experimentType.equals(DetectorParameters.FLUORESCENCE_TYPE)) {
			FluorescenceParameters fluoresenceParameters = detectorBean.getFluorescenceParameters();
			String xmlFileName = experimentFullPath + fluoresenceParameters.getConfigFileName();
			String detType = fluoresenceParameters.getDetectorType();
			if (detType.equals(FluorescenceParameters.GERMANIUM_DET_TYPE)) {
				xspress2system.setConfigFileName(xmlFileName);
				xspress2system.configure();
				setXspressCorrectionParameters();
			} else if (detType.equals(FluorescenceParameters.SILICON_DET_TYPE)) {
				vortex.setConfigFileName(xmlFileName);
				vortex.configure();
			}
		} else if (experimentType.equals(DetectorParameters.XES_TYPE)) {
			FluorescenceParameters fluoresenceParameters = detectorBean.getXesParameters();
			String detType = fluoresenceParameters.getDetectorType();
			String xmlFileName = experimentFullPath + fluoresenceParameters.getConfigFileName();
			if (detType.equals(FluorescenceParameters.SILICON_DET_TYPE)) {
				vortex.setConfigFileName(xmlFileName);
				vortex.configure();
			}
			else if ( detType.equals(FluorescenceParameters.MEDIPIX_DET_TYPE)) {
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
		ADRoiStatsPair roistatPair = getNXRoiStatPair( basePvName, arrayPortName, roi );

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
	private ADRoiStatsPair getNXRoiStatPair( String basePvName, String arrayPortName, RectangularROI<Integer> roi ) throws Exception {

		ADRoiStatsPairFactory fac = new ADRoiStatsPairFactory();
		fac.setPluginName("roistats");
		fac.setBaseRoiPVName(basePvName+roiPvName);
		fac.setBaseStatsPVName(basePvName+statPvName);
		fac.setRoiInputNdArrayPort(arrayPortName);
		List<BasicStat> stats = Arrays.asList( new BasicStat[]{ BasicStat.MaxValue, BasicStat.Total } );
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
	}

	@Override
	public Detector[] getExtraDetectors() {
		return null;
	}

	@Override
	public void completeCollection() {
		topupChecker.setCollectionTime(0.0);
		ionchambers.setOutputLogValues(false);

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

	private void _setUpIonChambers() throws Exception {
		// # determine max collection time
		double maxTime = 0;
		tfgFrameTimes = null;

		if (scanBean instanceof XanesScanParameters) {
			XanesScanParameters xanesParams = (XanesScanParameters) scanBean;
			for (Region region : xanesParams.getRegions()) {
				if (region.getTime() > maxTime) {
					maxTime = region.getTime();
				}
			}
			tfgFrameTimes = XanesScanPointCreator.getScanTimeArray(xanesParams);
		}
		else if (scanBean instanceof XasScanParameters) {
			XasScanParameters xasParams = (XasScanParameters) scanBean;
			if (xasParams.getPreEdgeTime() > maxTime) {
				maxTime = xasParams.getPreEdgeTime();
			}
			if (xasParams.getEdgeTime() > maxTime) {
				maxTime = xasParams.getEdgeTime();
			}
			if (xasParams.getExafsTimeType().equals("Constant Time")) {
				if (xasParams.getExafsTime() > maxTime) {
					maxTime = xasParams.getExafsTime();
				}
			} else {
				if (xasParams.getExafsToTime() > maxTime) {
					maxTime = xasParams.getExafsToTime();
				}
				if (xasParams.getExafsFromTime() > maxTime) {
					maxTime = xasParams.getExafsFromTime();
				}
			}
			tfgFrameTimes = ExafsScanPointCreator.getScanTimeArray(xasParams);
		}
		else if ( scanBean instanceof XesScanParameters ) {
			XesScanParameters xesParams = (XesScanParameters) scanBean;

			double collectionTime = xesParams.getXesIntegrationTime();
			double energyRange = xesParams.getXesFinalEnergy() - xesParams.getXesInitialEnergy();
			int numStepsXes = 1 + getWholeNumSteps(energyRange, xesParams.getXesStepSize());

			int numStepsMono = 1;
			int scanType = xesParams.getScanType();

			// 2d scan, mono is also moved.
			if (scanType == XesScanParameters.SCAN_XES_SCAN_MONO) { // # XesScanParameters.SCAN_XES_SCAN_MONO:
				energyRange = xesParams.getMonoFinalEnergy() - xesParams.getMonoInitialEnergy();
				numStepsMono = 1 + getWholeNumSteps(energyRange, xesParams.getMonoStepSize());
			}

			// Determine number of steps in inner and outer loops
			// (These will be probably be needed when implementing bragg offset optimization during 2d scan)

//			int numStepsPerInnerLoop = 0, numStepsPerOuterLoop = 0;
//			String loopType = xesParams.getLoopChoice();
//			if (loopType.equals(XesScanParameters.EF_OUTER_MONO_INNER)) {
//				numStepsPerOuterLoop = numStepsXes;
//				numStepsPerInnerLoop = numStepsMono;
//			} else if (loopType.equals(XesScanParameters.MONO_OUTER_EF_INNER)) {
//				numStepsPerOuterLoop = numStepsMono;
//				numStepsPerInnerLoop = numStepsXes;
//			}

			tfgFrameTimes = new Double[numStepsMono * numStepsXes];
			Arrays.fill(tfgFrameTimes, collectionTime);

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
			xspress2system.setDeadtimeCalculationEnergy(dtEnergy);
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

	/**
	 * Run mono optimisation scan (i.e. adjust bragg offset for start and end scan energies to maximise signal
	 * on the detector and set appropriate fitting parameters to be used to adjust the offset during an energy scan).<p>
	 * This is not really a 'detector preparer' type of method, but need to do it here since it should (optionally) be run
	 * at the start of each scan/repetition and there are currently no beforeRepetition methods in the {@link BeamlinePreparer} interface.
	 * @throws Exception
	 */
	private void doMonoOptimisation() throws Exception {
		if (monoOptimiser != null) {
			double lowEnergy = 0;
			double highEnergy = 0;

			if (scanBean instanceof XanesScanParameters) {
				lowEnergy = ((XanesScanParameters) scanBean).getInitialEnergy();
				highEnergy = ((XanesScanParameters) scanBean).getFinalEnergy();
			} else if (scanBean instanceof XasScanParameters) {
				lowEnergy = ((XasScanParameters) scanBean).getInitialEnergy();
				highEnergy = ((XasScanParameters) scanBean).getFinalEnergy();
			}

			if (lowEnergy>0 && highEnergy>lowEnergy) {
				logger.info("Running monochromator optimisation for XAS/XANES scan : low energy = {}, high energy = {}", lowEnergy, highEnergy);
				monoOptimiser.optimise(lowEnergy, highEnergy);
			}
		}
	}
}
