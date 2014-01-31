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
import gda.scan.EdeScan;
import gda.scan.MultiScan;
import gda.scan.ScanBase;
import gda.scan.ScanPlotSettings;
import gda.scan.ede.EdeExperimentProgressBean.ExperimentCollectionType;
import gda.scan.ede.datawriters.EdeAsciiFileWriter;
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

	public static final String TIMINGGROUP_COLUMN_NAME = "Timing_Group";
	public static final String FRAME_COLUMN_NAME = "Frame";
	public static final String STRIP_COLUMN_NAME = "Strip";
	public static final String ENERGY_COLUMN_NAME = "Energy";
	public static final String I0_CORR_COLUMN_NAME = "I0_corr";
	public static final String IT_CORR_COLUMN_NAME = "It_corr";
	public static final String LN_I0_IT_COLUMN_NAME = "LnI0It";
	public static final String LN_I0_IREF_COLUMN_NAME = "LnI0IRef";
	public static final String I0_RAW_COLUMN_NAME = "I0_raw";
	public static final String IT_RAW_COLUMN_NAME = "It_raw";
	public static final String I0_DARK_COLUMN_NAME = "I0_dark";
	public static final String IT_DARK_COLUMN_NAME = "It_dark";
	public static final String DATA_COLUMN_NAME = "Data";
	/**
	 * The name of the ScriptController object which is sent progress information and normalised spectra by experiments
	 */
	public static final String PROGRESS_UPDATER_NAME = "EDEProgressUpdater";

	protected final int firstRepetitionIndex = 0; // in case we swicth to 1-based indexing

	protected EdeScanParameters iRefScanParameters;
	protected EdeScanPosition iRefPosition;
	protected EdeScan iRefScan;
	protected EdeScan i0ForIRefScan;
	protected EdeScan iRefFinalScan;
	protected boolean runIRef;
	protected boolean runI0ForIRef;

	protected Scannable beamLightShutter;
	protected StripDetector theDetector;
	protected EdeScan i0DarkScan;
	protected EdeScan itDarkScan;
	protected EdeScan i0InitialScan;
	protected EdeScan[] itScans;
	protected final EdeScanParameters itScanParameters;
	protected final LinkedList<ScanBase> scansForExperiment = new LinkedList<ScanBase>();

	protected EdeScanParameters i0ScanParameters;
	protected EdeScanPosition i0Position;
	protected EdeScanPosition itPosition;
	protected EdeAsciiFileWriter writer;
	protected String nexusFilename;

	private ScriptControllerBase controller;
	private String filenameTemplate = "";
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

	public void setIRefParameters(Map<String, Double> iRefScanableMotorPositions, double accumulationTime, int numberOfAccumulcations) throws DeviceException {
		iRefPosition = this.setPosition(EdePositionType.REFERENCE, iRefScanableMotorPositions);
		iRefScanParameters = this.deriveScanParametersFromIt(accumulationTime, numberOfAccumulcations);
		runIRef = true;
		runI0ForIRef = true;
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

	private Findable getFindable(String name) {
		return Finder.getInstance().find(name);
	}

	protected abstract int getRepetitions();

	protected abstract boolean shouldRunItDark();

	protected void addScansForExperiment() {
		int repetitions = getRepetitions();

		i0DarkScan = new EdeScan(i0ScanParameters, i0Position, EdeScanType.DARK, theDetector, firstRepetitionIndex, beamLightShutter);
		i0DarkScan.setProgressUpdater(this);
		scansForExperiment.add(i0DarkScan);

		if (shouldRunItDark()) {
			itDarkScan = new EdeScan(itScanParameters, itPosition, EdeScanType.DARK, theDetector, firstRepetitionIndex, beamLightShutter);
			itDarkScan.setProgressUpdater(this);
			scansForExperiment.add(itDarkScan);
		} else {
			itDarkScan = i0DarkScan;
		}

		i0InitialScan = new EdeScan(i0ScanParameters, i0Position, EdeScanType.LIGHT, theDetector, firstRepetitionIndex, beamLightShutter);
		i0InitialScan.setProgressUpdater(this);
		scansForExperiment.add(i0InitialScan);

		if (runIRef) {
			if (runI0ForIRef) {
				i0ForIRefScan = new EdeScan(iRefScanParameters, iRefPosition, EdeScanType.DARK, theDetector, firstRepetitionIndex, beamLightShutter);
				scansForExperiment.add(i0ForIRefScan);
				i0ForIRefScan.setProgressUpdater(this);
			}
			iRefScan = new EdeScan(iRefScanParameters, iRefPosition, EdeScanType.LIGHT, theDetector, firstRepetitionIndex, beamLightShutter);
			scansForExperiment.add(iRefScan);
			iRefScan.setProgressUpdater(this);
		}

		itScans = new EdeScan[repetitions];
		for(int repIndex = 0; repIndex < repetitions; repIndex++){
			itScans[repIndex] = new EdeScan(itScanParameters, itPosition, EdeScanType.LIGHT, theDetector, repIndex, beamLightShutter);
			itScans[repIndex].setProgressUpdater(this);
			scansForExperiment.add(itScans[repIndex]);
		}


	}

	public String runExperiment() throws Exception {
		scansForExperiment.clear();
		addScansForExperiment();
		nexusFilename = addToMultiScanAndRun();
		String asciiDataFile = writeAsciiFile();
		return asciiDataFile;
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

			MultiScan theScan = new MultiScan(scansForExperiment);
			theScan.setScanPlotSettings(plotNothing);

			pauseForToup();
			logger.debug("Starting multiscan...");
			theScan.runScan();
			return theScan.getDataWriter().getCurrentFileName();
		} finally {
			NexusExtraMetadataDataWriter.removeAllMetadataEntries();
		}
	}

	private String writeAsciiFile() throws Exception {
		writer = createFileWritter();
		if (filenameTemplate != null && !filenameTemplate.isEmpty()) {
			writer.setFilenameTemplate(filenameTemplate);
		}
		logger.debug("EDE linear experiment writing its ascii derived data files...");
		writer.writeAsciiFile();
		log("EDE single spectrum experiment complete.");
		return writer.getAsciiFilename();
	}

	protected abstract EdeAsciiFileWriter createFileWritter();

	protected abstract double getPredictedExperimentTime();

	private void pauseForToup() throws Exception {
		double predictedExperimentTime = getPredictedExperimentTime();
		TopupChecker topup = createTopupChecker(predictedExperimentTime);
		topup.atScanStart();
	}

	private void addMetaData() {
		String headerText = getHeaderText();
		NexusFileMetadata metadata = new NexusFileMetadata(theDetector.getName() + "_settings", headerText,
				EntryTypes.NXinstrument, NXinstrumentSubTypes.NXdetector, theDetector.getName() + "_settings");
		NexusExtraMetadataDataWriter.addMetadataEntry(metadata);
	}

	public String getFilenameTemplate() {
		return filenameTemplate;
	}
	/**
	 * A String format for the name of the ascii file to be written.
	 * <p>
	 * It <b>must</b> contain a '%s' to substitute the nexus file name into the given template.
	 * <p>
	 * E.g. if the nexus file created was: '/dls/i01/data/1234.nxs' then the filenameTemplate given in this method
	 * should be something like: 'Fe-Kedge_%s' for the final ascii file to be: '/dls/i01/data/Fe-Kedge_1234.txt'
	 * 
	 * @param filenameTemplate
	 */
	public void setFilenameTemplate(String filenameTemplate) {
		this.filenameTemplate = filenameTemplate;
	}

	protected void log(String message) {
		InterfaceProvider.getTerminalPrinter().print(message);
		logger.info(message);
	}

	private TopupChecker createTopupChecker(Double timeRequired) {
		TopupChecker topupchecker = new TopupChecker();
		topupchecker.setScannableToBeMonitored(topup);
		topupchecker.setTimeout(timeRequired);
		topupchecker.setWaittime(10); // fixed for EDE beamline
		topupchecker.setTolerance(0);
		topupchecker.setPauseBeforeScan(true);
		topupchecker.setPauseBeforePoint(false);
		return topupchecker;
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

	@Override
	public void update(Object source, Object arg) {
		if (controller != null && arg instanceof EdeScanProgressBean) {
			EdeScanProgressBean progress = (EdeScanProgressBean) arg;
			if (source.equals(i0DarkScan)) {
				lastEnergyData = EdeAsciiFileWriter.extractDetectorEnergyFromSDP(theDetector.getName(), i0DarkScan.getData().get(0));
				lastI0DarkData = EdeAsciiFileWriter.extractDetectorDataSets(theDetector.getName(), i0DarkScan, 0);
				controller.update(i0DarkScan, new EdeExperimentProgressBean(getCollectionType(), progress,
						EdeExperiment.I0_DARK_COLUMN_NAME, lastI0DarkData, lastEnergyData));
			}
			else if (source.equals(itDarkScan)) {
				lastItDarkData = EdeAsciiFileWriter.extractDetectorDataSets(theDetector.getName(), itDarkScan, 0);
				controller.update(itDarkScan, new EdeExperimentProgressBean(getCollectionType(), progress,
						EdeExperiment.IT_DARK_COLUMN_NAME, lastItDarkData, lastEnergyData));
			}
			else if (source.equals(i0InitialScan)) {
				lastI0Data = EdeAsciiFileWriter.extractDetectorDataSets(theDetector.getName(), i0InitialScan, 0);
				if (lastI0DarkData != null) {
					lastI0Data = lastI0Data.isubtract(lastI0DarkData);
				}
				controller.update(i0InitialScan, new EdeExperimentProgressBean(getCollectionType(), progress,
						EdeExperiment.I0_CORR_COLUMN_NAME, lastI0Data, lastEnergyData));
			}
			else if (ArrayUtils.contains(itScans, source)) {
				if (shouldPublishItScanData(progress)) {
					lastItData = EdeAsciiFileWriter.extractDetectorDataSets(theDetector.getName(), (EdeScan) source, 0);
					if (this.shouldRunItDark() & lastItDarkData != null) {
						lastItData = lastItData.isubtract(lastItDarkData);
					} else {
						lastItData = lastItData.isubtract(lastI0DarkData);
					}
					controller.update(source, new EdeExperimentProgressBean(getCollectionType(), progress, EdeExperiment.IT_CORR_COLUMN_NAME,
							lastItData, lastEnergyData));
					DoubleDataset normalisedIt = EdeAsciiFileWriter.normaliseDatasset(lastItData, lastI0Data);
					controller.update(source, new EdeExperimentProgressBean(getCollectionType(), progress, EdeExperiment.LN_I0_IT_COLUMN_NAME,
							normalisedIt, lastEnergyData));
				}
			}
		}
	}

}
