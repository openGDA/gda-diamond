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
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;

import gda.device.trajectoryscancontroller.EpicsTrajectoryScanController;
import gda.device.trajectoryscancontroller.TrajectoryScanController;
import gda.device.trajectoryscancontroller.TrajectoryScanController.Status;
import gda.factory.Findable;

/**
 * Epics controller for Trajectory scan.
 * Contains getters, setters for accessing PVs for time, position, velocity mode, user mode arrays, etc. needed
 * for setting up, building and executing a trajectory scan.
 * Trajectories can also be built up in memory by using the functions {@link #addPointsToTrajectory},
 * {@link #addSpectrumToTrajectory}, {@link #addPointsForTimingGroups} before sending to Epics using {@link #sendProfileValues}.
 * @since 12/1/2017
 */
public class TrajectoryScanPreparer implements Findable, InitializingBean {
	private static final Logger logger = LoggerFactory.getLogger(TrajectoryScanPreparer.class);
	private TrajectoryScanController trajScanController;

	private String name;

	/** Number of subdivision to use for spectrum part of trajectory scan */
	private int numStepsForSpectrumSweep = 10;

	/** Number of subdivision to use for return sweep part of trajectory scan */
	private int numStepsForReturnSweep = 2;

	/** Max time per step. Moves in trajectory that take longer than this will be subdivided */
	private double maxTimePerStep = 2.0;

	/** Whether to use maxTimePerStep for subdivisions; otherwise use numStepsForSpectrumSweep, numStepsForReturnSweep */
	private boolean useMaxTimePerStep = true;

	@Override
	public void setName(String name) {
		this.name = name;
	}

	@Override
	public String getName() {
		return name;
	}

	@Override
	public void afterPropertiesSet() throws Exception {
		if( name == null || name.isEmpty())
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
		int numTimingGroups = timingGroups.size();

		// Calculate motor parameters (positions and velocities) for first timing group only
		// (positions are same for each group, and times used to set trajectory scan come directly from timing group list)
		motorParameters.setMotorParametersForTimingGroup(0);
		double startDelta = motorParameters.getScanStartPosition()-motorParameters.getStartPosition();
		double endDelta = motorParameters.getEndPosition() - motorParameters.getScanEndPosition();

		trajScanController.clearTrajectoryLists();
		for(int i=0; i<numTimingGroups; i++) {
			TurboSlitTimingGroup timingGroup = timingGroups.get(i);

			addSpectrumToTrajectorySubdivide(motorParameters.getScanStartPosition(), motorParameters.getScanEndPosition(), startDelta, endDelta,
				timingGroup.getTimePerSpectrum(), timingGroup.getTimeBetweenSpectra(), timingGroup.getNumSpectra(), i == 0);

		}
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
	public void addSpectrumToTrajectorySubdivide(double userStart, double userEnd, double startDelta, double endDelta,
			double timeForSpectrum, double timeBetweenSpectra, int numRepetitions, boolean firstGroup) {

		int startIndex = 0;
		if (firstGroup) {
			// First spectrum of first group includes move to initial position
			addSpectrumToTrajectorySubdivide(userStart, userEnd, startDelta, endDelta, timeForSpectrum, timeBetweenSpectra, true);
			startIndex = 1;
		}

		for(int i=startIndex; i<numRepetitions; i++) {
			addSpectrumToTrajectorySubdivide(userStart, userEnd, startDelta, endDelta, timeForSpectrum, timeBetweenSpectra, false);
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
			double timeForSpectrum, double timeBetweenSpectra, boolean includeMoveToInitialPosition) {

		Double[] positions = {userStart-startDelta, userStart, userEnd, userEnd+endDelta};
		double vSweep = (userEnd - userStart)/timeForSpectrum;
		double timeToUserStart = (positions[1]-positions[0])/vSweep;
		double timeForEnd = (positions[3]-positions[2])/vSweep;
		double timeForReturn = timeBetweenSpectra - (timeToUserStart + timeForEnd);

		Double[] times= {timeForReturn, timeToUserStart, timeForSpectrum, timeForEnd};
		Integer[] velocityModes = {3, 1, 1, 1};

		// Move to initial position, use fixed time (should be slow enough to not cause trouble with the motor)
		if (includeMoveToInitialPosition) {
			addPointToTrajectory(positions[0], maxTimePerStep, velocityModes[0]);
		}

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
	 * Add linear profile to trajectory (velocity based).
	 * Trajectory runs from userStart-startDelta to userEnd+endDelta and is broken into 3 segments;
	 * times for each point are computed from velocities vSweep (for + direction move) and and vReturn
	 * for move (back) to first position.
	 * @param userStart
	 * @param userEnd
	 * @param startDelta
	 * @param endDelta
	 * @param vSweep
	 * @param vReturn
	 * @param numRepetitions
	 */
	public void addSpectrumToTrajectory(double userStart, double userEnd, double startDelta, double endDelta,
			double vSweep, double vReturn, int numRepetitions) {

		Double[] positions = {userStart-startDelta, userStart, userEnd, userEnd+endDelta};

		double timeToUserStart = (positions[1]-positions[0])/vSweep;
		double timeForSpectrum = (positions[2]-positions[1])/vSweep;
		double timeForEnd = (positions[3]-positions[2])/vSweep;
		double timeForReturn = (positions[3]-positions[0])/vReturn;

		Double[] times= {timeForReturn, timeToUserStart, timeForSpectrum, timeForEnd};
		Integer[] velocityModes = {3, 1, 1, 1};

		for(int i=0; i<numRepetitions; i++) {
			addPointsToTrajectory(positions, times, velocityModes);
		}
	}

	/**
	 * Add linear profile to trajectory (time based).
	 * Trajectory runs from userStart-startDelta to userEnd+endDelta and is broken into 3 segments;
	 * times for each point are calculated from timeForSpectrum, timeBetween parameters.
	 * @param userStart
	 * @param userEnd
	 * @param startDelta
	 * @param endDelta
	 * @param timeForSpectrum
	 * @param timeBetweenSpectra
	 * @param numRepetitions
	 */
	public void addSpectrumToTrajectoryTimes(double userStart, double userEnd, double startDelta, double endDelta,
			double timeForSpectrum, double timeBetweenSpectra,	int numRepetitions) {

		Double[] positions = {userStart-startDelta, userStart, userEnd, userEnd+endDelta};
		double vSweep = (userEnd - userStart)/timeForSpectrum;
		double timeToUserStart = (positions[1]-positions[0])/vSweep;
		double timeForEnd = (positions[3]-positions[2])/vSweep;
		double timeForReturn = timeBetweenSpectra - (timeToUserStart + timeForEnd);

		Double[] times= {timeForReturn, timeToUserStart, timeForSpectrum, timeForEnd};
		Integer[] velocityModes = {3, 1, 1, 1};
		for(int i=0; i<numRepetitions; i++) {
			addPointsToTrajectory(positions, times, velocityModes);
		}
	}

	/**
	 * Add position, time, velocity mode arrays to trajectory point list.
	 * @param positions
	 * @param times
	 * @param velocityMode
	 */
	public void addPointsToTrajectory(Double[] positions, Double[] times, Integer[] velocityMode) {
		trajScanController.addPointsToTrajectory(positions, times, velocityMode);
	}

	public void addPointToTrajectory(double position, double time, int velocityMode) {
		trajScanController.addPointToTrajectory(position, time, velocityMode);
	}

	/**
	 * Send currently stored trajectory scan list values to Epics.
	 * (i.e. convert from List to array and send to appropriate PV)
	 * @throws Exception
	 */
	public void sendProfileValues() throws Exception {
		trajScanController.sendProfileValues();
	}

	public List<Double> getTrajectoryPositionsList() {
		return trajScanController.getTrajectoryPositionsList();
	}

	public void setTrajectoryPositionList(List<Double> positionProfileValues) {
		trajScanController.setTrajectoryPositionList(positionProfileValues);
	}

	public List<Double> getTrajectoryTimesList() {
		return trajScanController.getTrajectoryTimesList();
	}

	public void setTrajectoryTimesList(List<Double> timeProfileValues) {
		trajScanController.setTrajectoryTimesList(timeProfileValues);
	}

	public List<Integer> getTrajectoryVelocityModesList() {
		return trajScanController.getTrajectoryVelocityModesList();
	}

	public void setTrajectoryVelocityModesList(List<Integer> velocityModeProfileValues) {
		trajScanController.setTrajectoryVelocityModesList(velocityModeProfileValues);
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

}
