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

import gda.data.scan.datawriter.NexusExtraMetadataDataWriter;
import gda.data.scan.datawriter.NexusFileMetadata;
import gda.data.scan.datawriter.NexusFileMetadata.EntryTypes;
import gda.data.scan.datawriter.NexusFileMetadata.NXinstrumentSubTypes;
import gda.data.scan.datawriter.XasAsciiNexusDataWriter;
import gda.device.DeviceException;
import gda.device.Monitor;
import gda.device.Scannable;
import gda.device.detector.StripDetector;
import gda.device.scannable.TopupChecker;
import gda.factory.Findable;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.jython.scriptcontroller.ScriptControllerBase;
import gda.observable.IObserver;
import gda.scan.EdeWithTFGScan;
import gda.scan.EdeWithoutTriggerScan;
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

import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import org.apache.commons.lang.ArrayUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.gda.exafs.data.AlignmentParametersBean;
import uk.ac.gda.exafs.data.AlignmentParametersModel;
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

	private static final Logger logger = LoggerFactory.getLogger(EdeExperiment.class);

	/**
	 * The name of the ScriptController object which is sent progress information and normalised spectra by experiments
	 */
	public static final String PROGRESS_UPDATER_NAME = "EDEProgressUpdater";

	protected final int firstRepetitionIndex = 0; // in case we switch to 1-based indexing

	protected EdeScanParameters iRefScanParameters;
	protected EdeScanPosition i0ForiRefPosition;
	protected EdeScanPosition iRefPosition;
	protected EdeScanParameters i0ForiRefScanParameters;

	protected EdeWithoutTriggerScan iRefFinalScan;
	protected EdeWithoutTriggerScan i0ForiRefScan;
	protected EdeWithoutTriggerScan iRefScan;
	protected EdeWithoutTriggerScan iRefDarkScan;
	protected boolean runIRef;

	protected Scannable beamLightShutter;
	protected StripDetector theDetector;
	protected EdeWithoutTriggerScan i0DarkScan;
	protected EdeWithoutTriggerScan itDarkScan;
	protected EdeWithoutTriggerScan i0LightScan;
	protected EdeWithoutTriggerScan itLightScan;
	protected EdeWithoutTriggerScan i0FinalScan;
	protected EdeWithTFGScan[] itScans;
	protected final EdeScanParameters itScanParameters;
	protected final LinkedList<ScanBase> scansForExperiment = new LinkedList<ScanBase>();

	protected EdeScanParameters i0ScanParameters;
	protected EdeScanPosition i0Position;
	protected EdeScanPosition itPosition;
	protected EdeExperimentDataWriter writer;
	protected String nexusFilename;

	protected ScriptControllerBase controller;

	private String fileNamePrefix = "";

	private Monitor topup;


	public EdeExperiment(List<TimingGroup> itTimingGroups,
			Map<String, Double> i0ScanableMotorPositions,
			Map<String, Double> iTScanableMotorPositions,
			String detectorName, String topupMonitorName, String beamShutterScannableName) throws DeviceException {
		itScanParameters = new EdeScanParameters();
		itScanParameters.setGroups(itTimingGroups);
		setupScannables(i0ScanableMotorPositions, iTScanableMotorPositions, detectorName, topupMonitorName,
				beamShutterScannableName);
	}

	public EdeExperiment(EdeScanParameters itScanParameters,
			Map<String, Double> i0ScanableMotorPositions,
			Map<String, Double> iTScanableMotorPositions,
			String detectorName, String topupMonitorName, String beamShutterScannableName) throws DeviceException {
		this.itScanParameters = itScanParameters;
		setupScannables(i0ScanableMotorPositions, iTScanableMotorPositions, detectorName, topupMonitorName,
				beamShutterScannableName);
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

	private void setupScannables(Map<String, Double> i0ScanableMotorPositions,
			Map<String, Double> iTScanableMotorPositions, String detectorName, String topupMonitorName,
			String beamShutterScannableName) throws DeviceException {
		i0Position = this.setPosition(EdePositionType.OUTBEAM, i0ScanableMotorPositions);
		itPosition = this.setPosition(EdePositionType.INBEAM, iTScanableMotorPositions);
		theDetector  = Finder.getInstance().find(detectorName);
		topup = (Monitor) getFindable(topupMonitorName);
		beamLightShutter = (Scannable) getFindable(beamShutterScannableName);
		controller = (ScriptControllerBase) getFindable(PROGRESS_UPDATER_NAME);
	}

	protected void setCommonI0Parameters(double accumulationTime, int numberOfAccumulcations) {
		i0ScanParameters = this.deriveScanParametersFromIt(accumulationTime, numberOfAccumulcations);
	}

	protected void setDefaultI0Parameters(double accumulationTime) {
		i0ScanParameters = this.deriveScanParametersFromIt(accumulationTime, null);
	}

	protected EdeScanParameters deriveScanParametersFromIt(Double commonAccumulationTime, Integer commonNumberOfAccumulcations) {
		// need an I0 spectrum for each timing group in itScanParameters
		List<TimingGroup> itgroups = itScanParameters.getGroups();

		EdeScanParameters parameters = new EdeScanParameters();
		for (TimingGroup itGroup : itgroups) {
			TimingGroup newGroup = new TimingGroup();
			newGroup.setLabel(itGroup.getLabel());
			newGroup.setNumberOfFrames(1);
			if(commonAccumulationTime == null) {
				newGroup.setTimePerScan(itGroup.getTimePerScan());
			} else {
				newGroup.setTimePerScan(commonAccumulationTime);
			}
			if(commonNumberOfAccumulcations == null) {
				newGroup.setNumberOfScansPerFrame(itGroup.getNumberOfScansPerFrame());
			} else {
				newGroup.setNumberOfScansPerFrame(commonNumberOfAccumulcations);
			}
			newGroup.setTimePerFrame(itGroup.getTimePerFrame());
			newGroup.setDelayBetweenFrames(0);
			parameters.addGroup(newGroup);
		}
		return parameters;
	}

	private EdeScanParameters deriveItDarkParametersFromItParameters() {
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

	private void addScansForExperiment() {
		int repetitions = getRepetitions();

		i0DarkScan = new EdeWithoutTriggerScan(i0ScanParameters, i0Position, EdeScanType.DARK, theDetector, firstRepetitionIndex, beamLightShutter,createTopupCheckerForBeforeItScans());
		i0DarkScan.setProgressUpdater(this);
		scansForExperiment.add(i0DarkScan);

		if (runIRef) {
			iRefDarkScan = new EdeWithoutTriggerScan(iRefScanParameters, iRefPosition, EdeScanType.DARK, theDetector, firstRepetitionIndex, beamLightShutter, null);
			scansForExperiment.add(iRefDarkScan);
			iRefDarkScan.setProgressUpdater(this);
		}

		if (shouldRunItDark()) {
			EdeScanParameters itDarkScanParameters = deriveItDarkParametersFromItParameters();
			itDarkScan = new EdeWithoutTriggerScan(itDarkScanParameters, itPosition, EdeScanType.DARK, theDetector, firstRepetitionIndex, beamLightShutter, null);
			itDarkScan.setProgressUpdater(this);
			scansForExperiment.add(itDarkScan);
		} else {
			itDarkScan = i0DarkScan;
		}

		i0LightScan = new EdeWithoutTriggerScan(i0ScanParameters, i0Position, EdeScanType.LIGHT, theDetector, firstRepetitionIndex, beamLightShutter, null);
		i0LightScan.setProgressUpdater(this);
		scansForExperiment.add(i0LightScan);

		if (runIRef) {
			i0ForiRefScan = new EdeWithoutTriggerScan(i0ForiRefScanParameters, i0ForiRefPosition, EdeScanType.LIGHT, theDetector, firstRepetitionIndex, beamLightShutter, null);
			scansForExperiment.add(i0ForiRefScan);
			i0ForiRefScan.setProgressUpdater(this);

			iRefScan = new EdeWithoutTriggerScan(iRefScanParameters, iRefPosition, EdeScanType.LIGHT, theDetector, firstRepetitionIndex, beamLightShutter, null);
			scansForExperiment.add(iRefScan);
			iRefScan.setProgressUpdater(this);
		}

		itScans = new EdeWithTFGScan[repetitions];
		for(int repIndex = 0; repIndex < repetitions; repIndex++){
			itScans[repIndex] = new EdeWithTFGScan(itScanParameters, itPosition, EdeScanType.LIGHT, theDetector, repIndex, beamLightShutter);
			itScans[repIndex].setProgressUpdater(this);
			scansForExperiment.add(itScans[repIndex]);
		}

		addFinalScans();
	}

	protected abstract void addFinalScans();

	public String runExperiment() throws Exception {
		try {
			scansForExperiment.clear();
			addScansForExperiment();
			nexusFilename = addToMultiScanAndRun();
			String asciiDataFile = writeToFiles();
			return asciiDataFile;
		} catch(Exception e) {
			logger.error("Error running experiment", e);
			throw e;
		}
	}

	protected abstract String getHeaderText();

	protected abstract ExperimentCollectionType getCollectionType();

	protected abstract boolean shouldPublishItScanData(EdeScanProgressBean progress);

	private String addToMultiScanAndRun() throws Exception {
		try {
			addMetaData();
			ScanPlotSettings plotNothing = new ScanPlotSettings();
			plotNothing.setUnlistedColumnBehaviour(ScanPlotSettings.IGNORE);
			plotNothing.setYAxesShown(new String[]{});
			plotNothing.setYAxesNotShown(new String[]{});

			XasAsciiNexusDataWriter dataWriter = new XasAsciiNexusDataWriter();

			String template = fileNamePrefix.isEmpty() ? "ascii/" + "%d.dat" : "ascii/" + fileNamePrefix + "_%d.dat";
			dataWriter.setAsciiFileNameTemplate(template);

			template = fileNamePrefix.isEmpty() ? "nexus/" + "%d.nxs" : "nexus/" + fileNamePrefix + "_%d.nxs";
			dataWriter.setNexusFileNameTemplate(template);
			MultiScan theScan = new MultiScan(scansForExperiment);
			theScan.setDataWriter(dataWriter);
			theScan.setScanPlotSettings(plotNothing);

			//			pauseForTopupBeforeStartingScans();
			logger.debug("Starting multiscan...");
			theScan.runScan();
			return theScan.getDataWriter().getCurrentFileName();
		} finally {
			NexusExtraMetadataDataWriter.removeAllMetadataEntries();
		}
	}

	private String writeToFiles() throws Exception {
		try {
			writer = createFileWritter();
			logger.debug("EDE linear experiment writing its ascii and update nexus data files...");
			writer.writeDataFile();
			log("Scan data written to file.");
			return writer.getAsciiFilename();
		} catch(Exception ex) {
			logger.error("Error creating data files", ex);
			throw new Exception("Error creating data files" , ex);
		}
	}

	protected abstract EdeExperimentDataWriter createFileWritter();

	protected abstract double getTimeRequiredBeforeTopup();

	private void addMetaData() {
		StringBuilder metadataText = new StringBuilder();
		// Alignment parameters
		Object result = InterfaceProvider.getJythonNamespace()
				.getFromJythonNamespace(AlignmentParametersModel.ALIGNMENT_PARAMETERS_RESULT_BEAN_NAME);
		if (result != null && (result instanceof AlignmentParametersBean)) {
			metadataText.append(result.toString());
		}
		metadataText.append(getHeaderText());
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

	public String getNexusFilename() {
		return nexusFilename;
	}

	protected void log(String message) {
		InterfaceProvider.getTerminalPrinter().print(message);
		logger.info(message);
	}

	protected TopupChecker createTopupChecker(Double timeRequired) {
		TopupChecker topupchecker = new TopupChecker();
		topupchecker.setName("EDE_scan_topup_checker");
		topupchecker.setScannableToBeMonitored(topup);
		topupchecker.setCollectionTime(timeRequired);
		topupchecker.setTimeout(timeRequired * 1.25);
		topupchecker.setWaittime(10); // fixed for EDE beamline
		topupchecker.setTolerance(0);
		topupchecker.setPauseBeforeScan(true);
		topupchecker.setPauseBeforePoint(false);
		return topupchecker;
	}

	private TopupChecker createTopupCheckerForBeforeItScans() {
		double predictedExperimentTime = getTimeRequiredBeforeTopup();
		return createTopupChecker(predictedExperimentTime);
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
	@Override
	public void update(Object source, Object arg) {
		if (controller != null && arg instanceof EdeScanProgressBean) {
			EdeScanProgressBean progress = (EdeScanProgressBean) arg;
			if (source.equals(i0DarkScan)) {
				lastEnergyData = ScanDataHelper.extractDetectorEnergyFromSDP(theDetector.getName(), i0DarkScan.getData().get(0));
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
				DoubleDataset i0DarkForI0LightData = i0FinalScan.extractDetectorDataSet(i0DarkSpectrumForCurrentGroup);
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
					lastItData = ((EdeWithoutTriggerScan)source).extractLastDetectorDataSet();
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

}
