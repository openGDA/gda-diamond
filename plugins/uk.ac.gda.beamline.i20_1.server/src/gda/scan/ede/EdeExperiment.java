/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package gda.scan.ede;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import org.apache.commons.lang.ArrayUtils;
import org.apache.commons.math3.util.Pair;
import org.eclipse.january.dataset.DoubleDataset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.gson.Gson;

import gda.data.scan.datawriter.NexusExtraMetadataDataWriter;
import gda.data.scan.datawriter.NexusFileMetadata;
import gda.data.scan.datawriter.NexusFileMetadata.EntryTypes;
import gda.data.scan.datawriter.NexusFileMetadata.NXinstrumentSubTypes;
import gda.data.scan.datawriter.XasAsciiNexusDataWriter;
import gda.device.DeviceException;
import gda.device.Monitor;
import gda.device.Scannable;
import gda.device.detector.EdeDetector;
import gda.device.detector.EdeDummyDetector;
import gda.device.scannable.TopupChecker;
import gda.factory.Findable;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.jython.scriptcontroller.ScriptControllerBase;
import gda.observable.IObserver;
import gda.scan.EdeScan;
import gda.scan.MultiScan;
import gda.scan.ScanBase;
import gda.scan.ScanPlotSettings;
import gda.scan.ede.EdeExperimentProgressBean.ExperimentCollectionType;
import gda.scan.ede.datawriters.EdeDataConstants;
import gda.scan.ede.datawriters.EdeExperimentDataWriter;
import gda.scan.ede.datawriters.ScanDataHelper;
import gda.scan.ede.position.EdePositionType;
import gda.scan.ede.position.EdeScanMotorPositions;
import gda.scan.ede.position.EdeScanPosition;
import uk.ac.gda.exafs.data.AlignmentParametersBean;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.experiment.trigger.TFGTrigger;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

/**
 * Base class for all EDE experiment classes.
 * <p>
 * These classes all work in a similar manner: they take experimental parameters in the form of a series of
 * EdeScanParameters, EdeScanPosition and StripDetector objects. Then in their runExperiment method they build and run
 * MultiScan which generates a single Nexus file. At they end they produce a single EDE format ASCII file whose filename
 * the runExperiment method returns.
 */
public abstract class EdeExperiment implements IObserver {

	protected static final Logger logger = LoggerFactory.getLogger(EdeExperiment.class);

	/**
	 * The name of the ScriptController object which is sent progress information and normalised spectra by experiments
	 */
	public static final String PROGRESS_UPDATER_NAME = "EDEProgressUpdater";

	public static final double TOP_UP_TIME = 10 * 60;

	protected final int firstRepetitionIndex = 0; // in case we switch to 1-based indexing

	protected EdeScanParameters iRefScanParameters;
	protected EdeScanPosition i0ForiRefPosition;
	protected EdeScanPosition iRefPosition;
	protected EdeScanParameters i0ForiRefScanParameters;

	protected EdeScan iRefFinalScan;
	protected EdeScan i0ForiRefScan;
	protected EdeScan iRefScan;
	protected EdeScan iRefDarkScan;
	protected boolean runIRef;
	protected boolean runItWithTriggerOptions = true; // default for linear/cyclic experiments

	protected Scannable beamLightShutter;
	protected EdeDetector theDetector;
	protected EdeScan i0DarkScan;
	protected EdeScan itDarkScan;
	protected EdeScan i0LightScan;
	protected EdeScan itLightScan;
	protected EdeScan i0FinalScan;
	protected EdeScan[] itScans;
	// protected final EdeScanParameters itScanParameters;
	protected EdeScanParameters itScanParameters; //This should not be 'final' otherwise params used in scan are 'one behind' what has been asked for... imh 16/10/2015
	protected final LinkedList<ScanBase> scansBeforeIt = new LinkedList<ScanBase>();
	protected final LinkedList<ScanBase> scansForIt = new LinkedList<ScanBase>();
	protected final LinkedList<ScanBase> scansAfterIt = new LinkedList<ScanBase>();
	protected ScanBase itScan;

	protected EdeScanParameters i0ScanParameters;
	protected EdeScanPosition i0Position;
	protected EdeScanPosition itPosition;
	protected EdeExperimentDataWriter writer;
	protected String nexusFilename;

	protected ScriptControllerBase controller;

	private String fileNamePrefix = "";

	private String sampleDetails = "";

	private Monitor topup;

	protected TFGTrigger itTriggerOptions;

	private static Gson gson = new Gson();

	protected boolean useFastShutter;
	protected String fastShutterName;
	protected Scannable fastShutter;

	protected double scanDeadTime = 2.0; // Approximate time overhead (secs) when running a scan.

	public EdeExperiment(List<TimingGroup> itTimingGroups,
			Map<String, Double> i0ScanableMotorPositions,
			Map<String, Double> iTScanableMotorPositions,
			String detectorName, String topupMonitorName, String beamShutterScannableName) throws DeviceException {
		itScanParameters = new EdeScanParameters();
		itScanParameters.setTimingGroups(itTimingGroups);
		this.itTriggerOptions = null;

		i0Position = this.setPosition(EdePositionType.OUTBEAM, i0ScanableMotorPositions);
		itPosition = this.setPosition(EdePositionType.INBEAM, iTScanableMotorPositions);

		setupExperiment(detectorName, topupMonitorName, beamShutterScannableName);

		useFastShutter = false;
		fastShutter = null;
	}

	public EdeExperiment(EdeScanParameters itScanParameters, TFGTrigger itTriggerOptions,
			EdeScanPosition i0ScanableMotorPositions,
			EdeScanPosition iTScanableMotorPositions,
			String detectorName, String topupMonitorName, String beamShutterScannableName) throws DeviceException {
		this.itTriggerOptions = itTriggerOptions;
		this.itScanParameters = itScanParameters;

		i0Position = i0ScanableMotorPositions;
		itPosition = iTScanableMotorPositions;

		setupExperiment(detectorName, topupMonitorName, beamShutterScannableName);

		useFastShutter = false;
		fastShutter = null;
	}

	public void setIRefParameters(Map<String, Double> i0ForIRefScanableMotorPositions, Map<String, Double> iRefScanableMotorPositions,
			double i0AccumulationTime, int i0NumberOfAccumulcations,
			double accumulationTime, int numberOfAccumulcations) throws DeviceException {
		iRefPosition = this.setPosition(EdePositionType.REFERENCE, iRefScanableMotorPositions);
		iRefScanParameters = new EdeScanParameters();

		TimingGroup newGroup = new TimingGroup();
		newGroup.setLabel(EdeDataConstants.IREF_DATA_NAME);
		newGroup.setNumberOfFrames(1);
		newGroup.setTimePerScan(accumulationTime);
		newGroup.setTimePerFrame(accumulationTime);
		newGroup.setNumberOfScansPerFrame(numberOfAccumulcations);
		iRefScanParameters.addGroup(newGroup);

		i0ForiRefPosition = this.setPosition(EdePositionType.OUTBEAM_REFERENCE, i0ForIRefScanableMotorPositions);
		i0ForiRefScanParameters = new EdeScanParameters();
		newGroup = new TimingGroup();
		newGroup.setLabel(EdeDataConstants.IREF_DATA_NAME);
		newGroup.setNumberOfFrames(1);
		newGroup.setTimePerScan(i0AccumulationTime);
		newGroup.setTimePerFrame(i0AccumulationTime);
		newGroup.setNumberOfScansPerFrame(i0NumberOfAccumulcations);
		i0ForiRefScanParameters.addGroup(newGroup);
		runIRef = true;
	}

	private void setupExperiment(String detectorName, String topupMonitorName, String beamShutterScannableName) throws DeviceException {
		theDetector  = Finder.getInstance().find(detectorName);
		topup = (Monitor) getFindable(topupMonitorName);
		beamLightShutter = (Scannable) getFindable(beamShutterScannableName);
		controller = (ScriptControllerBase) getFindable(PROGRESS_UPDATER_NAME);
	}

	protected void setCommonI0Parameters(double accumulationTime, int numberOfAccumulcations) throws DeviceException {
		i0ScanParameters = this.deriveScanParametersFromIt(accumulationTime, numberOfAccumulcations);
	}

	protected void setDefaultI0Parameters(double accumulationTime) throws DeviceException {
		i0ScanParameters = this.deriveScanParametersFromIt(accumulationTime, null);
	}

	protected EdeScanParameters deriveScanParametersFromIt(double accumulationTime, Integer commonNumberOfAccumulcations) throws DeviceException {
		// need an I0 spectrum for each timing group in itScanParameters
		List<TimingGroup> itgroups = itScanParameters.getGroups();

		EdeScanParameters parameters = new EdeScanParameters();
		for (TimingGroup itGroup : itgroups) {
			TimingGroup newGroup = new TimingGroup();
			newGroup.setLabel(itGroup.getLabel());
			newGroup.setNumberOfFrames(1);
			newGroup.setTimePerScan(accumulationTime);
			if(commonNumberOfAccumulcations == null) {
				// newGroup.setNumberOfScansPerFrame(theDetector.getNumberScansInFrame(itGroup.getTimePerFrame(), itGroup.getTimePerScan(), newGroup.getNumberOfFrames()));
				newGroup.setNumberOfScansPerFrame( itGroup.getNumberOfScansPerFrame() );
			} else {
				newGroup.setNumberOfScansPerFrame(commonNumberOfAccumulcations);
			}
			newGroup.setTimePerFrame(accumulationTime*newGroup.getNumberOfScansPerFrame());
			newGroup.setDelayBetweenFrames(0);
			parameters.addGroup(newGroup);
		}
		return parameters;
	}

	protected EdeScanParameters deriveItDarkParametersFromItParameters() {
		List<TimingGroup> itgroups = itScanParameters.getGroups();

		EdeScanParameters parameters = new EdeScanParameters();
		for (TimingGroup itGroup : itgroups) {
			TimingGroup newGroup = new TimingGroup();
			newGroup.setLabel(itGroup.getLabel());
			newGroup.setNumberOfFrames(1);
			newGroup.setTimePerScan(itGroup.getTimePerScan());
			newGroup.setNumberOfScansPerFrame(itGroup.getNumberOfScansPerFrame());
			newGroup.setTimePerFrame(itGroup.getTimePerFrame());
			newGroup.setDelayBetweenFrames(0);
			parameters.addGroup(newGroup);
		}
		return parameters;
	}

	private Findable getFindable(String name) {
		return Finder.getInstance().find(name);
	}

	protected abstract int getRepetitions();

	protected abstract boolean shouldRunItDark();

	/** Map to specify which detector to use for particular combination of position (Inbeam, outbeam..) and type (light, dark) */
	private Map< Pair<EdePositionType,EdeScanType>, EdeDetector> detectorsForScanParts = new HashMap< Pair<EdePositionType,EdeScanType>, EdeDetector>();

	/**
	 * Set a specific EdeDetector to be used for particular position (inbeam, outbeam..) and scantype (inbeam, outbeam) combination.
	 * This function allows dummy detector to be used to provide data for specific part of the scan.
	 * The default behaviour to use xh or frelon (as before).
	 * @param positionType {@link EdePositionType}
	 * @param scanType {@link EdeScanType}
	 * @param detector {@link EdeDetector} to use (probably an {@link EdeDummyDetector}).
	 */
	public void setDetectorForScanPart(EdePositionType positionType, EdeScanType scanType, EdeDetector detector) {
		detectorsForScanParts.put(Pair.create(positionType, scanType), detector);
	}

	public Map< Pair<EdePositionType,EdeScanType>, EdeDetector> getDetectorsForScanParts() {
		return detectorsForScanParts;
	}

	/**
	 * Method for creating EdeScan object; sets the detector to be used for the scan part by looking up from detectorsForScanParts map
	 * @param scanParams
	 * @param scanPosition
	 * @param scanType
	 * @param firstRepetitionIndex
	 * @param topupChecker
	 * @return
	 */
	public EdeScan makeEdeScan( EdeScanParameters scanParams, EdeScanPosition scanPosition, EdeScanType scanType, int firstRepetitionIndex, TopupChecker topupChecker ) {
		EdeDetector detectorForScan = theDetector;
		// Try to look up detector for this particular position and scan type :
		Pair<EdePositionType, EdeScanType> expPart = Pair.create(scanPosition.getType(), scanType);
		if (detectorsForScanParts.containsKey(expPart) ){
			detectorForScan = detectorsForScanParts.get(expPart);
		}
		return makeEdeScan(scanParams, scanPosition, scanType, detectorForScan, firstRepetitionIndex, topupChecker);
	}

	/**
	 * Method for creating EdeScan objects; includes setting of fastShutter
	 * @param scanParams
	 * @param scanPosition
	 * @param scanType
	 * @param detector
	 * @param firstRepetitionIndex
	 * @param topupChecker
	 * @return EdeScan object
	 * @since 23/2/2016
	 */
	public EdeScan makeEdeScan( EdeScanParameters scanParams, EdeScanPosition scanPosition, EdeScanType scanType, EdeDetector detector, int firstRepetitionIndex, TopupChecker topupChecker ) {

		if (detector instanceof EdeDummyDetector) {
			((EdeDummyDetector)detector).setMainDetectorName(theDetector.getName());
		}

		EdeScan edeScan = new EdeScan( scanParams, scanPosition, scanType, detector, firstRepetitionIndex, beamLightShutter, topupChecker );

		// Set option for using fast shutter during scan
		edeScan.setUseFastShutter(useFastShutter);
		if ( useFastShutter == true && fastShutterName != null ) {
			fastShutter = (Scannable) Finder.getInstance().find( fastShutterName );
			edeScan.setFastShutter( fastShutter );
		}

		return edeScan;
	}

	private void addScansForExperiment() throws Exception {
		Scannable motorToMoveDuringScan = getItScanPositions().getScannableToMoveDuringScan();
		if (motorToMoveDuringScan != null && i0Position instanceof EdeScanMotorPositions) {
			((EdeScanMotorPositions)i0Position).setScannableToMoveDuringScan(motorToMoveDuringScan);
		}

		double timeToTopup = getNextTopupTime();
		i0ScanParameters.setUseFrameTime(false);
		i0DarkScan = makeEdeScan(i0ScanParameters, i0Position, EdeScanType.DARK, firstRepetitionIndex, createTopupCheckerForStartOfExperiment(timeToTopup));
		i0DarkScan.setProgressUpdater(this);
		scansBeforeIt.add(i0DarkScan);

		if (runIRef) {
			iRefScanParameters.setUseFrameTime(false);
			iRefDarkScan = makeEdeScan(iRefScanParameters, iRefPosition, EdeScanType.DARK, firstRepetitionIndex, null);
			scansBeforeIt.add(iRefDarkScan);
			iRefDarkScan.setProgressUpdater(this);
		}

		addFinalScans();
	}

	protected abstract boolean shouldWaitForTopup(int repIndex, double timeToTopupInSec);

	protected abstract void addFinalScans() throws Exception;

	public String runExperiment() throws Exception {
		try {
			clearScans();
			addScansForExperiment();
			nexusFilename = addToMultiScanAndRun();
			if (beamLightShutter!= null) {
				beamLightShutter.moveTo("Close");
				logger.info("Close shutter called in EdeExperiment.runExperiment() at end of scan before writing ascii files");
				InterfaceProvider.getTerminalPrinter().print("Close shutter at end of scan, before writing ascii files.");
			}
			String asciiDataFile = writeToFiles();
			return asciiDataFile;
		} catch(Exception e) {
			logger.error("Error running experiment", e);
			throw e;
		} finally {
			theDetector.stop();
			if (beamLightShutter!= null) {
				//logger.warn("shutter closing being called in EdeExperiment.runExperiment()");
				//InterfaceProvider.getTerminalPrinter().print("Close shutter at end of experiment run.");
				beamLightShutter.moveTo("Close");
			}
		}
	}

	protected abstract String getHeaderText();

	protected abstract ExperimentCollectionType getCollectionType();

	protected abstract boolean shouldPublishItScanData(EdeScanProgressBean progress);

	private String addToMultiScanAndRun() throws Exception {
		try {
			ScanPlotSettings plotNothing = new ScanPlotSettings();
			plotNothing.setUnlistedColumnBehaviour(ScanPlotSettings.IGNORE);
			plotNothing.setYAxesShown(new String[]{});
			plotNothing.setYAxesNotShown(new String[]{});

			XasAsciiNexusDataWriter dataWriter = new XasAsciiNexusDataWriter();
			addMetaData(dataWriter);

			String template = fileNamePrefix.isEmpty() ? "ascii/" + "%d.dat" : "ascii/" + fileNamePrefix + "_%d.dat";
			dataWriter.setAsciiFileNameTemplate(template);

			template = fileNamePrefix.isEmpty() ? "nexus/" + "%d.nxs" : "nexus/" + fileNamePrefix + "_%d.nxs";
			dataWriter.setNexusFileNameTemplate(template);

			List<ScanBase> allScans = addAllScans();
			setMultiScan(new MultiScan(allScans));
			getMultiScan().setDataWriter(dataWriter);
			getMultiScan().setScanPlotSettings(plotNothing);

			logger.debug("Starting multiscan...");
			getMultiScan().runScan();
			return getMultiScan().getDataWriter().getCurrentFileName();
		} finally {
			NexusExtraMetadataDataWriter.removeAllMetadataEntries();
		}
	}

	private List<ScanBase> addAllScans() {
		List<ScanBase> scans = new ArrayList<ScanBase>();
		scans.addAll(scansBeforeIt);
		scans.addAll(scansForIt);
		scans.addAll(scansAfterIt);
		return scans;
	}

	private void clearScans() {
		scansBeforeIt.clear();
		scansForIt.clear();
		scansAfterIt.clear();
	}

	private String writeToFiles() throws Exception {
		try {
			writer = createFileWritter();
			writer.setSampleDetails(sampleDetails);
			logger.debug("EDE linear experiment writing its ascii and update nexus data files...");
			writer.writeDataFile(theDetector);
			logToJythonTerminal("Scan data written to file.");
			return writer.getAsciiFilename();
		} catch(Exception ex) {
			logger.error("Error creating data files", ex);
			throw new Exception("Error creating data files" , ex);
		}
	}

	protected abstract EdeExperimentDataWriter createFileWritter();

	// protected abstract double getTimeRequiredBeforeItCollection();
	// protected abstract double getTimeRequiredForItCollection();
	// protected abstract double getTimeRequiredAfterItCollection();

	protected double getTimeRequiredBeforeItCollection() {
		//Time to move from current motor position to I0 position
		double timeForI0Move = i0Position.getTimeToMove();

		//Time to move from I0 to It position
		double timeForItMove = ( (EdeScanMotorPositions) itPosition).getTimeToMove( (EdeScanMotorPositions)i0Position );

		double timeForI0Spectrum = i0ScanParameters.getTotalTime(); // total time for single I0 spectrum
		return timeForI0Spectrum*6 + timeForI0Move + timeForItMove;
	}

	protected double getTimeRequiredForLightI0Collection() {
		return 2.0*i0ScanParameters.getTotalTime();
	}

	protected double getTimeRequiredForItCollection() {
		double totalTime = itScanParameters.getTotalTime();
		return totalTime * getRepetitions();
	}

	protected double getTimeToMoveFromI0ToIt() {
		return ( (EdeScanMotorPositions) i0Position).getTimeToMove( (EdeScanMotorPositions)itPosition );
	}

	protected double getTimeRequiredAfterItCollection() {
		// Time for move from It to I0 position
		double timeForI0Move = ( (EdeScanMotorPositions) i0Position).getTimeToMove( (EdeScanMotorPositions)itPosition );
		double timeForSpectrum = getTimeRequiredForLightI0Collection();
		return timeForSpectrum + timeForI0Move;
	}

	protected double getTimeRequiredForFullExperiment() {
		return getTimeRequiredBeforeItCollection() + getTimeRequiredForItCollection() + getTimeRequiredAfterItCollection();
	}

	private void addMetaData(XasAsciiNexusDataWriter dataWriter) {
		StringBuilder metadataText = new StringBuilder();
		// Alignment parameters
		Object result = InterfaceProvider.getJythonNamespace().getFromJythonNamespace(ClientConfig.ALIGNMENT_PARAMETERS_RESULT_BEAN_NAME);
		if (result != null && (result instanceof AlignmentParametersBean)) {
			metadataText.append(result.toString());
		}
		metadataText.append(getHeaderText());
		if (!sampleDetails.isEmpty()) {
			metadataText.append("\nSample details: " + sampleDetails + "\n");

			ArrayList<String> arrayList = new ArrayList<String>();
			arrayList.add(sampleDetails);
			dataWriter.setDescriptions(arrayList);
		}
		NexusFileMetadata metadata = new NexusFileMetadata(theDetector.getName() + "_settings", metadataText.toString(),
				EntryTypes.NXinstrument, NXinstrumentSubTypes.NXdetector, theDetector.getName() + "_settings");
		NexusExtraMetadataDataWriter.addMetadataEntry(metadata);
	}

	public String getFileNamePrefix() {
		return fileNamePrefix;
	}

	public void setFileNamePrefix(String fileNamePrefix) {
		this.fileNamePrefix = fileNamePrefix;
	}

	public String getSampleDetails() {
		return sampleDetails;
	}

	public void setSampleDetails(String sampleDetails) {
		this.sampleDetails = sampleDetails;
	}

	public String getNexusFilename() {
		return nexusFilename;
	}

	protected void logToJythonTerminal(String message) {
		InterfaceProvider.getTerminalPrinter().print(message);
		logger.info(message);
	}

	protected TopupChecker createTopupChecker(Double realTimeRequired) {
		// Display warning in log panel rather than throw exception if 'before It' collection is longer than time between topups.
		if (realTimeRequired >= TOP_UP_TIME) {
			logger.info("Time required (" + realTimeRequired + ") secs is too large to fit within a topup");
		}

		double timeRequired = Math.min(TOP_UP_TIME-30, realTimeRequired); //otherwise if realTimeRequired>TOP_UP_TIME checker runs forever...

		double waitTime = 5.0, tolerance = 2.0;

		// Copy values for waittime and tolerance from machine topupChecker to this new topupchecker.
		TopupChecker topupCheckerMachine = (TopupChecker) Finder.getInstance().find("topupChecker");
		if (topupCheckerMachine != null) {
			tolerance = topupCheckerMachine.getTolerance();
			waitTime = topupCheckerMachine.getWaittime();
		}

		// timeout should be > collectiontime+tolerance+waitTime
		double timeout = 2.0*(waitTime+tolerance+timeRequired);

		logger.debug("createTopupChecker() : collectionTime = {}, timeout = {}, waitTime = {}, tolerance = {}", timeRequired, timeout, waitTime, tolerance);

		TopupChecker topupchecker = new TopupChecker();
		topupchecker.setName("EDE_scan_topup_checker");
		topupchecker.setScannableToBeMonitored(topup);
		topupchecker.setCollectionTime(timeRequired);
		topupchecker.setTimeout(timeout); // maximum time for how long to wait for topup to finish
		topupchecker.setWaittime(waitTime);  // how long to pause for after topup has finished (e.g. to wait for beam to stabilise)
		topupchecker.setTolerance(tolerance);

		topupchecker.setPauseBeforeScan(true);
		topupchecker.setPauseBeforePoint(false);

		// Set machine mode monitor object for topup object so it works correctly.
		Scannable machineModeMonitor = Finder.getInstance().find( "machineModeMonitor" );
		if ( machineModeMonitor != null ) {
			topupchecker.setMachineModeMonitor(machineModeMonitor);
		}
		return topupchecker;
	}

	/**
	 * Create topup checker for specified time interval
	 * @param timeRequired
	 * @param timeUntilNextTopup
	 * @return TopupChecker
	 * @since 29/2/2016
	 */
	protected TopupChecker createTopupChecker( double timeRequired, double timeUntilNextTopup ) {
		if (timeRequired < timeUntilNextTopup) {
			// Don't wait for topup
			return null;
		}
		return createTopupChecker(timeRequired);
	}

	protected TopupChecker createTopupCheckerForStartOfExperiment(double nextTopupTime) throws Exception {
		// double predictedExperimentTime = getTimeRequiredForFullExperiment();
		double timeForPreItScans = getTimeRequiredBeforeItCollection();
		if (timeForPreItScans < nextTopupTime) {
			// Don't wait for topup
			return null;
		}

		// Display warning in log panel rather than throw exception if 'before It' collection is longer than time between topups.
		if (timeForPreItScans >= TOP_UP_TIME) {
			logger.info("Time required for before It collection ("+timeForPreItScans+") secs is too large to fit within a topup");
		}

		return createTopupChecker(timeForPreItScans);
	}
	/**
	 * Create topup checker to be used for main It collection.
	 * @param nextTopupTime
	 * @return TopupChecker
	 * @throws Exception
	 * @since 22/1/2016
	 */
	protected TopupChecker createTopupCheckerForItCollection(double nextTopupTime) throws Exception {
		// double predictedExperimentTime = getTimeRequiredForFullExperiment();
		double timeForItScan = getTimeRequiredForItCollection();

		if (timeForItScan < nextTopupTime) {
			// Don't wait for topup
			return null;
		}

		// Display warning in log panel rather than throw exception if 'before It' collection is longer than time between topups. imh 14/10/2015
		if (timeForItScan >= TOP_UP_TIME) {
			logger.info("Time required for before It collection ("+timeForItScan+") secs is too large to fit within a topup");
		}
		return createTopupChecker(timeForItScan);

	}

	protected double getNextTopupTime() throws DeviceException {
		return (double) topup.getPosition();
	}

	public boolean getItWaitForTopup() {
		if ( itScanParameters.getGroups().size() > 0 ) {
			return itScanParameters.getGroups().get(0).getUseTopChecker();
		} else {
			return false;
		}
	}

	protected EdeScanPosition setPosition(EdePositionType type, Map<String, Double> scanableMotorPositions) throws DeviceException {
		// FIXME Replacing with alignment stage motors is removed until the requirement spec is cleared
		return new EdeScanMotorPositions(type, scanableMotorPositions);
	}

	private DoubleDataset lastEnergyData = null;
	private DoubleDataset lastI0DarkData = null;
	private DoubleDataset lastItDarkData = null;
	private DoubleDataset lastI0Data = null;
	private DoubleDataset lastItData = null;
	private DoubleDataset lastIRefData = null;
	private DoubleDataset lastI0ForIRefData = null;
	private DoubleDataset lastDarkRefData = null;
	private DoubleDataset lastIRefFinalData = null;
	private DoubleDataset lastI0FinalData = null;

	private MultiScan multiScan;
	@Override
	public void update(Object source, Object arg) {
		if (controller != null && arg instanceof EdeScanProgressBean) {
			EdeScanProgressBean progress = (EdeScanProgressBean) arg;
			if (source.equals(i0DarkScan)) {
				lastEnergyData = ScanDataHelper.extractDetectorEnergyFromSDP(theDetector.getName(), i0DarkScan.getData().get(0));
				if (!theDetector.isEnergyCalibrationSet()) {
					lastEnergyData.setName("Strip");
				}
				lastI0DarkData = i0DarkScan.extractLastDetectorDataSet();

				controller.update(i0DarkScan, new EdeExperimentProgressBean(getCollectionType(), progress,
						EdeDataConstants.I0_DARK_COLUMN_NAME, lastI0DarkData, lastEnergyData));
			}
			else if (source.equals(itDarkScan)) {
				lastItDarkData = itDarkScan.extractLastDetectorDataSet();
				controller.update(itDarkScan, new EdeExperimentProgressBean(getCollectionType(), progress,
						EdeDataConstants.IT_DARK_COLUMN_NAME, lastItDarkData, lastEnergyData));
			}
			else if (source.equals(i0LightScan)) {
				lastI0Data = i0LightScan.extractLastDetectorDataSet();
				// Get the first spectrum for each group is current group number because I0 has only one spectrum for each group
				int i0DarkSpectrumForCurrentGroup = progress.getGroupNumOfThisSDP();
				DoubleDataset i0DarkForI0LightData = i0DarkScan.extractDetectorDataSet(i0DarkSpectrumForCurrentGroup);
				lastI0Data = lastI0Data.isubtract(i0DarkForI0LightData);
				controller.update(i0LightScan, new EdeExperimentProgressBean(getCollectionType(), progress,
						EdeDataConstants.I0_CORR_COLUMN_NAME, lastI0Data, lastEnergyData));
			} else if (source.equals(i0FinalScan)) {
				lastI0FinalData = i0FinalScan.extractLastDetectorDataSet();
				// Get the first spectrum for each group is current group number because I0 has only one spectrum for each group
				int i0DarkSpectrumForCurrentGroup = progress.getGroupNumOfThisSDP();
				DoubleDataset i0DarkForI0LightData = i0DarkScan.extractDetectorDataSet(i0DarkSpectrumForCurrentGroup);
				lastI0FinalData = lastI0FinalData.isubtract(i0DarkForI0LightData);
				controller.update(i0LightScan, new EdeExperimentProgressBean(getCollectionType(), progress,
						EdeDataConstants.I0_FINAL_CORR_COLUMN_NAME, lastI0FinalData, lastEnergyData));
			} else if (source.equals(iRefDarkScan)) {
				lastDarkRefData = iRefDarkScan.extractLastDetectorDataSet();
				controller.update(itDarkScan, new EdeExperimentProgressBean(getCollectionType(), progress,
						EdeDataConstants.IREF_DARK_DATA_NAME, lastDarkRefData, lastEnergyData));
			}
			else if (source.equals(i0ForiRefScan)) {
				lastI0ForIRefData = i0ForiRefScan.extractLastDetectorDataSet();
				lastI0ForIRefData = lastI0ForIRefData.isubtract(lastDarkRefData);
			} else if (source.equals(iRefScan)) {
				lastIRefData = iRefScan.extractLastDetectorDataSet();
				lastIRefData = lastIRefData.isubtract(lastDarkRefData);
				DoubleDataset normalisedIRef = EdeExperimentDataWriter.normaliseDatasset(lastIRefData, lastI0ForIRefData);
				controller.update(source, new EdeExperimentProgressBean(getCollectionType(), progress, EdeDataConstants.LN_I0_IREF_COLUMN_NAME,
						normalisedIRef, lastEnergyData));
			} else if (source.equals(iRefFinalScan)) {
				lastIRefFinalData = iRefFinalScan.extractLastDetectorDataSet();
				lastIRefFinalData = lastIRefFinalData.isubtract(lastDarkRefData);
				DoubleDataset normalisedIRef = EdeExperimentDataWriter.normaliseDatasset(lastIRefFinalData, lastI0ForIRefData);
				controller.update(source, new EdeExperimentProgressBean(getCollectionType(), progress, EdeDataConstants.LN_I0_IREF_FINAL_COLUMN_NAME,
						normalisedIRef, lastEnergyData));
			} else if (ArrayUtils.contains(itScans, source)) {
				if (shouldPublishItScanData(progress)) {
					// TODO this will be affected by changes to EdeScan
					lastItData = ((EdeScan)source).extractLastDetectorDataSet();
					if (this.shouldRunItDark() & lastItDarkData != null) {
						int itDarkSpectrumForCurrentGroup = progress.getGroupNumOfThisSDP();
						DoubleDataset itDarkForItLightData = itDarkScan.extractDetectorDataSet(itDarkSpectrumForCurrentGroup);
						lastItData = lastItData.isubtract(itDarkForItLightData);
					} else {
						// If ItDark is not collected (which means each group parameters for It is the same as I0 parameters)
						int i0DarkSpectrumForCurrentGroup = progress.getGroupNumOfThisSDP();
						DoubleDataset i0DarkForItLightData = i0DarkScan.extractDetectorDataSet(i0DarkSpectrumForCurrentGroup);
						lastItData = lastItData.isubtract(i0DarkForItLightData);
					}
					controller.update(source, new EdeExperimentProgressBean(getCollectionType(), progress, EdeDataConstants.IT_CORR_COLUMN_NAME,
							lastItData, lastEnergyData));
					DoubleDataset normalisedIt = EdeExperimentDataWriter.normaliseDatasset(lastItData, lastI0Data);
					controller.update(source, new EdeExperimentProgressBean(getCollectionType(), progress,
							EdeDataConstants.LN_I0_IT_COLUMN_NAME, normalisedIt, lastEnergyData));
				}
			}
		}
	}

	public MultiScan getMultiScan() {
		return multiScan;
	}

	public void setMultiScan(MultiScan multiScan) {
		this.multiScan = multiScan;
	}

	public boolean getUseFastShutter() {
		return useFastShutter;
	}

	public void setUseFastShutter(boolean useFastShutter) {
		this.useFastShutter = useFastShutter;
	}

	public String getFastShutterName() {
		return fastShutterName;
	}

	public void setFastShutterName(String fastShutterName) {
		this.fastShutterName = fastShutterName;
	}

	public EdeScanMotorPositions getItScanPositions() {
		return (EdeScanMotorPositions)itPosition;
	}

	public EdeScanMotorPositions getI0ScanPositions() {
		return (EdeScanMotorPositions)i0Position;
	}

	public EdeScanParameters getItScanParameters() {
		return itScanParameters;
	}

	public void setItTriggerOptions(String itTriggerOptionsString) {
		this.itTriggerOptions = gson.fromJson(itTriggerOptionsString, TFGTrigger.class);
	}

	public void setItTriggerOptions(TFGTrigger itTriggerOptions) {
		this.itTriggerOptions = itTriggerOptions;
	}

	public TFGTrigger getItTriggerOptions() {
		return itTriggerOptions;
	}
}
