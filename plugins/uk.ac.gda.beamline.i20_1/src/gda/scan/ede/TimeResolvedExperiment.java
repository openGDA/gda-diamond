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

import gda.device.DeviceException;
import gda.scan.EdeScan;
import gda.scan.ede.EdeExperimentProgressBean.ExperimentCollectionType;
import gda.scan.ede.datawriters.EdeExperimentDataWriter;
import gda.scan.ede.datawriters.EdeTimeResolvedExperimentDataWriter;
import gda.scan.ede.timeestimators.LinearExperimentTimeEstimator;

import java.util.List;
import java.util.Map;

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

	public static final int DEFALT_NO_OF_SEC_PER_SPECTRUM_TO_PUBLISH = 2;

	protected int numberOfRepetitions = 1;

	private int noOfSecPerSpectrumToPublish = DEFALT_NO_OF_SEC_PER_SPECTRUM_TO_PUBLISH;
	private int totalNumberOfspectra;
	private double totalTime;

	public TimeResolvedExperiment(double i0accumulationTime, List<TimingGroup> itTimingGroups,
			Map<String, Double> i0ScanableMotorPositions,
			Map<String, Double> iTScanableMotorPositions,
			String detectorName, String topupMonitorName, String beamShutterScannableName) throws DeviceException {
		super(itTimingGroups, i0ScanableMotorPositions, iTScanableMotorPositions, detectorName, topupMonitorName, beamShutterScannableName);
		setDefaultI0Parameters(i0accumulationTime);
		setupTimingGroups();
	}

	public TimeResolvedExperiment(double i0accumulationTime, int i0NoOfAccumulcation, List<TimingGroup> itTimingGroups,
			Map<String, Double> i0ScanableMotorPositions,
			Map<String, Double> iTScanableMotorPositions,
			String detectorName, String topupMonitorName, String beamShutterScannableName) throws DeviceException {
		this(i0accumulationTime,
				i0NoOfAccumulcation,
				EdeScanParameters.createEdeScanParameters(itTimingGroups),
				i0ScanableMotorPositions,
				iTScanableMotorPositions,
				detectorName,
				topupMonitorName,
				beamShutterScannableName);
	}

	public TimeResolvedExperiment(double i0accumulationTime, int i0NoOfAccumulcation, EdeScanParameters iTScanParameters,
			Map<String, Double> i0ScanableMotorPositions,
			Map<String, Double> iTScanableMotorPositions,
			String detectorName, String topupMonitorName, String beamShutterScannableName) throws DeviceException {
		super(iTScanParameters, i0ScanableMotorPositions, iTScanableMotorPositions, detectorName, topupMonitorName, beamShutterScannableName);
		setCommonI0Parameters(i0accumulationTime, i0NoOfAccumulcation);
		setupTimingGroups();
	}

	private void setupTimingGroups() {
		totalNumberOfspectra = 0;
		totalTime = 0.0;
		for (TimingGroup group : itScanParameters.getTimingGroups()) {
			totalNumberOfspectra += group.getNumberOfFrames();
			totalTime += (group.getTimePerFrame() * group.getNumberOfFrames()) + group.getPreceedingTimeDelay();
		}
	}

	@Override
	protected boolean shouldPublishItScanData(EdeScanProgressBean progress) {
		int current = 0;
		for (int i = 0; i < progress.getGroupNumOfThisSDP(); i++) {
			current += itScans[0].getScanParameters().getTimingGroups().get(i).getNumberOfFrames();
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



	public int getNoOfSecPerSpectrumToPublish() {
		return noOfSecPerSpectrumToPublish;
	}


	public void setNoOfSecPerSpectrumToPublish(int noOfSecPerSpectrumToPublish) {
		this.noOfSecPerSpectrumToPublish = noOfSecPerSpectrumToPublish;
	}

	@Override
	protected void addScans() {

		i0FinalScan = new EdeScan(i0ScanParameters, i0Position, EdeScanType.LIGHT, theDetector, firstRepetitionIndex, beamLightShutter);
		i0FinalScan.setProgressUpdater(this);
		scansForExperiment.add(i0FinalScan);

		if (runIRef) {
			iRefFinalScan = new EdeScan(iRefScanParameters, iRefPosition, EdeScanType.LIGHT, theDetector, firstRepetitionIndex, beamLightShutter);
			iRefFinalScan.setProgressUpdater(this);
			scansForExperiment.add(iRefFinalScan);
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
		if (runIRef){
			header.append("iRefFinalScan: " + iRefFinalScan.getHeaderDescription() + "\n");
		}
		return header.toString();
	}

	@Override
	protected double getPredictedExperimentTime() {
		return new LinearExperimentTimeEstimator(itScanParameters,  i0Position,
				itPosition, iRefPosition).getTotalDuration();
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
		return new EdeTimeResolvedExperimentDataWriter(i0DarkScan, i0LightScan, iRefScan, iRefDarkScan, itDarkScan, itScans, i0FinalScan, iRefFinalScan, theDetector, nexusFilename);
	}

	@Override
	protected boolean shouldRunItDark() {
		return true;  //TODO always true, so remove from the interface??
	}
}
