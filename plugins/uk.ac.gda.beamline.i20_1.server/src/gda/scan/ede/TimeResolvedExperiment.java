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

import java.util.List;
import java.util.Map;

import gda.device.DeviceException;
import gda.device.scannable.TopupChecker;
import gda.scan.EdeScan;
import gda.scan.EdeScanWithTFGTrigger;
import gda.scan.ede.EdeExperimentProgressBean.ExperimentCollectionType;
import gda.scan.ede.datawriters.EdeExperimentDataWriter;
import gda.scan.ede.datawriters.EdeTimeResolvedExperimentDataWriter;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

/**
 * Similar to the {@link TimeResolvedExperiment} class except that a series of TimingGroups are run which will produce
 * multiple spectra. In other words the itScanParameters given to this class is not assumed to be a single timing group
 * producing a single spectrum.
 * <p>
 * The experiment is not repeated, so all the spectra will occur at a different point in time wrt the progress of a
 * chemical reaction or other state of the sample.
 */
public class TimeResolvedExperiment extends EdeExperiment {

	public static final double DEFALT_NO_OF_SEC_PER_SPECTRUM_TO_PUBLISH = 2.0d;

	protected int numberOfRepetitions = 1;

	private double noOfSecPerSpectrumToPublish = DEFALT_NO_OF_SEC_PER_SPECTRUM_TO_PUBLISH;
	private int totalNumberOfspectra;
	private double totalTime;

	public TimeResolvedExperiment(double i0accumulationTime, List<TimingGroup> itTimingGroups,
			Map<String, Double> i0ScanableMotorPositions, Map<String, Double> iTScanableMotorPositions,
			String detectorName, String topupMonitorName, String beamShutterScannableName, String itTriggerOptions) throws DeviceException {
		super(itTimingGroups, itTriggerOptions, i0ScanableMotorPositions, iTScanableMotorPositions, detectorName, topupMonitorName,
				beamShutterScannableName);
		setDefaultI0Parameters(i0accumulationTime);
		setupTimingGroups();
	}

	public TimeResolvedExperiment(double i0accumulationTime, int i0NoOfAccumulcation, List<TimingGroup> itTimingGroups,
			Map<String, Double> i0ScanableMotorPositions, Map<String, Double> iTScanableMotorPositions,
			String detectorName, String topupMonitorName, String beamShutterScannableName, String itTriggerOptions) throws DeviceException {
		this(i0accumulationTime, i0NoOfAccumulcation, EdeScanParameters.createEdeScanParameters(itTimingGroups),
				i0ScanableMotorPositions, iTScanableMotorPositions, detectorName, topupMonitorName,
				beamShutterScannableName,itTriggerOptions);
	}

	public TimeResolvedExperiment(double i0accumulationTime, int i0NoOfAccumulcation,
			EdeScanParameters iTScanParameters, Map<String, Double> i0ScanableMotorPositions,
			Map<String, Double> iTScanableMotorPositions, String detectorName, String topupMonitorName,
			String beamShutterScannableName, String itTriggerOptions) throws DeviceException {
		super(iTScanParameters, itTriggerOptions, i0ScanableMotorPositions, iTScanableMotorPositions, detectorName, topupMonitorName,
				beamShutterScannableName);
		setCommonI0Parameters(i0accumulationTime, i0NoOfAccumulcation);
		setupTimingGroups();
	}

	private void setupTimingGroups() {
		totalNumberOfspectra = itScanParameters.getTotalNumberOfFrames();
		totalTime = itScanParameters.getTotalTime();
	}

	@Override
	protected boolean shouldPublishItScanData(EdeScanProgressBean progress) {
		int current = 0;
		List<TimingGroup> groups = itScans[0].getScanParameters().getTimingGroups();
		for (int i = 0; i < progress.getGroupNumOfThisSDP(); i++) {
			current += groups.get(i).getNumberOfFrames();
		}
		current += progress.getFrameNumOfThisSDP() + 1; // + 1 because it is 0 index
		int avg = (int) (totalNumberOfspectra / (totalTime / noOfSecPerSpectrumToPublish));
		if (avg < 1) {
			avg = 1;
		}
		if (current % avg == 0 || current == totalNumberOfspectra || current == 1) {
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
		return ((EdeTimeResolvedExperimentDataWriter) writer).getAsciiI0Filename();
	}

	/**
	 * NPE if this is called before the scan has been run and the datawriter has been created
	 *
	 * @return the name of the I0 output file
	 */
	public String getIRefFilename() {
		return ((EdeTimeResolvedExperimentDataWriter) writer).getAsciiIRefFilename();
	}

	/**
	 * NPE if this is called before the scan has been run and the datawriter has been created
	 *
	 * @return the name of the It output file
	 */
	public String getItFilename() {
		return ((EdeTimeResolvedExperimentDataWriter) writer).getAsciiItFilename();
	}

	/**
	 * NPE if this is called before the scan has been run and the datawriter has been created
	 *
	 * @return the name of the It output file
	 */
	public String getItFinalFilename() {
		return ((EdeTimeResolvedExperimentDataWriter) writer).getAsciiItFinalFilename();
	}

	/**
	 * NPE if this is called before the scan has been run and the datawriter has been created
	 *
	 * @return the name of the It output file
	 */
	public String getItAveragedFilename() {
		return ((EdeTimeResolvedExperimentDataWriter) writer).getAsciiItAveragedFilename();
	}

	public double getNoOfSecPerSpectrumToPublish() {
		return noOfSecPerSpectrumToPublish;
	}

	public void setNoOfSecPerSpectrumToPublish(double noOfSecPerSpectrumToPublish) {
		this.noOfSecPerSpectrumToPublish = noOfSecPerSpectrumToPublish;
	}

	private TopupChecker createTopupCheckerForAfterItScans() {
		double predictedExperimentTime = getTimeRequiredForFinalScans();
		return createTopupChecker(predictedExperimentTime);
	}

	@Override
	protected void addFinalScans() throws Exception {
		int repetitions = getRepetitions();
		double timeToTopup = getNextTopupTime();

		if (shouldRunItDark()) {
			EdeScanParameters itDarkScanParameters = deriveItDarkParametersFromItParameters();
			itDarkScanParameters.setUseFrameTime(true);
			itDarkScan = makeEdeScan(itDarkScanParameters, itPosition, EdeScanType.DARK, theDetector, firstRepetitionIndex,  null);
			itDarkScan.setProgressUpdater(this);
			scansBeforeIt.add(itDarkScan);
		} else {
			itDarkScan = i0DarkScan;
		}

		i0ScanParameters.setUseFrameTime(false);
		i0LightScan = makeEdeScan(i0ScanParameters, i0Position, EdeScanType.LIGHT, theDetector, firstRepetitionIndex, null);
		i0LightScan.setProgressUpdater(this);
		scansBeforeIt.add(i0LightScan);

		if (runIRef) {
			i0ForiRefScanParameters.setUseFrameTime(false);
			i0ForiRefScan = makeEdeScan(i0ForiRefScanParameters, i0ForiRefPosition, EdeScanType.LIGHT, theDetector, firstRepetitionIndex, null);
			scansBeforeIt.add(i0ForiRefScan);
			i0ForiRefScan.setProgressUpdater(this);

			iRefScanParameters.setUseFrameTime(false);
			iRefScan = makeEdeScan(iRefScanParameters, iRefPosition, EdeScanType.LIGHT, theDetector, firstRepetitionIndex, null);
			scansBeforeIt.add(iRefScan);
			iRefScan.setProgressUpdater(this);
		}

		runItWithTriggerOptions=itScanParameters.getGroups().get(0).isGroupTrig();

		if (runItWithTriggerOptions) {
			itScans = new EdeScanWithTFGTrigger[repetitions];

			itScanParameters.setUseFrameTime(true);
			for(int repIndex = 0; repIndex < repetitions; repIndex++){
				// itScans[repIndex] = new EdeScanWithTFGTrigger(itScanParameters, itTriggerOptions, itPosition, EdeScanType.LIGHT, theDetector, repIndex, beamLightShutter, shouldWaitForTopup(repIndex, timeToTopup));
				itScans[repIndex] = new EdeScanWithTFGTrigger(itScanParameters, itTriggerOptions, itPosition, EdeScanType.LIGHT, theDetector, repIndex, beamLightShutter, getItWaitForTopup() && shouldItScanWaitForTopup(timeToTopup));
				itScans[repIndex].setProgressUpdater(this);
				scansForIt.add(itScans[repIndex]);
			}
		} else {
			itScans = new EdeScan[repetitions];
			itScanParameters.setUseFrameTime(true);
			for(int repIndex = 0; repIndex < repetitions; repIndex++){
				TopupChecker topupChecker = getItWaitForTopup() ? createTopupCheckerForItCollection(timeToTopup) : null;
				itScans[repIndex] = makeEdeScan(itScanParameters, itPosition, EdeScanType.LIGHT, theDetector, repIndex, topupChecker);
				itScans[repIndex].setProgressUpdater(this);
				scansForIt.add(itScans[repIndex]);
			}
		}

		i0ScanParameters.setUseFrameTime(false);
		i0FinalScan = makeEdeScan(i0ScanParameters, i0Position, EdeScanType.LIGHT, theDetector,
				firstRepetitionIndex, createTopupCheckerForAfterItScans());
		i0FinalScan.setProgressUpdater(this);
		scansAfterIt.add(i0FinalScan);

		if (runIRef) {
			iRefScanParameters.setUseFrameTime(false);
			iRefFinalScan = makeEdeScan(iRefScanParameters, iRefPosition, EdeScanType.LIGHT, theDetector,
					firstRepetitionIndex, null);
			iRefFinalScan.setProgressUpdater(this);
			scansAfterIt.add(iRefFinalScan);
		}
	}

	@Override
	protected String getHeaderText() {
		StringBuilder header = new StringBuilder();
		header.append("i0Dark: " + i0DarkScan.getHeaderDescription() + "\n");
		if (runIRef) {
			header.append("iRefDarkScan: " + iRefDarkScan.getHeaderDescription() + "\n");
		}
		header.append("itDark: " + itDarkScan.getHeaderDescription() + "\n");

		header.append("i0InitialScan: " + i0LightScan.getHeaderDescription() + "\n");
		if (runIRef) {
			header.append("iRefScan: " + iRefScan.getHeaderDescription() + "\n");
		}
		header.append("itScan: " + itScans[0].getHeaderDescription() + "\n");

		header.append("i0FinalScan: " + i0FinalScan.getHeaderDescription() + "\n");
		if (runIRef) {
			header.append("iRefFinalScan: " + iRefFinalScan.getHeaderDescription() + "\n");
		}
		return header.toString();
	}

	private Double getTimeRequiredForFinalScans() {
		//LinearExperimentTimeEstimator estimator = new LinearExperimentTimeEstimator(i0ScanParameters, itScanParameters, iRefScanParameters, i0Position, itPosition, iRefPosition);
		//return estimator.getBeforeItDuration();
		return getTimeRequiredAfterItCollection();
	}

	@Override
	protected ExperimentCollectionType getCollectionType() {
		return ExperimentCollectionType.MULTI;
	}

	@Override
	protected int getRepetitions() {
		return numberOfRepetitions;
	}

	@Override
	protected EdeExperimentDataWriter createFileWritter() {
		return new EdeTimeResolvedExperimentDataWriter(i0DarkScan, i0LightScan, iRefScan, iRefDarkScan, itDarkScan,
				itScans, i0FinalScan, iRefFinalScan, theDetector, nexusFilename);
	}

	@Override
	protected boolean shouldRunItDark() {
		return true; // TODO always true, so remove from the interface??
	}

	// These functions are now implemented in parent class (EdeExperiment)
	//	@Override
	//	protected double getTimeRequiredBeforeItCollection() {
	//		//Time to move from current motor position to I0 position
	//		double timeForI0Move = i0Position.getTimeToMove();
	//		//Time to move from I0 to It position
	//		double timeForItMove = ( (EdeScanMotorPositions) itPosition).getTimeToMove( (EdeScanMotorPositions)i0Position );
	//		return itTriggerOptions.getTimePerSpectrum()*6 + timeForI0Move + timeForItMove;
	//	}
	//
	//	@Override
	//	protected double getTimeRequiredForItCollection() {
	//		// itScanParameters.getTotalTime();
	//		double totalTime = itScanParameters.getTotalNumberOfFrames();
	//		return itTriggerOptions.getTotalTime() * numberOfRepetitions;
	//	}

	//	@Override
	//	protected double getTimeRequiredAfterItCollection() {
	//		// Time for move from It to I0 position
	//		double timeForI0Move = ( (EdeScanMotorPositions) i0Position).getTimeToMove( (EdeScanMotorPositions)itPosition );
	//
	//		return itTriggerOptions.getTimePerSpectrum()*2 + timeForI0Move;
	//	}

	private int getCyclesForTopup() {
		if (getTimeRequiredForItCollection() <= TOP_UP_TIME) {
			return numberOfRepetitions;
		}
		return (int) (TOP_UP_TIME / itTriggerOptions.getTotalTime());
	}


	protected boolean shouldItScanWaitForTopup(double timeToTopupInSec) {
		double timeRequired = getTimeRequiredForItCollection();
		if ( timeRequired < timeToTopupInSec || timeRequired < TOP_UP_TIME) {
			return false;
		}
		return true;
	}

	@Override
	protected boolean shouldWaitForTopup(int repIndex, double timeToTopupInSec) {
		double timeRequiredForFullExperiment = getTimeRequiredForFullExperiment();
		if (timeRequiredForFullExperiment < timeToTopupInSec || timeRequiredForFullExperiment < TOP_UP_TIME) {
			return false;
		}
		if (numberOfRepetitions == 1 || repIndex == 0 || (repIndex + 1) % getCyclesForTopup() == 0) {
			return true;
		}
		return false;
	}
}
