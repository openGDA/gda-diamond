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

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;

import gda.epics.CachedLazyPVFactory;
import gda.epics.LazyPVFactory;
import gda.epics.PV;
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

	private CachedLazyPVFactory pvFactory;

	private String name;
	private String pvBase;

	private static final String X_POSITION_ARRAY = "X:Positions";

	private static final String PROFILE_NUM_POINTS = "ProfileNumPoints";
	private static final String PROFILE_NUM_POINTS_RBV = "ProfileNumPoints_RBV";

	private static final String PROFILE_NUM_POINTS_TO_BUILD = "ProfilePointsToBuild";
	private static final String PROFILE_NUM_POINTS_TO_BUILD_RBV = "ProfilePointsToBuild_RBV";

	private static final String USER_ARRAY = "UserArray";
	private static final String VELOCITY_MODE_ARRAY = "VelocityMode";
	private static final String PROFILE_TIME_ARRAY = "ProfileTimeArray";

	private static final String PROFILE_BUILD_PROC = "ProfileBuild.PROC";
	private static final String PROFILE_BUILD_STATUS = "ProfileBuildStatus_RBV";

	private static final String PROFILE_EXECUTE_PROC = "ProfileExecute.PROC";
	private static final String PROFILE_EXECUTE_STATUS = "ProfileExecuteStatus_RBV";

	private static final String PROFILE_APPEND_PROC = "ProfileAppend.PROC";
	private static final String PROFILE_APPEND_STATUS = "ProfileAppendStatus_RBV";
	private static final String PROFILE_EXECUTE_STATE = "ProfileExecuteState_RBV";
	private static final String TSCAN_PERCENT = "TscanPercent_RBV";

	private PV<Integer[]> userArrayPv;
	private PV<Integer[]> velocityModeArrayPv;
	private PV<Double[]> profileTimeArrayPv;
	private PV<Double[]> xPositionArrayPv;

	/** Conversion factor from seconds to trajectory scan time units */
	private final int timeConversionFromSecondsToPmacUnits = 1000000;

	/** These Lists are used to store the trajectory scan points when building a profile */
	private List<Double> trajectoryPositions;
	private List<Double> trajectoryTimes;
	private List<Integer> trajectoryVelocityModes;

	/** Number of subdivision to use for spectrum part of trajectory scan */
	private int numStepsForSpectrumSweep = 10;

	/** Number of subdivision to use for return sweep part of trajectory scan */
	private int numStepsForReturnSweep = 2;

	@Override
	public void setName(String name) {
		this.name = name;
	}

	@Override
	public String getName() {
		return name;
	}

	public void setPvBase(String prefix) {
		this.pvBase = prefix;
	}

	public String getPvBase() {
		return this.pvBase;
	}

	@Override
	public void afterPropertiesSet() throws Exception {
		if( name == null || name.isEmpty())
			throw new Exception("name is not set");
		if (pvBase == null || pvBase.isEmpty())
			throw new Exception("pvBase is not set");
		if (pvFactory == null) {
			pvFactory = new CachedLazyPVFactory(pvBase);
		}
		userArrayPv = LazyPVFactory.newIntegerArrayPV(pvBase + USER_ARRAY);
		velocityModeArrayPv = LazyPVFactory.newIntegerArrayPV(pvBase + VELOCITY_MODE_ARRAY);
		profileTimeArrayPv = LazyPVFactory.newDoubleArrayPV(pvBase + PROFILE_TIME_ARRAY);
		xPositionArrayPv = LazyPVFactory.newDoubleArrayPV(pvBase + X_POSITION_ARRAY);
	}

	// Num profile points
	public int getProfileNumPointsRBV() throws Exception {
		return pvFactory.getIntegerPVValueCache(PROFILE_NUM_POINTS_RBV).get();
	}

	public int getProfileNumPoints() throws Exception {
		return pvFactory.getIntegerPVValueCache(PROFILE_NUM_POINTS).get();
	}
	public void setProfileNumPoints(int numPoints) throws Exception {
		pvFactory.getIntegerPVValueCache(PROFILE_NUM_POINTS).putWait(numPoints);
	}


	// Num profile points to build
	public int getProfileNumPointsToBuildRBV() throws Exception {
		return pvFactory.getIntegerPVValueCache(PROFILE_NUM_POINTS_TO_BUILD_RBV).get();
	}

	public int getProfileNumPointsToBuild() throws Exception {
		return pvFactory.getIntegerPVValueCache(PROFILE_NUM_POINTS_TO_BUILD).get();
	}
	public void setProfileNumPointsToBuild(int numPoints) throws Exception {
		pvFactory.getIntegerPVValueCache(PROFILE_NUM_POINTS_TO_BUILD).putWait(numPoints);
	}

	// User mode
	public void setProfileUserArray(Integer[] vals) throws IOException {
		userArrayPv.putWait(vals);
	}
	public Integer[] getProfileUserArray() throws IOException {
		return userArrayPv.get();
	}

	// Velocity mode
	public void setProfileVelocityModeArray(Integer[] vals) throws IOException {
		velocityModeArrayPv.putWait(vals);
	}
	public Integer[] getProfileVelocityModeArray() throws IOException {
		return velocityModeArrayPv.get();
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
		profileTimeArrayPv.putWait(vals);
	}
	public Double[] getProfileTimeArray() throws IOException {
		return profileTimeArrayPv.get();
	}

	// Position
	public void setProfileXPositionArray(Double[] vals) throws IOException {
		xPositionArrayPv.putWait(vals);
	}
	public Double[] getProfileXPositionArray() throws IOException {
		return xPositionArrayPv.get();
	}

	// Don't use value cache for these functions, since always want to send value when building, appending, executing profile.
	// Build profile
	public void setBuildProfile() throws Exception {
		pvFactory.getPVInteger(PROFILE_BUILD_PROC).putWait(1);
	}

	public String getBuildProfileStatus() throws Exception {
		return pvFactory.getPVString(PROFILE_BUILD_STATUS).get();
	}
	public String getExecuteProfileStatus() throws Exception {
		return pvFactory.getPVString(PROFILE_EXECUTE_STATUS).get();
	}

	public String getExecuteProfileState() throws Exception {
		return pvFactory.getPVString(PROFILE_EXECUTE_STATE).get();
	}

	public String getTscanPercent() throws Exception {
		return pvFactory.getPVString(TSCAN_PERCENT).get();
	}

	public String getAppendProfileStatus() throws Exception {
		return pvFactory.getPVString(PROFILE_APPEND_STATUS).get();
	}
	// Append profile
	public void setAppendProfile() throws Exception {
		pvFactory.getPVInteger(PROFILE_APPEND_PROC).putWait(1);
	}

	// Append profile
	public void setExecuteProfile() throws Exception {
		pvFactory.getPVInteger(PROFILE_EXECUTE_PROC).putWait(1);
	}

	private static final String PROFILE_CS_NAME = "ProfileCsName";
	private static final String DEFAULT_PMAC_NAME="PMAC6CS3";
	private static final String DEFAULT_CS_AXIS = "10000X";

	private static final String X_RESOLUTION = ":Resolution";
	private static final int DEFAULT_RESOLUTION=1;

	private static final String X_OFFSET=":Offset";
	private static final int DEFAULT_OFFSET=0;

	private static final String USE_AXIS_PV = ":UseAxis";
	private static final String PROFILE_TIME_MODE="ProfileTimeMode";
	private static final String DEFAULT_TIME_MODE="ARRAY";

	private static final String[] AXIS_NAMES = {"A", "B", "C", "U", "V", "W", "X", "Y", "Z"};
	private static final int[] AXIS_IN_USE   = { 0,   0,   0,   0,   0,   0,   1,   0,   0};

	public void setDefaults() throws Exception {
		// Set in use status for each axis; for in use axes also set default resolution and offset
		for(int i=0; i<AXIS_NAMES.length; i++) {
			String axisPvName = AXIS_NAMES[i]+USE_AXIS_PV;
			pvFactory.getIntegerPVValueCache(axisPvName).putWait(AXIS_IN_USE[i]);
			if (AXIS_IN_USE[i]>0) {
				String offsetPvName = AXIS_NAMES[i]+":Offset";
				String resolutionPvName = AXIS_NAMES[i]+":Resolution";
				pvFactory.getIntegerPVValueCache(offsetPvName).putWait(DEFAULT_OFFSET);
				pvFactory.getIntegerPVValueCache(resolutionPvName).putWait(DEFAULT_RESOLUTION);
			}
		}
		pvFactory.getPVString(PROFILE_CS_NAME).putWait(DEFAULT_PMAC_NAME);
		pvFactory.getPVString(PROFILE_TIME_MODE).putWait(DEFAULT_TIME_MODE);

		//CSPort for motor 4
		String csPortMotor4 = pvFactory.getPVString("M4:CsPort_RBV").get();
		String csAxisMotor4 = pvFactory.getPVString("M4:CsAxis_RBV").get();
		if (!csPortMotor4.equals(DEFAULT_PMAC_NAME)) {
			logger.warn("Motor 4 CS port name should be set to {}", DEFAULT_PMAC_NAME);
		}
		if (!csAxisMotor4.equals(DEFAULT_CS_AXIS)) {
			logger.warn("Motor 4 CS assignment should be set to {}", DEFAULT_CS_AXIS);
		}
	}

	private boolean includeTurnaround = false;

	public boolean getIncludeTurnaround() {
		return includeTurnaround;
	}

	public void setIncludeTurnaround(boolean includeTurnaround) {
		this.includeTurnaround = includeTurnaround;
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

		clearTrajectoryLists();
		for(int i=0; i<numTimingGroups; i++) {
			TurboSlitTimingGroup timingGroup = timingGroups.get(i);

			if (includeTurnaround) {
				addSpectrumToTrajectoryWithTurnarounds(motorParameters.getScanStartPosition(), motorParameters.getScanEndPosition(), startDelta, endDelta,
					timingGroup.getTimePerSpectrum(), timingGroup.getTimeBetweenSpectra(), timingGroup.getNumSpectra());
			} else {
				addSpectrumToTrajectorySubdivide(motorParameters.getScanStartPosition(), motorParameters.getScanEndPosition(), startDelta, endDelta,
						timingGroup.getTimePerSpectrum(), timingGroup.getTimeBetweenSpectra(), timingGroup.getNumSpectra());
			}

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
			double timeForSpectrum, double timeBetweenSpectra, int numRepetitions) {

		// First spectrum includes move to initial position
		addSpectrumToTrajectorySubdivide(userStart, userEnd, startDelta, endDelta, timeForSpectrum, timeBetweenSpectra, true);

		for(int i=1; i<numRepetitions; i++) {
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

		// Move to initial position
		if (includeMoveToInitialPosition) {
			addPointToTrajectory(positions[0], times[0], velocityModes[0]);
		}

		// Move to start of spectrum sweep
		addPointToTrajectory(positions[1], times[1], velocityModes[1]);

		// Spectrum sweep (subdivide)
		addSubdividedStep(userStart, userEnd, timeForSpectrum, numStepsForSpectrumSweep, velocityModes[2]);

		// move to final position
		addPointToTrajectory(positions[3], times[3], 3);

		// Return to start position
		addSubdividedStep(positions[3], positions[0], timeForReturn, numStepsForReturnSweep, velocityModes[3]);

	}

	public void addSpectrumToTrajectoryWithTurnarounds(double userStart, double userEnd, double startDelta, double endDelta,
			double timeForSpectrum, double timeBetweenSpectra, int numRepetitions) {

		// First spectrum includes move to initial position
		addSpectrumToTrajectoryWithTurnarounds(userStart, userEnd, startDelta, endDelta, timeForSpectrum, timeBetweenSpectra, true);

		for(int i=1; i<numRepetitions; i++) {
			addSpectrumToTrajectoryWithTurnarounds(userStart, userEnd, startDelta, endDelta, timeForSpectrum, timeBetweenSpectra, false);
		}
	}

	private int numStepsForTurnaround = 10; //should be an even number

	public void setNumStepsForTurnaround(int numStepsForTurnaround) {
		this.numStepsForTurnaround = numStepsForTurnaround;
	}

	public int getNumStepsForTurnaround() {
		return this.numStepsForTurnaround;
	}

	public void addSpectrumToTrajectoryWithTurnarounds(double userStart, double userEnd, double startDelta, double endDelta,
			double timeForSpectrum, double timeBetweenSpectra, boolean includeMoveToInitialPosition) {
		Double[] positions = {userStart-startDelta, userStart, userEnd, userEnd+endDelta};
		double vSweep = (userEnd - userStart)/timeForSpectrum;
		double timeForTurnaroundAtEnd = endDelta/vSweep;
		double timeForTurnaroundAtStart = startDelta/vSweep;
		double timeForStartDelta = startDelta/vSweep;

		double timeForReturn = timeBetweenSpectra - (timeForTurnaroundAtEnd+timeForTurnaroundAtStart+timeForStartDelta);
		double vReturnApprox = vSweep*timeForSpectrum/timeForReturn; // approx return velocity

//		Double[] times= {timeForReturn, timeForTurnaroundAtStart, timeForSpectrum, timeForTurnaroundAtEnd};
		Integer[] velocityModes = {3, 1, 1, 1};

		// Move to initial position for start of ramp up
		// (use timeForReturn for 'move to' time to avoid trying to move too fast and getting 'motor following' error )
		if (includeMoveToInitialPosition) {
			addPointToTrajectory(positions[0], timeForReturn, velocityModes[0]);

			// Move to first point of spectrum sweep
			addPointToTrajectory(positions[1], timeForTurnaroundAtStart, velocityModes[1]);
		}

		// Spectrum sweep (subdivide)
		List<TrajectoryPoint> spectrumSweepPoints = getSubdividedStep(positions[1], positions[2], timeForSpectrum, numStepsForSpectrumSweep, velocityModes[2]);
		addPointsToTrajectory(spectrumSweepPoints);

		// Turnaround at spectrum end:
		List<TrajectoryPoint> pointsForEndTurnaround = getVelocityChange(positions[2], vSweep, 0, timeForTurnaroundAtEnd, numStepsForTurnaround/2, 1);
		addPointsToTrajectory(pointsForEndTurnaround);
		double turnaroundPos = pointsForEndTurnaround.get(pointsForEndTurnaround.size()-1).getPosition();
		pointsForEndTurnaround = getVelocityChange(turnaroundPos, 0, -vReturnApprox, timeForTurnaroundAtEnd/2, numStepsForTurnaround/2, 1);
		addPointsToTrajectory(pointsForEndTurnaround);

		// Calc. points for turnaround at spectrum start
		List<TrajectoryPoint> pointsForStartTurnaround = getVelocityChange(positions[0], -vReturnApprox, vSweep, timeForTurnaroundAtStart, numStepsForTurnaround, 1);

		// adjust start turnaround positions so that final point is at position[1]
		double finalPos = pointsForStartTurnaround.get(pointsForStartTurnaround.size()-1).getPosition();
		double offset = positions[0] - finalPos;
		for(TrajectoryPoint point : pointsForStartTurnaround) {
			double newpos = point.getPosition() + offset;
			point.setPosition(newpos);
		}

		double lastPointOfTurnaroundAtEnd = pointsForEndTurnaround.get(pointsForEndTurnaround.size()-1).getPosition();
		double firstPosOfTurnaroundAtStart = pointsForStartTurnaround.get(0).getPosition();

		// Return sweep (subdivided) between the two turnarounds
		List<TrajectoryPoint> returnSweepPoints = getSubdividedStep(lastPointOfTurnaroundAtEnd, firstPosOfTurnaroundAtStart, timeForReturn, numStepsForReturnSweep, velocityModes[3]);
		addPointsToTrajectory(returnSweepPoints);

		// Turnaround at start
		pointsForStartTurnaround.remove(0);// remove first point (this is last point of return sweep)
		addPointsToTrajectory(pointsForStartTurnaround);

		List<TrajectoryPoint> points = getSubdividedStep(positions[0], positions[1], timeForStartDelta, 5, velocityModes[3]);
		addPointsToTrajectory(points);
	}

	public void addPointsToTrajectory(List<TrajectoryPoint> points) {
		for(TrajectoryPoint point : points) {
			addPointToTrajectory(point.getPosition(), point.getTime(), point.getVelocityMode());
		}
	}

	public void addSpectrumToTrajectoryWithVelocityRamp(double userStart, double userEnd, double startDelta, double endDelta,
			double timeForSpectrum, double timeBetweenSpectra, boolean includeMoveToInitialPosition) {

		Double[] positions = {userStart-startDelta, userStart, userEnd, userEnd+endDelta};
		double vSweep = (userEnd - userStart)/timeForSpectrum;
		double timeToUserStart = (positions[1]-positions[0])/vSweep;
		double timeForEnd = (positions[3]-positions[2])/vSweep;
		double timeForReturn = timeBetweenSpectra - (2*timeToUserStart + timeForEnd);
		double vReturnApprox = vSweep*timeForSpectrum/timeForReturn; // approx return velocity

		Double[] times= {timeForReturn, timeToUserStart, timeForSpectrum, timeForEnd};
		Integer[] velocityModes = {3, 1, 1, 1};

		// Move to initial position for start of ramp up
		if (includeMoveToInitialPosition) {
			addPointToTrajectory(positions[0], 0, velocityModes[0]);
			// accel from stationary to required speed
			double endPosAfterRampUp = addVelocityChange(positions[0], 0, vSweep, timeToUserStart*0.5, 10, velocityModes[1]);
		}


		// Move to start of spectrum sweep
		addPointToTrajectory(positions[1], timeToUserStart*0.5, velocityModes[1]);

		// Spectrum sweep (subdivide)
		addSubdividedStep(positions[1], positions[2], timeForSpectrum, numStepsForSpectrumSweep, velocityModes[2]);

		// move to final position (velocity ramp down as well)
		double endPosAfterTurnaround = addVelocityChange(positions[2], vSweep, -vReturnApprox, timeForEnd, 10, velocityModes[2]);

		// Return to start position
		addSubdividedStep(endPosAfterTurnaround, positions[1], timeForReturn, numStepsForReturnSweep, velocityModes[3]);

		// move to final position (velocity ramp down as well)
		double endPosAfterTurnaroundAtStart = addVelocityChange(positions[1], -vReturnApprox, vSweep, timeToUserStart*0.9, 10, velocityModes[2]);

		// start position for ramp at beginning of next spectrum
		addPointToTrajectory(positions[0], timeToUserStart*0.1, velocityModes[0]);
	}

	List<TrajectoryPoint> getSubdividedStep(double startPos, double endPos, double timeForMove,  int numSteps, int velocityMode) {
		List<TrajectoryPoint> points = new ArrayList<TrajectoryPoint>();
		double posStep = (endPos-startPos)/numSteps;
		double timePerstep = timeForMove/numSteps;
		double pos = startPos;
		for(int i=0; i<numSteps; i++) {
			pos += posStep;
			points.add(new TrajectoryPoint(pos, timePerstep, velocityMode));
		}
		return points;
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

	class TrajectoryPoint {

		private double position;
		private double time;
		private int velocityMode;

		public TrajectoryPoint(double position, double time, int velocityMode) {
			this.position = position;
			this.time = time;
			this.velocityMode = velocityMode;
		}
		public double getPosition() {
			return position;
		}
		public void setPosition(double position) {
			this.position = position;
		}
		public double getTime() {
			return time;
		}
		public void setTime(double time) {
			this.time = time;
		}
		public int getVelocityMode() {
			return velocityMode;
		}
		public void setVelocityMode(int velocityMode) {
			this.velocityMode = velocityMode;
		}
	}

	public List<TrajectoryPoint> getVelocityChange(double startPos, double startVelocity, double endVelocity, double timeForMove, int numSteps, int velocityMode) {
		List<TrajectoryPoint> points = new ArrayList<TrajectoryPoint>();
		double accel = (endVelocity-startVelocity)/timeForMove;
		double deltaTime = timeForMove/numSteps;
		double pos = 0;
		for(int i=1; i<numSteps+1; i++) {
			double time = i*deltaTime;
			pos = startPos + startVelocity*time + 0.5*accel*time*time;
			points.add(new TrajectoryPoint(pos, deltaTime, velocityMode));
		}
		return points;
	}

	/**
	 *
	 * @param startPos
	 * @param startVelocity
	 * @param endVelocity
	 * @param timeForMove
	 * @param numSteps
	 * @param velocityMode
	 * @return Final position
	 */
	public double addVelocityChange(double startPos, double startVelocity, double endVelocity, double timeForMove, int numSteps, int velocityMode) {
		double accel = (endVelocity-startVelocity)/timeForMove;
		double deltaTime = timeForMove/numSteps;
		double pos = 0;
		for(int i=1; i<numSteps+1; i++) {
			double time = i*deltaTime;
			pos = startPos + startVelocity*time + 0.5*accel*time*time;
			addPointToTrajectory(pos, deltaTime, velocityMode);
		}
		return pos;
	}

	public double addTurnaround(double startPos, double startVelocity, double timeForMove, int numPoints) {
		double accel = -startVelocity/timeForMove;
		double deltaTime = timeForMove/numPoints;
		for(int i=1; i<numPoints+1; i++) {
			double time = i*deltaTime;
			double pos = startPos + startVelocity*time + accel*time*time;
			addPointToTrajectory(pos, deltaTime, 1);
		}
		return 0;
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
			double  vSweep, double vReturn,	int numRepetitions) {

		Double[] positions = {userStart-startDelta, userStart, userEnd, userEnd+endDelta};

		double timeToUserStart = (positions[1]-positions[0])/vSweep;
		double timeForSpectrum = (positions[2]-positions[1])/vSweep;
		double timeForEnd = (positions[3]-positions[2])/vSweep;
		double timeForReturn = (positions[3]-positions[0])/vReturn;

		Double[] times= {timeForReturn, timeToUserStart, timeForSpectrum, timeForEnd};
		Integer[] velocityModes = {3, 1, 1, 1};
		Integer[] intTime = new Integer[4];

		for(int i=0; i<times.length; i++){
			intTime[i] = (int) (times[i]*timeConversionFromSecondsToPmacUnits);
		}
		for(int i=0; i<numRepetitions; i++) {
			addPointsToTrajectory(positions, times, velocityModes);
		}
	}

	public void createTrajectoryLists() {
		trajectoryPositions = new ArrayList<Double>();
		trajectoryTimes = new ArrayList<Double>();
		trajectoryVelocityModes = new ArrayList<Integer>();
	}

	public void clearTrajectoryLists() {
		if (trajectoryPositions==null || trajectoryTimes==null || trajectoryVelocityModes==null) {
			createTrajectoryLists();
		}
		trajectoryPositions.clear();
		trajectoryTimes.clear();
		trajectoryVelocityModes.clear();
	}

	/**
	 * Add position, time, velocity mode arrays to trajectory point list.
	 * @param positions
	 * @param times
	 * @param velocityMode
	 */
	public void addPointsToTrajectory(Double[] positions, Double[] times, Integer[] velocityMode) {
		if (trajectoryPositions==null || trajectoryTimes==null || trajectoryVelocityModes==null) {
			createTrajectoryLists();
		}

		if (positions.length != times.length || positions.length != velocityMode.length) {
			logger.warn("Trajectory point arrays to add have different lengths!");
			return;
		}

		for(int i=0; i<positions.length; i++) {
			addPointToTrajectory(positions[i], times[i], velocityMode[i]);
		}
	}

	public void addPointToTrajectory(double position, double time, int velocityMode) {
		if (trajectoryPositions==null || trajectoryTimes==null || trajectoryVelocityModes==null) {
			createTrajectoryLists();
		}
		trajectoryPositions.add(position);
		trajectoryTimes.add(time);
		trajectoryVelocityModes.add(velocityMode);
	}

	/**
	 * Return trajectory point time values converted to PMac time units
	 * @return list of converted time values
	 */
	public List<Double> getTrajectoryConvertTimes() {
		List<Double> convertedTime = new ArrayList<Double>();
		for(int i=0; i<trajectoryTimes.size(); i++) {
			convertedTime.add(trajectoryTimes.get(i)*timeConversionFromSecondsToPmacUnits);
		}
		return convertedTime;
	}

	/**
	 * Send currently stored trajectory scan list values to Epics.
	 * (i.e. convert from List to array and send to appropriate PV)
	 * @throws Exception
	 */
	public void sendProfileValues() throws Exception {
		int numPointsInProfile = trajectoryTimes.size();
		Integer[] userMode = new Integer[numPointsInProfile];
		Arrays.fill(userMode, 0);

		// Get times in converted time units
		List<Double> convertedTime = getTrajectoryConvertTimes();
		// Check to make sure converted time isn't too large (otherwise bad things happen and have to reboot IOC...)
		double maxAllowedTimeForPMac = Math.pow(2,  24);
		for(int i=0; i<convertedTime.size(); i++) {
			if (convertedTime.get(i)>maxAllowedTimeForPMac) {
				throw new Exception("Time "+convertedTime.get(i)+" for profile point "+i+" exceeds limit ("+maxAllowedTimeForPMac+")");
			}
		}
		// These are used for class types by toArray function.
		Double []dblArray = new Double[0];
		Integer []intArray = new Integer[0];

		// Apply to Epics
		setProfileNumPointsToBuild(numPointsInProfile);
		setProfileTimeArray(convertedTime.toArray(dblArray));
		setProfileXPositionArray(trajectoryPositions.toArray(dblArray));
		setProfileVelocityModeArray(trajectoryVelocityModes.toArray(intArray) );
		setProfileUserArray(userMode);
	}

	public List<Double> getTrajectoryPositionsList() {
		return trajectoryPositions;
	}

	public void setTrajectoryPositionList(List<Double> positionProfileValues) {
		this.trajectoryPositions = positionProfileValues;
	}

	public List<Double> getTrajectoryTimesList() {
		return trajectoryTimes;
	}

	public void setTrajectoryTimesList(List<Double> timeProfileValues) {
		this.trajectoryTimes = timeProfileValues;
	}

	public List<Integer> getTrajectoryVelocityModesList() {
		return trajectoryVelocityModes;
	}

	public void setTrajectoryVelocityModesList(List<Integer> velocityModeProfileValues) {
		this.trajectoryVelocityModes = velocityModeProfileValues;
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
}
