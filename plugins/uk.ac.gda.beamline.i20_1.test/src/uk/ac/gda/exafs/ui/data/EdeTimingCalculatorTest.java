/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.ui.data;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import org.eclipse.january.dataset.DoubleDataset;
import org.junit.Test;

public class EdeTimingCalculatorTest {

	@Test
	public void testEdeTimingCalculator() {

		// create timing groups
		TimingGroup group1 = new TimingGroup();
		group1.setDelayBetweenFrames(1);
		group1.setTimePerScan(0.1);
		group1.setTimePerFrame(10);
		group1.setNumberOfFrames(5);
		group1.setOutLemo3(true);

		TimingGroup group2 = new TimingGroup();
		group2.setDelayBetweenFrames(60);
		group2.setTimePerScan(0.5);
		group2.setTimePerFrame(50);
		group2.setNumberOfFrames(5);
		group2.setGroupTrig(true);
		group2.setFramesExclFirstTrig(true);

		// create ede scan
		EdeScanParameters scan = new EdeScanParameters();
		scan.addGroup(group1);
		scan.addGroup(group2);
		scan.setNumberOfRepetitions(3);
		scan.setOutputsChoice3(EdeScanParameters.TRIG_FRAME_BEFORE);

		// run calculator
		DoubleDataset[] times = EdeTimingCalculator.calculateTimePoints(scan);

		// test calculator
		assertEquals(4, times.length);

		assertEquals(12048,times[0].getData().length);

		assertEquals(15,times[2].getData().length);

		assertEquals(15,times[3].getData().length);

		assertEquals(times[0].getData().length,times[1].getData().length);

		assertTrue(arrayAlwaysIncreasing(times[0].getData()));
		assertTrue(arrayAlwaysIncreasing(times[2].getData()));
		assertTrue(arrayAlwaysIncreasing(times[3].getData()));
	}

	private boolean arrayAlwaysIncreasing(double[] data) {
		double last = 0;
		for (int i = 0; i < data.length; i++){
			// can be the same, but must not be lower
			if (data[i] < last){
				return false;
			}
			last = data[i];
		}
		return true;
	}
}
