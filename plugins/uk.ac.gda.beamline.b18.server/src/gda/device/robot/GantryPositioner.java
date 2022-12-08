/*-
 * Copyright © 2020 Diamond Light Source Ltd.
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

package gda.device.robot;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannableUtils;
import gda.factory.FactoryException;

public class GantryPositioner extends SamplePlateMoverBase  {

	private static final Logger logger = LoggerFactory.getLogger(GantryPositioner.class);

	/** Scannable controlling horizontal motion of the gantry */
	private Scannable horizScannable;

	/** Scannable controlling vertical position of gantry */
	private Scannable vertScannable;

	/** Scannable controlling orientation of the gripper */
	private Scannable gripperAngleScannable;

	public Scannable getGripperAngleScannable() {
		return gripperAngleScannable;
	}

	public void setGripperAngleScannable(Scannable gripperAngle) {
		this.gripperAngleScannable = gripperAngle;
	}

	/** Gripper used to hold sample plate */
	private Scannable gripperScannable;

	private Map<String, Double> platePositions = new HashMap<>();
	private String currentPlateName = "";

	private Map<GripperState, Object> gripperPositions;
	private GripperState currentGripperState;

	/** Type of individual motor move that can take place */
	public enum MotorMove {SAFE_HEIGHT, LOAD_HEIGHT, PLATE_POSITION, BEAM_POSITION, GRIPPER, GRIPPER_ROTATE}

	private MotorMove currentMotorMove;

	private double gripperBeamAngle;
	private double gripperLoadAngle;

	private double loadHeight;
	private double safeHeight;
	private double beamHorizontalPosition;

	private double moveTolerance = 1e-3;
	private boolean verifyMove = true;

	public GantryPositioner() {
		// Setup map from GripperState to corresponding position of the scannable.
		gripperPositions = new EnumMap<>(GripperState.class);
		gripperPositions.put(GripperState.OPEN, "Open");
		gripperPositions.put(GripperState.CLOSE, "Close");
	}

	private List<Scannable> scannablesForPosition = Collections.emptyList();

	@Override
	public void configure() throws FactoryException {
		checkForScannable(getHorizScannable(), "horizScannable");
		checkForScannable(getVertScannable(), "vertScannable");
		checkForScannable(getGripperScannable(), "gripperScannable");
		checkForScannable(getGripperAngleScannable(), "gripperAngleScannable");

		scannablesForPosition = Arrays.asList(horizScannable, vertScannable, gripperScannable, gripperAngleScannable);

		setOutputFormat(scannablesForPosition.stream().map(s -> s.getOutputFormat()[0]).toArray(String[]::new));
		setInputNames(scannablesForPosition.stream().map(Scannable::getName).toArray(String[]::new));
	}

	/**
	 * Check scannable is not null
	 * @param scannable
	 * @param scannableName
	 * @throws FactoryException if scannable is null (scannableName is included in the message)
	 */
	private void checkForScannable(Scannable scannable, String scannableName) throws FactoryException {
		if (scannable == null) {
			throw new FactoryException("Could not configure "+getName()+" : "+scannableName+" has not been set");
		}
	}

	public void setGripperPosition(GripperState state, Object gripperPosition) {
		this.gripperPositions.put(state, gripperPosition);
	}

	@Override
	public Object getPosition() throws DeviceException {
		List<Object> obj = new ArrayList<>();
		for(Scannable s: scannablesForPosition) {
			obj.add(s.getPosition());
		}
		return obj.toArray(new Object[] {});
	}

	@Override
	public void loadPlate(String c) throws DeviceException {
		logMessage("Preparing to load sample plate "+c+" ...");
		if (platePositions.get(c) == null) {
			logger.warn("No position found for sample plate {}", c);
			logMessage("No position found for sample plate "+c);
			return;
		}
		if (currentPlateName.equals(c)) {
			logMessage("Sample plate "+c+" is already held");
			return;
		}

		if (!currentPlateName.isEmpty()) {
			unloadPlate(); // unload any currently held sample plate
		}
		logMessage("Loading sample plate "+c);
		moveToHorizontalPositionForPlate(c);
		rotateGripper(gripperLoadAngle);
		openGripper();
		moveToLoadHeight();
		closeGripper();
		currentPlateName = c;
		logMessage("Finished loading plate "+currentPlateName);
		logStatus();
	}

	@Override
	public void unloadPlate() throws DeviceException {
		if (currentPlateName.isEmpty()) {
			logMessage("No sample plate currently held");
			return;
		}
		logMessage("Unloading currently held sample plate ("+currentPlateName+")");
		moveToHorizontalPositionForPlate(currentPlateName);
		rotateGripper(gripperLoadAngle);
		moveToLoadHeight();
		openGripper();
		logMessage("Finished unloading plate "+currentPlateName);
		currentPlateName = "";
		logStatus();
	}

	@Override
	public void moveToBeam() throws DeviceException {
		logMessage("Moving to beam position");
		moveToHorizontalPosition(beamHorizontalPosition, MotorMove.BEAM_POSITION);
		rotateGripper(gripperBeamAngle);
		logMessage("Finished moving to beam");
		logStatus();
	}

	/**
	 * Move to horizontal position for named plate, after first moving to the 'safe' height.
	 * @param plateName
	 * @throws DeviceException
	 */
	public void moveToHorizontalPositionForPlate(String plateName) throws DeviceException {
		if (platePositions.get(plateName) != null) {
			moveToHorizontalPosition(platePositions.get(plateName), MotorMove.PLATE_POSITION);
		} else {
			logger.warn("No position found for sample plate {}", plateName);
			logMessage("No position found for sample plate "+plateName);
		}
	}

	private void moveToHorizontalPosition(double horizPosition, MotorMove moveType) throws DeviceException {
		double currentPosition = (double) horizScannable.getPosition();
		if (Math.abs(horizPosition-currentPosition) > 1e-4) {
			moveToSafeHeight();
			moveScannable(horizScannable, horizPosition, moveType);
		}
	}

	/**
	 * Move to safe height, so that horizontal move can be made
	 * @throws DeviceException
	 */
	public void moveToSafeHeight() throws DeviceException {
		moveScannable(vertScannable, safeHeight, MotorMove.SAFE_HEIGHT);
	}

	/**
	 * Move to vertical position for loading/unloading a plate
	 * @throws DeviceException
	 */
	public void moveToLoadHeight() throws DeviceException {
		moveScannable(vertScannable, loadHeight, MotorMove.LOAD_HEIGHT);
	}

	public void rotateGripper(double angle) throws DeviceException {
		moveScannable(gripperAngleScannable, angle, MotorMove.GRIPPER_ROTATE);
	}

	public void openGripper() throws DeviceException {
		moveGripper(GripperState.OPEN);
	}

	public void closeGripper() throws DeviceException {
		moveGripper(GripperState.CLOSE);
	}

	/**
	 * Open/close the gripper.
	 * @param state GripperState (i.e. Open, Close)
	 * @throws DeviceException
	 */
	private void moveGripper(GripperState state) throws DeviceException {
		moveScannable(gripperScannable, gripperPositions.get(state), MotorMove.GRIPPER);
		currentGripperState = state;
	}

	/**
	 * Move a scannable synchronously and check final position is within tolerance of requested position
	 * @param scn
	 * @param position
	 * @throws DeviceException
	 */
	private void moveScannable(Scannable scn, Object demandPosition, MotorMove moveType) throws DeviceException {
		if (scn.getPosition().equals(demandPosition)) {
			logMessage(scn.getName()+" is already at requested position "+demandPosition+ " ("+moveType+")");
			return;
		}

		logMessage("Moving "+scn.getName()+" to "+demandPosition+ " ("+moveType+")");
		setMotorMove(moveType);
		scn.moveTo(demandPosition);
		if (verifyMove) {
			checkScannablePosition(scn, demandPosition);
		}
	}

	private void checkScannablePosition(Scannable scn, Object requiredPosition) throws DeviceException {
		logger.debug("Checking {} is at required position ({})", scn.getName(), requiredPosition);
		if (requiredPosition instanceof Double) {
			Double[] dblPositions = ScannableUtils.objectToArray(scn.getPosition());
			Double position = (Double) requiredPosition;
			if (dblPositions.length == 0 || Math.abs(dblPositions[0] - position) > moveTolerance) {
				throw new DeviceException("Position after moving "+scn.getName()+" to "+position+" is not within tolerance");
			}
		} else {
			if (!scn.getPosition().toString().equals(requiredPosition.toString())) {
				throw new DeviceException("Position after moving "+scn.getName()+" to "+requiredPosition+" is not correct. Expected "+requiredPosition+" but got "+scn.getPosition());
			}
		}
	}

	protected void logMessage(String message) {
		logger.info(message);
		printConsoleMessage(message);
	}

	protected void logStatus() throws DeviceException {
		String pos = ScannableUtils.getFormattedCurrentPosition(this);
		String plateName = currentPlateName.isEmpty() ? "None" : currentPlateName;
		logger.info("{} , currently held plate = {}", pos, plateName);
	}

	private void setMotorMove(MotorMove move) {
		currentMotorMove = move;
	}

	/**
	 * The last motor move that took place - one of the values in {@link MotorMove} enum.
	 * @return
	 */
	public MotorMove getMotorMove() {
		return currentMotorMove;
	}


	public GripperState getCurrentGripperState() {
		return currentGripperState;
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return super.isBusy() ||
				horizScannable.isBusy() || vertScannable.isBusy() || gripperScannable.isBusy() || gripperAngleScannable.isBusy();
	}

	public Scannable getHorizScannable() {
		return horizScannable;
	}

	public void setHorizScannable(Scannable horizScannable) {
		this.horizScannable = horizScannable;
	}

	public Scannable getVertScannable() {
		return vertScannable;
	}

	public void setVertScannable(Scannable vertScannable) {
		this.vertScannable = vertScannable;
	}

	public Scannable getGripperScannable() {
		return gripperScannable;
	}

	public void setGripperScannable(Scannable gripper) {
		this.gripperScannable = gripper;
	}

	/**
	 *
	 * @return Map of all known plate positions currently (key = plate name, value = horizontal position).
	 */
	public Map<String, Double> getPlatePositions() {
		return platePositions;
	}

	@Override
	public List<String> getPlateNames() {
		return platePositions.keySet().stream().collect(Collectors.toList());
	}

	public void setPlatePositions(Map<String, Object> samplePlatePositions) {
		this.platePositions = new HashMap<>();
		samplePlatePositions.forEach(this::setPlatePosition);
	}

	/**
	 * Set the position of a plate (i.e. horizontal position where plate is located)
	 * Create Double from passed position Object - to deal with Integers, Doubles passed from Jython
	 * and avoid class cast exceptions.
	 * @param plateName
	 * @param position
	 */
	public void setPlatePosition(String plateName, Object position) {
		platePositions.put(plateName, Double.valueOf(position.toString()));
	}

	/**
	 * Get position of named plate
	 * @param samplePlateName
	 * @return Position of sample plate, or null if plate is not known
	 */
	public Double getPlatePosition(String samplePlateName) {
		return platePositions.get(samplePlateName);
	}

	public double getLoadHeight() {
		return loadHeight;
	}

	public void setLoadHeight(double loadUnloadHeight) {
		this.loadHeight = loadUnloadHeight;
	}

	public double getSafeHeight() {
		return safeHeight;
	}

	public void setSafeHeight(double safeHeight) {
		this.safeHeight = safeHeight;
	}

	public double getBeamHorizontalPosition() {
		return beamHorizontalPosition;
	}

	public void setBeamHorizontalPosition(double beamPosition) {
		this.beamHorizontalPosition = beamPosition;
	}

	public double getGripperBeamAngle() {
		return gripperBeamAngle;
	}

	public void setGripperBeamAngle(double gripperBeamAngle) {
		this.gripperBeamAngle = gripperBeamAngle;
	}

	public double getGripperLoadAngle() {
		return gripperLoadAngle;
	}

	public void setGripperLoadAngle(double gripperLoadAngle) {
		this.gripperLoadAngle = gripperLoadAngle;
	}

	@Override
	public String getCurrentPlate() {
		return currentPlateName;
	}

	/**
	 * Set the name of the currently held sample plate.
	 * @param currentSamplePlate
	 */
	public void setCurrentPlate(String currentSamplePlate) {
		this.currentPlateName = currentSamplePlate;
	}

	public void setVerifyMove(boolean verifyMove) {
		this.verifyMove = verifyMove;
	}

	public boolean isVerifyMove() {
		return verifyMove;
	}

	public double getMoveTolerance() {
		return moveTolerance;
	}

	public void setMoveTolerance(double moveTolerance) {
		this.moveTolerance = moveTolerance;
	}
}
