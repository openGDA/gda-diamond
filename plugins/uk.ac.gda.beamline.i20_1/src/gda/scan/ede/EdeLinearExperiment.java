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
import gda.factory.Finder;
import gda.observable.IObserver;
import gda.scan.AxisSpecProviderImpl;
import gda.scan.EdeScan;
import gda.scan.MultiScan;
import gda.scan.ScanBase;
import gda.scan.ScanPlotSettings;
import gda.scan.ede.EdeExperimentProgressBean.ExperimentCollectionType;
import gda.scan.ede.datawriters.EdeAsciiFileWriter;
import gda.scan.ede.datawriters.EdeLinearExperimentAsciiFileWriter;
import gda.scan.ede.position.EdePositionType;
import gda.scan.ede.position.EdeScanPosition;
import gda.scan.ede.timeestimators.LinearExperimentTimeEstimator;

import java.util.List;
import java.util.Map;
import java.util.Vector;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

/**
 * Similar to the {@link EdeLinearExperiment} class except that a series of TimingGroups are run which will produce
 * multiple spectra. In other words the itScanParameters given to this class is not assumed to be a single timing group
 * producing a single spectrum.
 * <p>
 * The experiment is not repeated, so all the spectra will occur at a different point in time wrt the progress of a
 * chemical reaction or other state of the sample.
 */
public class EdeLinearExperiment extends EdeExperiment implements IObserver {

	private static final Logger logger = LoggerFactory.getLogger(EdeLinearExperiment.class);

	private final EdeScanPosition i0Position;
	private final EdeScanPosition itPosition;
	private EdeScanPosition iRefPosition;
	private final StripDetector theDetector;

	public static final int DEFALT_NO_OF_SEC_PER_SPECTRUM_TO_PUBLISH = 2;
	private int noOfSecPerSpectrumToPublish = DEFALT_NO_OF_SEC_PER_SPECTRUM_TO_PUBLISH;
	private int totalNumberOfspectra;
	private double totalTime;

	private final EdeScanParameters itScanParameters;
	private EdeScanParameters i0ScanParameters;
	private EdeScanParameters iRefScanParameters;
	private EdeScan i0DarkScan;
	private EdeScan i0InitialScan;
	private EdeScan iRefScan;
	private EdeScan itScan;
	private EdeScan i0FinalScan;
	private EdeScan iRefFinalScan;
	private EdeLinearExperimentAsciiFileWriter writer;
	private final Scannable beamShutter;

	public EdeLinearExperiment(List<TimingGroup> itTimingGroups,
			Map<String, Double> i0ScanableMotorPositions,
			Map<String, Double> iTScanableMotorPositions,
			String detectorName, String topupMonitorName, String beamShutterScannableName) throws DeviceException {
		itScanParameters = new EdeScanParameters();
		itScanParameters.setGroups(itTimingGroups);
		i0Position = this.setPosition(EdePositionType.OUTBEAM, i0ScanableMotorPositions);
		itPosition = this.setPosition(EdePositionType.INBEAM, iTScanableMotorPositions);
		theDetector  = Finder.getInstance().find(detectorName);
		topup = Finder.getInstance().find(topupMonitorName);
		beamShutter = Finder.getInstance().find(beamShutterScannableName);
		calculateTotalNoOfSpectra();
	}

	public void setIRefParameters(Map<String, Double> iRefScanableMotorPositions) throws DeviceException {
		iRefPosition = this.setPosition(EdePositionType.REFERENCE, iRefScanableMotorPositions);
	}

	public void setIRefParameters(Map<String, Double> iRefScanableMotorPositions, double accumulationTime, int numberOfAccumulcations) throws DeviceException {
		iRefPosition = this.setPosition(EdePositionType.REFERENCE, iRefScanableMotorPositions);
		iRefScanParameters = this.deriveScanParametersFromIt(accumulationTime, numberOfAccumulcations);
	}

	public void setCommonI0Parameters(double accumulationTime, int numberOfAccumulcations) {
		i0ScanParameters = this.deriveScanParametersFromIt(accumulationTime, numberOfAccumulcations);
	}

	public EdeLinearExperiment(EdeScanParameters itScanParameters, EdeScanPosition i0Position,
			EdeScanPosition itPosition, EdeScanPosition iRefPosition, StripDetector theDetector, Monitor topupMonitor, Scannable shutter2) {
		super();
		this.itScanParameters = itScanParameters;
		this.i0Position = i0Position;
		this.itPosition = itPosition;
		this.iRefPosition = iRefPosition;
		this.theDetector = theDetector;
		beamShutter = shutter2;
		topup = topupMonitor;
		calculateTotalNoOfSpectra();
	}

	private void calculateTotalNoOfSpectra() {
		totalNumberOfspectra = 0;
		totalTime = 0.0;
		for (TimingGroup group : itScanParameters.getTimingGroups()) {
			totalNumberOfspectra += group.getNumberOfFrames();
			totalTime += (group.getTimePerFrame() * group.getNumberOfFrames()) + group.getPreceedingTimeDelay();
		}
	}

	/**
	 * Run the scans and write the data files.
	 * <p>
	 * Should not return until data collection completed.
	 * 
	 * @throws Exception
	 */
	@Override
	public String runExperiment() throws Exception {
		if (i0ScanParameters == null) {
			i0ScanParameters = deriveScanParametersFromIt(null, null);
		}
		if (iRefPosition !=null & iRefScanParameters == null) {
			iRefScanParameters = this.deriveScanParametersFromIt(null, null);
		}
		runScans();
		return writeAsciiFile();
	}

	@Override
	public void update(Object source, Object arg) {
		// only expect EdeScanProgressBean objects from the itScan here. Normalise the data and broadcast out to the
		if (controller != null && arg instanceof EdeScanProgressBean) {
			EdeScanProgressBean progress = (EdeScanProgressBean) arg;
			if (source.equals(itScan)) {
				if (!shouldPublishItScanData(progress)) {
					return;
				}
				// assume that the I0 and dark scans have run correctly if we are getting messages back from It scan
				DoubleDataset darkData = EdeAsciiFileWriter.extractDetectorDataSets(theDetector.getName(), i0DarkScan, 0);
				DoubleDataset i0Data = EdeAsciiFileWriter.extractDetectorDataSets(theDetector.getName(), i0InitialScan, progress.getGroupNumOfThisSDP());
				DoubleDataset thisItData = EdeAsciiFileWriter.extractDetectorDataFromSDP(theDetector.getName(), progress.getThisPoint());
				DoubleDataset normalisedIt = EdeAsciiFileWriter.normaliseDatasset(thisItData, i0Data, darkData);
				DoubleDataset energyData = EdeAsciiFileWriter.extractDetectorEnergyFromSDP(theDetector.getName(), i0DarkScan.getData().get(0));
				controller.update(itScan, new EdeExperimentProgressBean(ExperimentCollectionType.MULTI, progress, EdeExperiment.IT_RAW_COLUMN_NAME, thisItData, energyData));
				controller.update(itScan, new EdeExperimentProgressBean(ExperimentCollectionType.MULTI, progress, EdeExperiment.LN_I0_IT_COLUMN_NAME, normalisedIt, energyData));
			} else if (source.equals(i0DarkScan)) {
				DoubleDataset darkData = EdeAsciiFileWriter.extractDetectorDataSets(theDetector.getName(), i0DarkScan, 0);
				DoubleDataset energyData = EdeAsciiFileWriter.extractDetectorEnergyFromSDP(theDetector.getName(), i0DarkScan.getData().get(0));
				controller.update(itScan, new EdeExperimentProgressBean(ExperimentCollectionType.MULTI, progress, EdeExperiment.I0_DARK_COLUMN_NAME, darkData, energyData));
			} else if (source.equals(i0InitialScan)) {
				DoubleDataset i0Data = EdeAsciiFileWriter.extractDetectorDataSets(theDetector.getName(), i0InitialScan, progress.getGroupNumOfThisSDP());
				DoubleDataset energyData = EdeAsciiFileWriter.extractDetectorEnergyFromSDP(theDetector.getName(), i0InitialScan.getData().get(0));
				controller.update(itScan, new EdeExperimentProgressBean(ExperimentCollectionType.MULTI, progress, EdeExperiment.I0_RAW_COLUMN_NAME, i0Data, energyData));
			}
		}
	}

	private boolean shouldPublishItScanData(EdeScanProgressBean progress) {
		int current = 0;
		for (int i = 0; i < progress.getGroupNumOfThisSDP(); i++) {
			current += itScan.getScanParameters().getTimingGroups().get(i).getNumberOfFrames();
		}
		if (current == 0) {
			return true;
		}
		current += progress.getFrameNumOfThisSDP() + 1; // + 1 because it is 0 index
		int avg = (int) (totalNumberOfspectra / (totalTime / noOfSecPerSpectrumToPublish));
		if (avg < 1) {
			avg = 1;
		}
		if (current % avg == 0 || current == totalNumberOfspectra) {
			return true;
		}
		return false;
	}

	/**
	 * NPE if this is called before the scan has been run and the datawriter has been created
	 * 
	 * @return the name of the I0 output file
	 */
	public String getI0Filename() {
		return writer.getAsciiI0Filename();
	}

	/**
	 * NPE if this is called before the scan has been run and the datawriter has been created
	 * 
	 * @return the name of the I0 output file
	 */
	public String getIRefFilename() {
		return writer.getAsciiIRefFilename();
	}

	/**
	 * NPE if this is called before the scan has been run and the datawriter has been created
	 * 
	 * @return the name of the It output file
	 */
	public String getItFilename() {
		return writer.getAsciiItFilename();
	}

	/**
	 * NPE if this is called before the scan has been run and the datawriter has been created
	 * 
	 * @return the name of the It output file
	 */
	public String getItFinalFilename() {
		return writer.getAsciiItFinalFilename();
	}

	/**
	 * NPE if this is called before the scan has been run and the datawriter has been created
	 * 
	 * @return the name of the It output file
	 */
	public String getItAveragedFilename() {
		return writer.getAsciiItAveragedFilename();
	}


	private EdeScanParameters deriveScanParametersFromIt(Double commonAccumulationTime, Integer commonNumberOfAccumulcations) {
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

	public int getNoOfSecPerSpectrumToPublish() {
		return noOfSecPerSpectrumToPublish;
	}


	public void setNoOfSecPerSpectrumToPublish(int noOfSecPerSpectrumToPublish) {
		this.noOfSecPerSpectrumToPublish = noOfSecPerSpectrumToPublish;
	}


	private void runScans() throws InterruptedException, Exception {
		i0DarkScan = new EdeScan(i0ScanParameters, i0Position, EdeScanType.DARK, theDetector, 1, beamShutter);
		i0DarkScan.setProgressUpdater(this);
		i0InitialScan = new EdeScan(i0ScanParameters, i0Position, EdeScanType.LIGHT, theDetector, 1, beamShutter);
		i0InitialScan.setProgressUpdater(this);
		if (iRefPosition != null) {
			iRefScan = new EdeScan(iRefScanParameters, iRefPosition, EdeScanType.LIGHT, theDetector, 1, beamShutter);
		}
		itScan = new EdeScan(itScanParameters, itPosition, EdeScanType.LIGHT, theDetector, 1, beamShutter);
		itScan.setProgressUpdater(this);
		i0FinalScan = new EdeScan(i0ScanParameters, i0Position, EdeScanType.LIGHT, theDetector, 1, beamShutter);
		if (iRefPosition != null){
			iRefFinalScan = new EdeScan(i0ScanParameters, iRefPosition, EdeScanType.LIGHT, theDetector, 1, beamShutter);
		}

		List<ScanBase> theScans = new Vector<ScanBase>();
		theScans.add(i0DarkScan);
		theScans.add(i0InitialScan);
		if (iRefPosition != null){
			theScans.add(iRefScan);
		}
		theScans.add(itScan);
		theScans.add(i0FinalScan);
		if (iRefPosition != null){
			theScans.add(iRefFinalScan);
		}

		try {
			addDetectorSettingsToMetadata();

			ScanPlotSettings plotNothing = new ScanPlotSettings();
			plotNothing.setUnlistedColumnBehaviour(ScanPlotSettings.IGNORE);
			plotNothing.setYAxesShown(theDetector.getExtraNames());
			plotNothing.setYAxesNotShown(new String[]{});
			plotNothing.setAxisSpecProvider(new AxisSpecProviderImpl(false));

			MultiScan theScan = new MultiScan(theScans);
			theScan.setScanPlotSettings(plotNothing);
			pauseForToup();
			logger.debug("EDE linear experiment starting its multiscan...");
			theScan.runScan();
		} finally {
			NexusExtraMetadataDataWriter.removeAllMetadataEntries();
		}
	}

	private void addDetectorSettingsToMetadata() {
		String header = "i0Dark: " + i0DarkScan.getHeaderDescription() + "\n";
		header += "i0InitialScan: " + i0InitialScan.getHeaderDescription() + "\n";
		if (iRefScan != null && iRefPosition != null) {
			header += "iRefScan: " + iRefScan.getHeaderDescription() + "\n";
		}
		header += "itScan: " + itScan.getHeaderDescription() + "\n";

		NexusFileMetadata metadata = new NexusFileMetadata(theDetector.getName() + "_settings", header,
				EntryTypes.NXinstrument, NXinstrumentSubTypes.NXdetector, theDetector.getName() + "_settings");
		NexusExtraMetadataDataWriter.addMetadataEntry(metadata);
	}

	private String writeAsciiFile() throws Exception {
		writer = new EdeLinearExperimentAsciiFileWriter(i0DarkScan, i0InitialScan, iRefScan, itScan, i0FinalScan, theDetector);
		if (filenameTemplate != null && !filenameTemplate.isEmpty()) {
			writer.setFilenameTemplate(filenameTemplate);
		}
		logger.debug("EDE linear experiment writing its ascii derived data files...");
		writer.writeAsciiFile();
		log("EDE single spectrum experiment complete.");
		return writer.getAsciiItFilename();
	}

	private void pauseForToup() throws Exception {
		Double predictedExperimentTime = new LinearExperimentTimeEstimator(itScanParameters,  i0Position,
				itPosition,iRefPosition).getTotalDuration();
		TopupChecker topup = createTopupChecker(predictedExperimentTime);
		topup.atScanStart();
	}
}
