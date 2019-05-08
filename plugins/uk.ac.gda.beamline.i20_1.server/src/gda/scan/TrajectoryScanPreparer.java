/*-
 * Copyright © 2017 Diamond Light Source Ltd.
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

package gda.scan;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;

import gda.device.trajectoryscancontroller.EpicsTrajectoryScanController;
import gda.device.trajectoryscancontroller.TrajectoryScanController;
import gda.device.trajectoryscancontroller.TrajectoryScanController.Status;
import gda.factory.FindableBase;

/**
 * Epics controller for Trajectory scan.
 * Contains getters, setters for accessing PVs for time, position, velocity mode, user mode arrays, etc. needed
 * for setting up, building and executing a trajectory scan.
 * Trajectories can also be built up in memory by using the functions {@link #addPointsToTrajectory},
 * {@link #addSpectrumToTrajectory}, {@link #addPointsForTimingGroups} before sending to Epics using {@link #sendProfileValues}.
 * @since 12/1/2017
 */
public class TrajectoryScanPreparer extends FindableBase implements InitializingBean {
	private static final Logger logger = LoggerFactory.getLogger(TrajectoryScanPreparer.class);
	private TrajectoryScanController trajScanController;


	/** Number of subdivision to use for spectrum part of trajectory scan */
	private int numStepsForSpectrumSweep = 10;

	/** Number of subdivision to use for return sweep part of trajectory scan */
	private int numStepsForReturnSweep = 2;

	/** Max time per step. Moves in trajectory that take longer than this will be subdivided */
	private double maxTimePerStep = 2.0;

	/** Whether to use maxTimePerStep for subdivisions; otherwise use numStepsForSpectrumSweep, numStepsForReturnSweep */
	private boolean useMaxTimePerStep = true;

	/** In memory trajectory parameters */
	private List<Double> trajectoryPositions = new ArrayList<>();

	private List<Double> trajectoryTimes = new ArrayList<>();

	private List<Integer> trajectoryVelocityModes = new ArrayList<>();

	private boolean twoWayScan = false;

	/** Rundown time at end of spectrum when doing two way scans */
	private double timeForRundown = 0.0025;

	@Override
	public void afterPropertiesSet() throws Exception {
		if( getName() == null || getName().isEmpty())
			throw new Exception("name is not set");
		if (trajScanController == null) {
			throw new Exception("TrejectoryScanController object is not set");
		}
	}

	//Time
	public void setProfileTimeArray(Double[] vals) throws IOException {
		// Check to make time values aren't too large (otherwise bad things happen and have to reboot IOC...)
		double maxAllowedTimeForPMac = Math.pow(2,  24);
		for(int i=0; i<vals.length; i++) {
			if (vals[i]>maxAllowedTimeForPMac) {
				throw new IOException("Time "+vals[i]+" for profile point "+i+" exceeds limit ("+maxAllowedTimeForPMac+")");
			}
		}
		trajScanController.setProfileTimeArray(vals);
	}

	// Build profile
	public void setBuildProfile() throws Exception {
		trajScanController.setBuildProfile();
	}
	public Status getBuildProfileStatus() throws Exception {
		return trajScanController.getBuildStatus();
	}

	// Append profile
	public void setAppendProfile() throws Exception {
		trajScanController.setAppendProfile();
	}
	public Status getAppendProfileStatus() throws Exception {
		return trajScanController.getAppendStatus();
	}

	// Execute profile
	public void setExecuteProfile() throws Exception {
		trajScanController.setExecuteProfile();
	}

	// Abort currently running profile
	public void setAbortProfile() throws Exception {
		trajScanController.setAbortProfile();
	}

	private static final String DEFAULT_PMAC_NAME="PMAC6CS3";
	private static final String DEFAULT_CS_AXIS = "10000X";
	private static final int DEFAULT_RESOLUTION=1;
	private static final int DEFAULT_OFFSET=0;

	private static final String DEFAULT_TIME_MODE="ARRAY";

	// 							axis names   = {"A", "B", "C", "U", "V", "W", "X", "Y", "Z"};
	private static final int[] AXIS_IN_USE   = { 0,   0,   0,   0,   0,   0,   1,   0,   0};

	public void setDefaults() throws Exception {
		if (trajScanController instanceof EpicsTrajectoryScanController){
			EpicsTrajectoryScanController epicsTrajScanController = (EpicsTrajectoryScanController) trajScanController;
			// Set in use status for each axis; for in use axes also set default resolution
			// and offset
			for (int i = 0; i < AXIS_IN_USE.length; i++) {
				epicsTrajScanController.setUseAxis(i, AXIS_IN_USE[i]>0);
				if (AXIS_IN_USE[i] > 0) {
					epicsTrajScanController.setOffsetForAxis(i, DEFAULT_OFFSET);
					epicsTrajScanController.setResolutionForAxis(i,  DEFAULT_RESOLUTION);
				}
			}
			// Select correct coordinate system
			epicsTrajScanController.setCoordinateSystem(DEFAULT_PMAC_NAME);
			epicsTrajScanController.setTimeMode(DEFAULT_TIME_MODE);

			// CSPort for motor 4
			epicsTrajScanController.setCSPort(3, DEFAULT_PMAC_NAME);
			epicsTrajScanController.setCSAssignment(3, DEFAULT_CS_AXIS);
		}
	}

	/**
	 * Setup trajectory scan points using timing groups from TurboXasParameters
	 * @param motorParameters
	 */
	public void addPointsForTimingGroups(TurboXasMotorParameters motorParameters) {
		List<TurboSlitTimingGroup> timingGroups = motorParameters.getScanParameters().getTimingGroups();

		// Calculate motor parameters (positions and velocities) for first timing group only
		// (positions are same for each group, and times used to set trajectory scan come directly from timing group list)
		motorParameters.setMotorParametersForTimingGroup(0);

		clearTrajectoryLists();
		if (twoWayScan) {
			List<TurnaroundParameters> turnParams = createTurnaroundParameters(motorParameters, timingGroups);
			addSpectraBiDirectional(motorParameters, timingGroups, turnParams);
		} else {
			addSpectraMonoDirectional(motorParameters, timingGroups);
		}
	}

	/**
	 * Calculate the runup/down distances and times for each spectrum in bi-directional scan.
	 * The rundown distance is adjusted to match the runup of next spectrum, to make sure
	 * end/start positions between timing groups match up.
	 * @param motorParams
	 * @return
	 */
	public List<TurnaroundParameters> createTurnaroundParameters(TurboXasMotorParameters motorParams, List<TurboSlitTimingGroup> timingGroups) {

		// Create a list of turnaround parameters for each spectrum in each timing group.
		List<TurnaroundParameters> turnaroundParams = new ArrayList<>();
		timingGroups.forEach( timingGroup -> {
			for(int i=0; i<timingGroup.getNumSpectra(); i++) {
				turnaroundParams.add(new TurnaroundParameters(motorParams, timingGroup));
			}
		});

		// Adjust rundown distances so they match runup distance of next spectrum
		// This is because final rundown distance of a group != runup distance of next group if time per spectrum is different
		for(int i=0; i<turnaroundParams.size()-1; i++) {
			double nextRunup = turnaroundParams.get(i+1).getRunupDistance();
			turnaroundParams.get(i).setRundownDistance(nextRunup);
			turnaroundParams.get(i).showParameters();
		}
		return turnaroundParams;
	}

	public void addSpectraBiDirectional(TurboXasMotorParameters motorParameters, List<TurboSlitTimingGroup> timingGroups, List<TurnaroundParameters> turnaroundParams) {

		double userStart = motorParameters.getScanStartPosition();
		double userEnd = motorParameters.getScanEndPosition();

		// Move to initial position, use fixed time (should be slow enough to not cause trouble with the motor)
		double sweepDirection = userStart < userEnd ? 1 : -1;
		addPointToTrajectory(userStart - sweepDirection * turnaroundParams.get(0).getRunupDistance(), maxTimePerStep, 3);

		int spectrumNumber = 0;
		for(TurboSlitTimingGroup timingGroup : timingGroups) {
			double timeForSpectrum = timingGroup.getTimePerSpectrum();
			int numRepetitions = timingGroup.getNumSpectra();

			// Add the spectra,
			for (int i = 0; i < numRepetitions; i++) {
				double startPos = userStart;
				double endPos = userEnd;
				// flip start and end positions on 'reverse' sweep.
				if (spectrumNumber % 2 == 1) {
					startPos = userEnd;
					endPos = userStart;
				}
				addSpectrumToTrajectoryRunupDown(startPos, endPos, timeForSpectrum, turnaroundParams.get(spectrumNumber));
				spectrumNumber++;
			}
		}
	}

	public void addSpectrumToTrajectoryRunupDown(double spectrumStart, double spectrumEnd, double timeForSpectrum, TurnaroundParameters turnparams) {

		double sweepDirection = spectrumStart < spectrumEnd ? 1 : -1;
		Double[] positions = {spectrumStart-sweepDirection*turnparams.getRunupDistance(), spectrumStart, spectrumEnd, spectrumEnd+sweepDirection*turnparams.getRundownDistance() };

		// Move to start of spectrum sweep
		addPointToTrajectory(positions[1], turnparams.getRunupTime(), 1);

		// Spectrum sweep (subdivide if necessary)
		int numStepsForSpectrum = numStepsForSpectrumSweep;
		if (useMaxTimePerStep && maxTimePerStep>0) {
			numStepsForSpectrum = (int) Math.ceil(timeForSpectrum / maxTimePerStep);
		}
		addSubdividedStep(positions[1], positions[2], timeForSpectrum, numStepsForSpectrum, 1);

		// Move to the turnaround position
		addPointToTrajectory(positions[3], turnparams.getRundownTime(), 3);
	}

	/**
	 * Adds several repetitions of same spectrum, using {@link #addSpectrumToTrajectorySubdivide(double, double, double, double, double, double, boolean)}.
	 * @param userStart
	 * @param userEnd
	 * @param startDelta
	 * @param endDelta
	 * @param timeForSpectrum
	 * @param timeBetweenSpectra
	 * @param numRepetitions
	 */
	public void addSpectraMonoDirectional(TurboXasMotorParameters motorParameters, List<TurboSlitTimingGroup> timingGroups) {

		double userStart = motorParameters.getScanStartPosition();
		double userEnd = motorParameters.getScanEndPosition();
		double startDelta = motorParameters.getScanStartPosition() - motorParameters.getStartPosition();
		double endDelta = motorParameters.getEndPosition() - motorParameters.getScanEndPosition();

		// Move to initial position, use fixed time (should be slow enough to not cause
		// trouble with the motor)
		double sweepDirection = userStart < userEnd ? 1 : -1;
		addPointToTrajectory(userStart - sweepDirection * startDelta, maxTimePerStep, 3);

		for(TurboSlitTimingGroup timingGroup : timingGroups) {
			double timeForSpectrum = timingGroup.getTimePerSpectrum();
			int numRepetitions = timingGroup.getNumSpectra();

			double timeBetweenSpectra = timingGroup.getTimeBetweenSpectra();

			// Add the spectra, include motor return back to start position
			for (int i = 0; i < numRepetitions; i++) {
				addSpectrumToTrajectorySubdivide(userStart, userEnd, startDelta, endDelta, timeForSpectrum, timeBetweenSpectra);
			}
		}
	}

	/**
	 * Same as {@link #addSpectrumToTrajectoryTimes(double, double, double, double, double, double, int)} except move corresponding
	 * to spectrum collection and move back to beginning are subdivided into number of steps ({@link #numStepsForSpectrumSweep},
	 * {@link #numStepsForReturnSweep} respectively).
	 * @param userStart
	 * @param userEnd
	 * @param startDelta
	 * @param endDelta
	 * @param timeForSpectrum
	 * @param timeBetweenSpectra
	 * @param includeMoveToInitialPosition include initial move to start of trajectory (set to true for first spectrum only,
	 * since move back to start is added at end of each spectrum sweep)
	 */
	public void addSpectrumToTrajectorySubdivide(double userStart, double userEnd, double startDelta, double endDelta,
			double timeForSpectrum, double timeBetweenSpectra) {

		Double[] positions = {userStart-startDelta, userStart, userEnd, userEnd+endDelta};
		double vSweep = (userEnd - userStart)/timeForSpectrum;
		double timeToUserStart = (positions[1]-positions[0])/vSweep;
		double timeForEnd = (positions[3]-positions[2])/vSweep;
		double timeForReturn = timeBetweenSpectra - (timeToUserStart + timeForEnd);

		Double[] times= {timeForReturn, timeToUserStart, timeForSpectrum, timeForEnd};
		Integer[] velocityModes = {3, 1, 1, 1};

		int numStepsForSpectrum = numStepsForSpectrumSweep;
		int numStepsForReturn = numStepsForReturnSweep;

//		// Set number of subdivisions according to max allowed time per step.
		if (useMaxTimePerStep && maxTimePerStep>0) {
			numStepsForSpectrum = (int) Math.ceil(timeForSpectrum / maxTimePerStep);
			numStepsForReturn = (int) Math.ceil(timeForReturn / maxTimePerStep);
		}

		// Move to start of spectrum sweep
		addPointToTrajectory(positions[1], times[1], velocityModes[1]);

		// Spectrum sweep (subdivide)
		addSubdividedStep(userStart, userEnd, timeForSpectrum, numStepsForSpectrum, velocityModes[2]);

		// move to final position
		addPointToTrajectory(positions[3], times[3], 3);

		// Return to start position
		addSubdividedStep(positions[3], positions[0], timeForReturn, numStepsForReturn, velocityModes[3]);

	}

	/**
	 * Add 'numSteps' positions between startPos and endPos to trajectory (constant speed), taking total of timeForMove seconds for whole move.'
	 * @param startPos start position
	 * @param endPos end position
	 * @param numSteps number of steps to add
	 * @param timeForMove total time to take for move
	 * @param velocityMode velocity mode to use
	 */
	public void addSubdividedStep(double startPos, double endPos, double timeForMove,  int numSteps, int velocityMode) {
		double posStep = (endPos-startPos)/numSteps;
		double timePerstep = timeForMove/numSteps;
		double pos = startPos;
		for(int i=0; i<numSteps; i++) {
			pos += posStep;
			addPointToTrajectory(pos, timePerstep, velocityMode);
		}
	}

	/**
	 * Add position, time, velocity mode arrays to trajectory point list.
	 * @param positions
	 * @param times
	 * @param velocityMode
	 */
	public void addPointsToTrajectory(Double[] positions, Double[] times, Integer[] velocityMode) {
		if (positions.length != times.length || positions.length != velocityMode.length) {
			throw new IllegalArgumentException("Trajectory parameter arrays have differing lengths");
		}
		trajectoryPositions.addAll(Arrays.asList(positions));
		trajectoryTimes.addAll(Arrays.asList(times));
		trajectoryVelocityModes.addAll(Arrays.asList(velocityMode));
	}

	public void addPointToTrajectory(double position, double time, int velocityMode) {
		trajectoryPositions.add(position);
		trajectoryTimes.add(time);
		trajectoryVelocityModes.add(velocityMode);
	}

	/**
	 * Send currently stored trajectory scan list values to Epics.
	 * (i.e. convert from List to array and send to appropriate PV)
	 * @throws Exception
	 */

	public void sendProfileValues() throws Exception {
		sendProfileValues(0, trajectoryTimes.size()-1);
	}

	/**
	 * Send trajectory profile to Epics, building and appending as many times as
	 * necessary to send all the points. See also {@link #sendAppendProfileValues(int)}.
	 * @throws Exception
	 */
	public void sendAppendProfileValues() throws Exception {
		int startPoint = 0;
		int numPoints = trajectoryTimes.size();

		while(startPoint < numPoints) {
			startPoint = sendAppendProfileValues(startPoint);
		}
	}

	/**
	 * Build/append profile in Epics; take range of values from trajectory scan list.
	 * Build if startPoint==0; otherwise Append. Use 'maxPointsPerProfileBuild' to set the
	 * number of profile points sent per build/append operation.
	 * @param startPoint index of first point in trajectory profile to send.
	 * @return index of next point to be sent to Epics
	 * @throws Exception
	 */
	public int sendAppendProfileValues(int startPoint) throws Exception {
		int maxPointIndex = trajectoryTimes.size()-1;
		int endPointIndex = Math.min(maxPointIndex, startPoint + trajScanController.getMaxPointsPerProfileBuild() - 1);
		logger.debug("Appending points {} ... {} to trajectory profile", startPoint, endPointIndex);
		sendProfileValues(startPoint, endPointIndex);
		if (startPoint == 0) {
			setBuildProfile();
			if (getBuildProfileStatus() == Status.FAILURE){
				throw new Exception("Failure when building trajectory scan profile - check Epics EDM screen");
			}
		} else {
			setAppendProfile();
			if (getAppendProfileStatus() == Status.FAILURE){
				throw new Exception("Failure when appending to trajectory scan profile - check Epics EDM screen");
			}
		}
		return endPointIndex+1;
	}

	/**
	 * Send values from currently stored trajectory scan list values to Epics.
	 * (i.e. convert from List to array and send to appropriate PV)
	 * @param startIndex index of first point in profile to send
	 * @param endIndex index of last point in profile to send
	 * @throws Exception
	 */
	private void sendProfileValues(int startIndex, int endIndex) throws Exception {
		int xAxisIndex = trajScanController.getAxisNames().indexOf("X");
		int start = Math.max(0, startIndex);
		start = Math.min(start, trajectoryTimes.size()-1);
		int end = Math.min(endIndex, trajectoryTimes.size()-1);
		int numPoints = end - start + 1;

		Integer[] userMode = new Integer[numPoints];
		Arrays.fill(userMode, 0);

		List<Double> convertedTimes = trajectoryTimes.stream()
				.map(t -> t * trajScanController.getTimeConversionFromSecondsToDeviceUnits())
				.collect(Collectors.toList());

		// check no time exceeds the maximum the device can handle
		final double maxTime = 1 << 24;
		if (trajectoryTimes.stream().anyMatch(t -> t >= maxTime)) {
			throw new Exception("Time array has values exceeding maximum allowed time of '" + maxTime + "'");
		}

		// Used to give type information to toArray method
		Double[] dblArray = new Double[0];
		Integer[] intArray = new Integer[0];

		trajScanController.setProfileNumPointsToBuild(numPoints);
		trajScanController.setProfileTimeArray(convertedTimes.subList(start, end+1).toArray(dblArray));
		trajScanController.setAxisPoints(xAxisIndex, trajectoryPositions.subList(start, end+1).toArray(dblArray));
		trajScanController.setProfileVelocityModeArray(trajectoryVelocityModes.subList(start, end+1).toArray(intArray) );
		trajScanController.setProfileUserArray(userMode);
	}

	public List<Double> getTrajectoryPositionsList() {
		return trajectoryPositions;
	}

	public void setTrajectoryPositionList(List<Double> positionProfileValues) {
		trajectoryPositions = positionProfileValues;
	}

	public List<Double> getTrajectoryTimesList() {
		return trajectoryTimes;
	}

	public void setTrajectoryTimesList(List<Double> timeProfileValues) {
		trajectoryTimes = timeProfileValues;
	}

	public List<Integer> getTrajectoryVelocityModesList() {
		return trajectoryVelocityModes;
	}

	public void setTrajectoryVelocityModesList(List<Integer> velocityModeProfileValues) {
		trajectoryVelocityModes = velocityModeProfileValues;
	}

	private void clearTrajectoryLists() {
		trajectoryPositions.clear();
		trajectoryTimes.clear();
		trajectoryVelocityModes.clear();
	}

	public int getNumStepsForReturnSweep() {
		return numStepsForReturnSweep;
	}

	public void setNumStepsForReturnSweep(int numStepsForReturnSweep) {
		this.numStepsForReturnSweep = numStepsForReturnSweep;
	}

	public int getNumStepsForSpectrumSweep() {
		return numStepsForSpectrumSweep;
	}

	public void setNumStepsForSpectrumSweep(int numStepsForSpectrumSweep) {
		this.numStepsForSpectrumSweep = numStepsForSpectrumSweep;
	}

	public double getMaxTimePerStep() {
		return maxTimePerStep;
	}

	public void setMaxTimePerStep(double maxTimePerStep) {
		this.maxTimePerStep = maxTimePerStep;
	}

	public boolean getUseMaxTimePerStep() {
		return useMaxTimePerStep;
	}

	public void setUseMaxTimePerStep(boolean useMaxTimePerStep) {
		this.useMaxTimePerStep = useMaxTimePerStep;
	}

	public TrajectoryScanController getTrajectoryScanController() {
		return trajScanController;
	}

	public void setTrajectoryScanController(TrajectoryScanController trajScanController) {
		this.trajScanController = trajScanController;
	}

	public boolean isTwoWayScan() {
		return twoWayScan;
	}

	public void setTwoWayScan(boolean twoWayScan) {
		this.twoWayScan = twoWayScan;
	}

	public double getTimeForRundown() {
		return timeForRundown;
	}

	public void setTimeForRundown(double minTimeForRundown) {
		this.timeForRundown = minTimeForRundown;
	}

	private class TurnaroundParameters {
		private double runupDistance;
		private double rundownDistance;
		private double runupTime;
		private double frameTime;
		private double spectrumVelocity;
		private double spectrumTime;
		private double rundownTime = timeForRundown;

		public TurnaroundParameters(TurboXasMotorParameters motorParameters, TurboSlitTimingGroup timingGroup) {
			calculateParameters(motorParameters, timingGroup);
		}

		/**
		 * Calculate the runup/down times and positions.
		 * Rundown time is fixed, runup distance and time are calculated based on time between spectra and spectrum velocity. i.e.
		 * <li> runupTime = timePerSpectrum - rundownTIme - frameTime;
		 * <li> runupDistance = spectrumVelocity * runupTime;
		 * @param motorParameters
		 * @param timingGroup
		 */
		public void calculateParameters(TurboXasMotorParameters motorParameters, TurboSlitTimingGroup timingGroup) {
			spectrumVelocity = Math.abs(motorParameters.getScanEndPosition() - motorParameters.getScanStartPosition()) / timingGroup.getTimePerSpectrum();
			frameTime = motorParameters.getPositionStepsize() / spectrumVelocity; // time take to travel across 1 zebra encoder pulse
			runupTime = timingGroup.getTimeBetweenSpectra() - timeForRundown - frameTime;
			runupDistance = spectrumVelocity * runupTime;
			rundownDistance = runupDistance;
		}

		public void showParameters() {
			logger.debug("Runup/down distances : {} , {} mm", runupDistance, runupDistance);
			logger.debug("Times  : frame {}, runup = {}, rundown = {} sec", frameTime, runupTime, rundownTime);
			logger.debug("Spectrum velocity : {} mm/sec", spectrumVelocity);
			logger.debug("Accels : runup = {}, rundown = {} mm/sec^2", spectrumVelocity / runupTime, spectrumVelocity / rundownTime);
		}

		public void setRundownDistance(double rundownDistance) {
			this.rundownDistance = rundownDistance;
		}

		public double getTimePerSpectrum() {
			return spectrumTime;
		}

		public double getRundownDistance() {
			return rundownDistance;
		}

		public double getRunupDistance() {
			return runupDistance;
		}

		public double getRunupTime() {
			return runupTime;
		}

		public double getRundownTime() {
			return rundownTime;
		}
	}
}
