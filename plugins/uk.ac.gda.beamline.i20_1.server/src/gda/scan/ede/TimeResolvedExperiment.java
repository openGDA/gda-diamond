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

import java.lang.reflect.Type;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;

import org.dawnsci.ede.EdeScanType;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

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
	private double timeBetweenRepetitions = 0;

	private double noOfSecPerSpectrumToPublish = DEFALT_NO_OF_SEC_PER_SPECTRUM_TO_PUBLISH;
	private double i0accumulationTime;
	private boolean writeAsciiData;

	public TimeResolvedExperiment(double i0accumulationTime, List<TimingGroup> itTimingGroups,
			Map<String, Double> i0ScanableMotorPositions, Map<String, Double> iTScanableMotorPositions,
			String detectorName, String topupMonitorName, String beamShutterScannableName) throws DeviceException {
		super(itTimingGroups, i0ScanableMotorPositions, iTScanableMotorPositions, detectorName, topupMonitorName,
				beamShutterScannableName);
		this.i0accumulationTime = i0accumulationTime;
		setDefaultI0Parameters(i0accumulationTime);
		writeAsciiData = true;
	}

	/**
	 * Set number of accumulations for I0
	 * @param numI0Accumulations
	 * @throws DeviceException
	 */
	public void setNumberI0Accumulations(int numI0Accumulations) throws DeviceException {
		List<TimingGroup> groups = i0ScanParameters.getGroups();
		if (groups!=null && !groups.isEmpty()) {
			double accumulationTime = groups.get(0).getTimePerScan();
			setCommonI0Parameters(accumulationTime, numI0Accumulations);
		}
	}

	/**
	 * Setup timing groups for It collection from list of groups (can be called after TimeREsolvedExperiment has been created)
	 * @param timingGroups
	 * @throws DeviceException
	 */
	public void setTimingGroups(List<TimingGroup> timingGroups) throws DeviceException {
		itScanParameters = new EdeScanParameters();
		itScanParameters.setTimingGroups(timingGroups);
		setDefaultI0Parameters(i0accumulationTime);
	}

	private static Gson gson = new Gson();
	public void setTimingGroups(String timingGroupsString) throws DeviceException {
		Type listOfObjects = new TypeToken<List<TimingGroup>>(){}.getType();
		List<TimingGroup> timingGroups = gson.fromJson(timingGroupsString, listOfObjects);
		setTimingGroups(timingGroups);
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

	@Override
	protected void addFinalScans() throws Exception {
		int repetitions = getRepetitions();

		if (shouldRunItDark()) {
			EdeScanParameters itDarkScanParameters = deriveItDarkParametersFromItParameters();
			itDarkScanParameters.setUseFrameTime(true);
			itDarkScan = makeEdeScan(itDarkScanParameters, itPosition, EdeScanType.DARK, firstRepetitionIndex,  null);
			itDarkScan.setProgressUpdater(this);
			scansBeforeIt.add(itDarkScan);
		} else {
			itDarkScan = i0DarkScan;
		}

		// Make Topup checker for I0 and It collection (time for It collection + motor move time from I0 to It position)
		TopupChecker topupChecker = null;
		if (getItWaitForTopup()) {
			topupChecker = createTopupChecker(2*scanDeadTime + getTimeRequiredForLightI0Collection() + getTimeToMoveFromI0ToIt() + getTimeRequiredForItCollection());
		}

		i0ScanParameters.setUseFrameTime(false);
		i0LightScan = makeEdeScan(i0ScanParameters, i0Position, EdeScanType.LIGHT, firstRepetitionIndex, topupChecker);
		i0LightScan.setProgressUpdater(this);
		scansBeforeIt.add(i0LightScan);

		if (runIRef) {
			i0ForiRefScanParameters.setUseFrameTime(false);
			i0ForiRefScan = makeEdeScan(i0ForiRefScanParameters, i0ForiRefPosition, EdeScanType.LIGHT, firstRepetitionIndex, null);
			scansBeforeIt.add(i0ForiRefScan);
			i0ForiRefScan.setProgressUpdater(this);

			iRefScanParameters.setUseFrameTime(false);
			iRefScan = makeEdeScan(iRefScanParameters, iRefPosition, EdeScanType.LIGHT, firstRepetitionIndex, null);
			scansBeforeIt.add(iRefScan);
			iRefScan.setProgressUpdater(this);
		}

		runItWithTriggerOptions=itScanParameters.getGroups().get(0).isGroupTrig();

		// Dont't include Topup check for It - I0 part of scan already includes time for It collection. imh 24/7/2017
		if (runItWithTriggerOptions) {
			itScans = new EdeScanWithTFGTrigger[repetitions];
			itScanParameters.setUseFrameTime(true);
			for(int repIndex = 0; repIndex < repetitions; repIndex++){
				itScans[repIndex] = makeEdeScan(itScanParameters, itTriggerOptions, itPosition, EdeScanType.LIGHT, theDetector, repIndex, null);
				itScans[repIndex].setProgressUpdater(this);
				scansForIt.add(itScans[repIndex]);
			}
		} else {
			itScans = new EdeScan[repetitions];
			itScanParameters.setUseFrameTime(true);
			for(int repIndex = 0; repIndex < repetitions; repIndex++){
				itScans[repIndex] = makeEdeScan(itScanParameters, itPosition, EdeScanType.LIGHT, repIndex, null);
				itScans[repIndex].setProgressUpdater(this);
				scansForIt.add(itScans[repIndex]);
			}
		}
		// Repetition properties
		if (repetitions > 1) {
			// Add the cycle number to plot label
			Stream.of(itScans).forEach(sc -> sc.setIncludeCyclePlotLabel(true));

			// Set the time between repetitions (for all but the last scan)
			for(int i=0; i<itScans.length-1; i++) {
				itScans[i].setWaitTimeAfterCollection(timeBetweenRepetitions);
			}
		}

		Stream.of(itScans).forEach(sc-> sc.setNoOfSecPerSpectrumToPublish(noOfSecPerSpectrumToPublish));

		// Make Topup checker for final I0 scan (I0 collection time + time for motor move from It to I0)
		topupChecker= null;
		if (getItWaitForTopup()) {
			topupChecker = createTopupChecker(scanDeadTime + getTimeToMoveFromI0ToIt() + getTimeRequiredForLightI0Collection());
		}

		i0ScanParameters.setUseFrameTime(false);
		i0FinalScan = makeEdeScan(i0ScanParameters, i0Position, EdeScanType.LIGHT, firstRepetitionIndex, topupChecker);
		i0FinalScan.setProgressUpdater(this);
		scansAfterIt.add(i0FinalScan);

		if (runIRef) {
			iRefScanParameters.setUseFrameTime(false);
			iRefFinalScan = makeEdeScan(iRefScanParameters, iRefPosition, EdeScanType.LIGHT, firstRepetitionIndex, null);
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

	@Override
	protected ExperimentCollectionType getCollectionType() {
		return ExperimentCollectionType.MULTI;
	}

	@Override
	protected int getRepetitions() {
		return numberOfRepetitions;
	}

	public void setRepetitions(int numberOfRepetitions) {
		this.numberOfRepetitions = numberOfRepetitions;
	}

	@Override
	protected EdeExperimentDataWriter createFileWritter() {
		EdeTimeResolvedExperimentDataWriter writer = new EdeTimeResolvedExperimentDataWriter(i0DarkScan, i0LightScan, iRefScan, iRefDarkScan, itDarkScan,
				itScans, i0FinalScan, iRefFinalScan, theDetector, nexusFilename);
		writer.setWriteAsciiData(writeAsciiData);
		writer.setExtraScannables(itScans[0].getScannablesToMonitorDuringScan());
		return writer;
	}

	@Override
	protected boolean shouldRunItDark() {
		return true; // TODO always true, so remove from the interface??
	}

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

	public boolean getWriteAsciiData() {
		return writeAsciiData;
	}

	public void setWriteAsciiData(boolean writeAsciiData) {
		this.writeAsciiData = writeAsciiData;
	}

	public double getTimeBetweenRepetitions() {
		return timeBetweenRepetitions;
	}

	public void setTimeBetweenRepetitions(double timeBetweenRepetitions) {
		this.timeBetweenRepetitions = timeBetweenRepetitions;
	}
}
