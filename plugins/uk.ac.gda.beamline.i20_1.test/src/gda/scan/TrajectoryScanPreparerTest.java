/*-
 * Copyright © 2018 Diamond Light Source Ltd.
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

import static org.junit.Assert.assertEquals;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.junit.Test;

import gda.device.trajectoryscancontroller.DummyTrajectoryScanController;
import gda.device.trajectoryscancontroller.TrajectoryScanController;

public class TrajectoryScanPreparerTest {

	private TrajectoryScanPreparer getTrajectoryScanPreparer() {
		TrajectoryScanPreparer trajScanPrep = new TrajectoryScanPreparer();
		TrajectoryScanController controller = new TrajectoryScanControllerForTest();
		trajScanPrep.setTrajectoryScanController(controller);
		return trajScanPrep;
	}

	private TurboXasParameters getTurboXasParameters() {
		TurboXasParameters parameters = new TurboXasParameters();
		parameters.setSampleName("sample name");
		parameters.setStartEnergy(0);
		parameters.setEndEnergy(10);
		parameters.setEnergyStep(0.01);
		return parameters;
	}

	@Test
	public void testAddSpectrumToTrajectory() {
		double delta = 0.1;
		double startPos = 0;
		double endPos = 1;

		TrajectoryScanPreparer trajScanPrep = getTrajectoryScanPreparer();
		trajScanPrep.addSpectrumToTrajectorySubdivide(startPos, endPos, delta, delta, 2, 2);
		Double[] times = trajScanPrep.getTrajectoryTimesList().toArray(new Double[0]);
		Double[] positions = trajScanPrep.getTrajectoryPositionsList().toArray(new Double[0]);

		assertEquals(4, times.length);
		assertEquals(4, positions.length, 8);
		Double[] expectedPositions = { startPos, endPos, endPos + delta, startPos - delta };
		for (int i = 0; i < positions.length; i++) {
			assertEquals(expectedPositions[i], positions[i], 1e-6);
		}
	}

	@Test
	public void testBuildsTrajectoryFromGroupsAndSendsProfile() throws InterruptedException, Exception {
		TurboXasParameters parameters = getTurboXasParameters();
		parameters.addTimingGroup(new TurboSlitTimingGroup("group1", 0.10, 0.5, 5));
		parameters.addTimingGroup(new TurboSlitTimingGroup("group2", 0.10, 0.5, 7));

		TrajectoryScanPreparer trajScanPrep = getTrajectoryScanPreparer();
		TrajectoryScanController controller = trajScanPrep.getTrajectoryScanController();

		// set max time per step in trajectory to large value, so that steps are not subdivided
		trajScanPrep.setMaxTimePerStep(10);
		trajScanPrep.setUseMaxTimePerStep(true);

		// Build trajectory profile point arrays
		trajScanPrep.addPointsForTimingGroups(parameters.getMotorParameters());

		int numSpectra = parameters.getTimingGroups().stream().mapToInt(TurboSlitTimingGroup::getNumSpectra).sum();
		int numTrajectoryPoints = numSpectra * 4 + 1; // 4 points per spectrum, plus move to initial position at the
														// start
		checkProfileNumPoints(trajScanPrep, numTrajectoryPoints);

		// Send trajectory scan values to epics, check arrays match expected size
		trajScanPrep.sendProfileValues();

		checkControllerNumPoints(trajScanPrep, numTrajectoryPoints);
	}

	@Test
	public void testBuildsTrajectoryFromGroupsTwoWay() throws Exception {
		TurboXasParameters parameters = getTurboXasParameters();
		parameters.addTimingGroup(new TurboSlitTimingGroup("group1", 1.0, 0.5, 5));
		parameters.addTimingGroup(new TurboSlitTimingGroup("group2", 2.0, 0.5, 7));

		TrajectoryScanPreparer trajScanPrep = getTrajectoryScanPreparer();
		trajScanPrep.setTwoWayScan(true);
		trajScanPrep.setUseFixedTurnaroundDistance(true);
		trajScanPrep.setTurnaroundDistance(1.0);

		trajScanPrep.addPointsForTimingGroups(parameters.getMotorParameters());
		int numSpectra = parameters.getTimingGroups().stream().mapToInt(TurboSlitTimingGroup::getNumSpectra).sum();
		int numTrajectoryPoints = numSpectra * 4 + 1; // 4 points per spectrum (including 1 for the wait at turnaround) + 1 extra from move to initial position

		checkProfileNumPoints(trajScanPrep, numTrajectoryPoints);

		// Send trajectory scan values to epics, check arrays match expected size
		trajScanPrep.sendProfileValues();

		checkControllerNumPoints(trajScanPrep, numTrajectoryPoints);
	}

	/**
	 * Check trajectory profile has expected number of points
	 * @param trajScanPrep
	 * @param expectedNumPoints
	 */
	private void checkProfileNumPoints(TrajectoryScanPreparer trajScanPrep, int expectedNumPoints) {
		assertEquals(expectedNumPoints, trajScanPrep.getTrajectoryTimesList().size());
		assertEquals(expectedNumPoints, trajScanPrep.getTrajectoryPositionsList().size());
		assertEquals(expectedNumPoints, trajScanPrep.getTrajectoryVelocityModesList().size());
	}
	/**
	 * Check the expected number of points have been set on the trajectory scan controller
	 * @param trajScanPrep
	 * @param expectedNumPoints
	 * @throws Exception
	 */
	private void checkControllerNumPoints(TrajectoryScanPreparer trajScanPrep, int expectedNumPoints) throws Exception {
		TrajectoryScanController controller = trajScanPrep.getTrajectoryScanController();
		assertEquals(expectedNumPoints, controller.getProfileNumPointsToBuild());
		assertEquals(expectedNumPoints, controller.getProfileTimeArray().length);
		assertEquals(expectedNumPoints, controller.getAxisPoints(0).length);
		assertEquals(expectedNumPoints, controller.getProfileVelocityModeArray().length);
		assertEquals(expectedNumPoints, controller.getProfileUserArray().length);
	}

	@Test
	public void testControllerAppendsBuildsProfile() throws InterruptedException, Exception {
		TurboXasParameters parameters = getTurboXasParameters();
		parameters.addTimingGroup(new TurboSlitTimingGroup("group1", 0.10, 0.5, 500));
		parameters.addTimingGroup(new TurboSlitTimingGroup("group2", 0.10, 0.5, 700));

		TrajectoryScanPreparer trajScanPrep = getTrajectoryScanPreparer();
		TrajectoryScanControllerForTest controller = (TrajectoryScanControllerForTest) trajScanPrep.getTrajectoryScanController();

		trajScanPrep.addPointsForTimingGroups(parameters.getMotorParameters());
		int numPoints = trajScanPrep.getTrajectoryTimesList().size();
		controller.setMaxPointsPerProfileBuild(1200);

		// Send profile by building and appending.
		int startIndex = 0;
		while (startIndex < numPoints) {
			startIndex = trajScanPrep.sendAppendProfileValues(startIndex);
			assertEquals(startIndex, controller.getBuiltProfile().size());
		}

		assertEquals(numPoints, controller.getBuiltProfile().size());
		for (int i = 0; i < numPoints; i++) {
			assertEquals("Problem with built profile point number " + i,
					trajScanPrep.getTrajectoryPositionsList().get(i), controller.getBuiltProfile().get(i), 1e-6);
		}
	}

	private class TrajectoryScanControllerForTest extends DummyTrajectoryScanController {

		private List<Double> builtProfile;

		// Build new profile from array of points
		@Override
		public void setBuildProfile() {
			builtProfile = new ArrayList<>();
			builtProfile.addAll(Arrays.asList(getAxisPoints(0)));
		}

		// Append array of points to profile
		@Override
		public void setAppendProfile() {
			builtProfile.addAll(Arrays.asList(getAxisPoints(0)));
		}

		public List<Double> getBuiltProfile() {
			return builtProfile;
		}
	}
}
