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
	private static final String PROFILE_EXECUTE_PROC = "ProfileExecute.PROC";
	private static final String PROFILE_APPEND_PROC = "ProfileAppend.PROC";


	private PV<Integer[]> userArrayPv;
	private PV<Integer[]> velocityModeArrayPv;
	private PV<Double[]> profileTimeArrayPv;
	private PV<Double[]> xPositionArrayPv;

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
		pvFactory.getPVInteger(PROFILE_BUILD_PROC).putWait(1);;
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

	/** Conversion factor from seconds to trajectory scan time units */
	private final int timeConversionFromSecondsToPmacUnits = 1000000;

	/** These Lists are used to store the trajectory scan points when building a profile */
	private List<Double> trajectoryPositions;
	private List<Double> trajectoryTimes;
	private List<Integer> trajectoryVelocityModes;

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

			addSpectrumToTrajectoryTimes( motorParameters.getScanStartPosition(), motorParameters.getScanEndPosition(), startDelta, endDelta,
					timingGroup.getTimePerSpectrum(), timingGroup.getTimeBetweenSpectra(), timingGroup.getNumSpectra());
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
		Integer[] intTime = new Integer[4];

		for(int i=0; i<times.length; i++){
			intTime[i] = (int) (times[i]*timeConversionFromSecondsToPmacUnits);
		}
		for(int i=0; i<numRepetitions; i++) {
			addPointsToTrajectory(positions, times, velocityModes);
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
			trajectoryPositions.add(positions[i]);
			trajectoryTimes.add(times[i]);
			trajectoryVelocityModes.add(velocityMode[i]);
		}
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
}
