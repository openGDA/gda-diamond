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
import static org.junit.Assert.assertArrayEquals;
import gda.device.DeviceException;
import gda.device.detector.ExperimentLocation;
import gda.device.detector.ExperimentLocationUtils;
import gda.device.scannable.FrameIndexer;
import gda.scan.ede.EdeScanType;
import gda.scan.ede.position.EdePositionType;

import org.junit.Test;

import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

public class FrameIndexerTest {
	@Test
	public void testStaticMethod() {

		Integer[] test1 = FrameIndexer.generateIndex(EdeScanType.LIGHT, EdePositionType.INBEAM, 1, 2, 3);
		assertEquals(Integer.valueOf(0), test1[0]);
		assertEquals(Integer.valueOf(1), test1[1]);
		assertEquals(Integer.valueOf(1), test1[2]);
		assertEquals(Integer.valueOf(2), test1[3]);
		assertEquals(Integer.valueOf(3), test1[4]);

		Integer[] test2 = FrameIndexer.generateIndex(EdeScanType.DARK, EdePositionType.OUTBEAM, 4, 5, 6);
		assertEquals(Integer.valueOf(1), test2[0]);
		assertEquals(Integer.valueOf(0), test2[1]);
		assertEquals(Integer.valueOf(4), test2[2]);
		assertEquals(Integer.valueOf(5), test2[3]);
		assertEquals(Integer.valueOf(6), test2[4]);

	}

	@Test
	public void testExperimentLocationUtils() {
		EdeScanParameters params = new EdeScanParameters();
		for (int i = 1; i <= 10; i++) {
			TimingGroup group1 = new TimingGroup();
			group1.setLabel("group" + i);
			group1.setNumberOfFrames(i);
			group1.setTimePerScan(0.0001);
			group1.setDelayBetweenFrames(0);
			group1.setNumberOfScansPerFrame(1);
			params.addGroup(group1);
		}

		Integer index = 0;
		for (Integer group = 1; group <= 10; group++) {
			for (Integer frame = 1; frame <= group; frame++) {

				// test from absolute number to user meaningful timing group / frame number

				Integer groupOutput = ExperimentLocationUtils.getGroupNum(params, index);
				Integer frameOutput = ExperimentLocationUtils.getFrameNum(params, index);
				System.out.println(index + "\t" + group + "\t" + groupOutput + "\t" + frame + "\t" + frameOutput);
				assertEquals(group, groupOutput);
				assertEquals(frame, frameOutput);

				// test from timing group / frame number to absolute number
				ExperimentLocation loc = new ExperimentLocation(group, frame, 1);
				Integer zerobasedAbsoluteFrame = ExperimentLocationUtils.getAbsoluteFrameNumber(params, loc);
				System.out.println(index + "\t" + zerobasedAbsoluteFrame);
				assertEquals(index, zerobasedAbsoluteFrame);

				index++;
			}
		}
	}

	@Test
	public void testOutputDuringScans() throws DeviceException {

		// a linear scan (so 1 repetition), with 10 timing groups of 1..10 frames in each.
		// So this will be 55 frames

		EdeScanParameters params = new EdeScanParameters();
		for (int i = 1; i <= 10; i++) {
			TimingGroup group1 = new TimingGroup();
			group1.setLabel("group" + i);
			group1.setNumberOfFrames(i);
			group1.setTimePerScan(0.0001);
			group1.setDelayBetweenFrames(0);
			group1.setNumberOfScansPerFrame(1);
			params.addGroup(group1);
		}

		FrameIndexer indexer = new FrameIndexer(EdeScanType.DARK, EdePositionType.OUTBEAM, 1);

		// first frame (frame is zero based but value reported to users will be 1 based)
		Integer group = ExperimentLocationUtils.getGroupNum(params, 0);
		Integer frame = ExperimentLocationUtils.getFrameNum(params, 0);
		indexer.setGroup(group);
		indexer.setFrame(frame);
		assertEquals(Integer.valueOf(1), group);
		assertEquals(Integer.valueOf(1), frame);
		assertArrayEquals(new Integer[] { 1, 0, 1, 1, 1 }, (Integer[]) indexer.getPosition());

		// 20th frame
		group = ExperimentLocationUtils.getGroupNum(params, 20);
		frame = ExperimentLocationUtils.getFrameNum(params, 20);
		indexer.setGroup(group);
		indexer.setFrame(frame);
		assertEquals(Integer.valueOf(6), group);
		assertEquals(Integer.valueOf(6), frame);
		assertArrayEquals(new Integer[] { 1, 0, 1, 6, 6 }, (Integer[]) indexer.getPosition());

		// 27th frame
		group = ExperimentLocationUtils.getGroupNum(params, 27);
		frame = ExperimentLocationUtils.getFrameNum(params, 27);
		indexer.setGroup(group);
		indexer.setFrame(frame);
		assertEquals(Integer.valueOf(7), group);
		assertEquals(Integer.valueOf(7), frame);
		assertArrayEquals(new Integer[] { 1, 0, 1, 7, 7 }, (Integer[]) indexer.getPosition());

		// 51st frame
		group = ExperimentLocationUtils.getGroupNum(params, 51);
		frame = ExperimentLocationUtils.getFrameNum(params, 51);
		indexer.setGroup(group);
		indexer.setFrame(frame);
		assertEquals(Integer.valueOf(10), group);
		assertEquals(Integer.valueOf(7), frame);
		assertArrayEquals(new Integer[] { 1, 0, 1, 10, 7 }, (Integer[]) indexer.getPosition());

	}
}
