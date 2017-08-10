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

package gda.scan;
import static org.junit.Assert.assertEquals;

import org.dawnsci.ede.herebedragons.EdePositionType;
import org.junit.Test;

import gda.device.scannable.ScannableMotor;
import gda.scan.ede.position.ExplicitScanPositions;
import gda.scan.ede.timeestimators.LinearExperimentTimeEstimator;
import gda.scan.ede.timeestimators.SingleExperimentTimeEstimator;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

public class TimeEstimatorsTest {

	@Test
	public void testSingleExperimentEstimator() throws Exception {

		EdeScanParameters itParams = new EdeScanParameters();
		TimingGroup group2 = new TimingGroup();
		group2.setLabel("group1");
		group2.setNumberOfFrames(1);
		group2.setTimePerScan(0.05);
		group2.setTimePerFrame(0.02);
		itParams.addGroup(group2);

		ScannableMotor xScannable = EdeTestBase.createMotor("xScannable");
		ScannableMotor yScannable = EdeTestBase.createMotor("yScannable");

		ExplicitScanPositions inBeam = new ExplicitScanPositions(EdePositionType.INBEAM, 1d, 1d, xScannable, yScannable);
		ExplicitScanPositions outBeam = new ExplicitScanPositions(EdePositionType.OUTBEAM, 0d, 0d, xScannable,
				yScannable);

		SingleExperimentTimeEstimator est = new SingleExperimentTimeEstimator(itParams, outBeam, inBeam);

		Double tot = est.getTotalDuration();
		Double end = est.getAfterItDuration();
		Double it = est.getItDuration();

		assertEquals(6.08,tot,0.1);
		assertEquals(2.04,end,0.1);
		assertEquals(0.02,it,0.1);

	}

	@Test
	public void testLinearExperimentEstimator() throws Exception {

		EdeScanParameters itParams = new EdeScanParameters();
		TimingGroup group2 = new TimingGroup();
		group2.setLabel("group1");
		group2.setNumberOfFrames(1);
		group2.setTimePerScan(0.05);
		group2.setTimePerFrame(0.02);
		itParams.addGroup(group2);

		ScannableMotor xScannable = EdeTestBase.createMotor("xScannable");
		ScannableMotor yScannable = EdeTestBase.createMotor("yScannable");

		ExplicitScanPositions inBeam = new ExplicitScanPositions(EdePositionType.INBEAM, 1d, 1d, xScannable, yScannable);
		ExplicitScanPositions outBeam = new ExplicitScanPositions(EdePositionType.OUTBEAM, 0d, 0d, xScannable,
				yScannable);

		LinearExperimentTimeEstimator est = new LinearExperimentTimeEstimator(itParams, itParams, itParams, outBeam, inBeam, null);

		Double tot = est.getTotalDuration();
		Double before = est.getBeforeItDuration();
		Double end = est.getAfterItDuration();
		Double it = est.getItDuration();

		assertEquals(6.08,tot,0.1);
		assertEquals(2.04,end,0.1);
		assertEquals(0.02,it,0.1);

	}

	@Test
	public void testLinearExperimentEstimator_withIref() throws Exception {
		// FIXME Rewrite the test

		EdeScanParameters itParams = new EdeScanParameters();
		TimingGroup group2 = new TimingGroup();
		group2.setLabel("group1");
		group2.setNumberOfFrames(1);
		group2.setTimePerScan(0.05);
		group2.setTimePerFrame(0.02);
		itParams.addGroup(group2);

		ScannableMotor xScannable = EdeTestBase.createMotor("xScannable");
		ScannableMotor yScannable = EdeTestBase.createMotor("yScannable");

		ExplicitScanPositions inBeam = new ExplicitScanPositions(EdePositionType.INBEAM, 1d, 1d, xScannable, yScannable);
		ExplicitScanPositions outBeam = new ExplicitScanPositions(EdePositionType.OUTBEAM, 0d, 0d, xScannable,
				yScannable);
		ExplicitScanPositions irefPosition = new ExplicitScanPositions(EdePositionType.OUTBEAM, 0d, 0d, xScannable,
				yScannable);

		LinearExperimentTimeEstimator est = new LinearExperimentTimeEstimator(itParams, itParams, itParams, outBeam, inBeam, irefPosition);

		Double tot = est.getTotalDuration();
		Double end = est.getAfterItDuration();
		Double it = est.getItDuration();

		assertEquals(6.08,tot,0.1);
		assertEquals(2.04,end,0.1);
		assertEquals(0.02,it,0.1);

	}

	@Test
	public void testLinearExperimentEstimator_multipleGroups() throws Exception {

		EdeScanParameters itParams = new EdeScanParameters();
		TimingGroup group1 = new TimingGroup();
		group1.setLabel("group1");
		group1.setNumberOfFrames(10);
		group1.setTimePerScan(0.05);
		group1.setTimePerFrame(1);
		itParams.addGroup(group1);

		TimingGroup group2 = new TimingGroup();
		group2.setLabel("group2");
		group2.setNumberOfFrames(1);
		group2.setTimePerScan(0.02);
		group2.setTimePerFrame(0.02);
		itParams.addGroup(group2);


		ScannableMotor xScannable = EdeTestBase.createMotor("xScannable");
		ScannableMotor yScannable = EdeTestBase.createMotor("yScannable");

		ExplicitScanPositions inBeam = new ExplicitScanPositions(EdePositionType.INBEAM, 1d, 1d, xScannable, yScannable);
		ExplicitScanPositions outBeam = new ExplicitScanPositions(EdePositionType.OUTBEAM, 0d, 0d, xScannable,
				yScannable);
		ExplicitScanPositions irefPosition = new ExplicitScanPositions(EdePositionType.OUTBEAM, 0d, 0d, xScannable,
				yScannable);

		LinearExperimentTimeEstimator est = new LinearExperimentTimeEstimator(itParams, itParams, itParams, outBeam, inBeam, irefPosition);

		Double tot = est.getTotalDuration();
		Double end = est.getAfterItDuration();
		Double it = est.getItDuration();

		assertEquals(20.10,tot,0.1); //
		assertEquals(3.02,end,0.1); // 2 * (1+0.02) + 2
		assertEquals(10.02,it,0.1); // 10 + 0.02

	}

}
