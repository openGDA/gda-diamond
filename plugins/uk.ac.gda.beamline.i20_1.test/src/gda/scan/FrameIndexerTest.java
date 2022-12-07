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

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;

import org.dawnsci.ede.EdePositionType;
import org.dawnsci.ede.EdeScanType;
import org.junit.Test;

import gda.device.DeviceException;
import gda.device.detector.DetectorScanInfo;
import gda.device.detector.xstrip.DetectorScanDataUtils;
import gda.device.scannable.FrameIndexer;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

public class FrameIndexerTest {
	@Test
	public void testStaticMethod() {

		// FIXME This is commented out because it is not a proper test!

//		Integer[] test1 = FrameIndexer.generateIndex(EdeScanType.LIGHT, EdePositionType.INBEAM, 1, 2, 3);
//		assertEquals(Integer.valueOf(1), test1[0]);
//		assertEquals(Integer.valueOf(1), test1[1]);
//		assertEquals(Integer.valueOf(1), test1[2]);
//		assertEquals(Integer.valueOf(2), test1[3]);
//		assertEquals(Integer.valueOf(3), test1[4]);
//
//		Integer[] test2 = FrameIndexer.generateIndex(EdeScanType.DARK, EdePositionType.OUTBEAM, 4, 5, 6);
//		assertEquals(Integer.valueOf(0), test2[0]);
//		assertEquals(Integer.valueOf(0), test2[1]);
//		assertEquals(Integer.valueOf(4), test2[2]);
//		assertEquals(Integer.valueOf(5), test2[3]);
//		assertEquals(Integer.valueOf(6), test2[4]);

	}

	@Test
	public void testExperimentLocationUtils() {
		EdeScanParameters params = new EdeScanParameters();
		for (int i = 0; i <= 9; i++) {
			TimingGroup group1 = new TimingGroup();
			group1.setLabel("group" + i);
			group1.setNumberOfFrames(i + 1);
			group1.setTimePerScan(0.0001);
			group1.setDelayBetweenFrames(0);
			group1.setNumberOfScansPerFrame(1);
			params.addGroup(group1);
		}

		Integer index = 0;
		System.out.println("index\tgroup\tgroupOutput\tframe\trameOutput");
		System.out.println("index\tzerobasedAbsoluteFrame");
		for (Integer group = 0; group <= 9; group++) {
			for (Integer frame = 0; frame <= group; frame++) {

				// test from absolute number to user meaningful timing group / frame number

				Integer groupOutput = DetectorScanDataUtils.getGroupNum(params, index);
				Integer frameOutput = DetectorScanDataUtils.getFrameNum(params, index);
				System.out.println(index + "\t" + group + "\t" + groupOutput + "\t" + frame + "\t" + frameOutput);
				assertEquals(group, groupOutput);
				assertEquals(frame, frameOutput);

				// test from timing group / frame number to absolute number
				DetectorScanInfo loc = new DetectorScanInfo(group, frame, 0);
				Integer zerobasedAbsoluteFrame = DetectorScanDataUtils.getAbsoluteFrameNumber(params, loc);
				System.out.println(index + "\t" + zerobasedAbsoluteFrame);
				assertEquals(index, zerobasedAbsoluteFrame);

				index++;
			}
		}
	}

	@Test
	public void testExperimentLocationUtilsReversed() {
		EdeScanParameters params = new EdeScanParameters();
		for (int i = 0; i <= 9; i++) {
			TimingGroup group1 = new TimingGroup();
			group1.setLabel("group" + i);
			group1.setNumberOfFrames(i + 1);
			group1.setTimePerScan(0.0001);
			group1.setDelayBetweenFrames(0);
			group1.setNumberOfScansPerFrame(1);
			params.addGroup(group1);
		}

		System.out.println("absFrameNum\tzerobasedAbsoluteFrame\tgroupOutput\trameOutput");

		for (Integer absFrameNum = 0; absFrameNum <= 54; absFrameNum++) {

			// test from absolute number to user meaningful timing group / frame number
			Integer groupOutput = DetectorScanDataUtils.getGroupNum(params, absFrameNum);
			Integer frameOutput = DetectorScanDataUtils.getFrameNum(params, absFrameNum);

			// test from timing group / frame number to absolute number
			DetectorScanInfo loc = new DetectorScanInfo(groupOutput, frameOutput, 1);
			Integer zerobasedAbsoluteFrame = DetectorScanDataUtils.getAbsoluteFrameNumber(params, loc);
			System.out.println(absFrameNum + "\t" + zerobasedAbsoluteFrame + "\t" + groupOutput + "\t" + frameOutput);

			assertEquals(absFrameNum, zerobasedAbsoluteFrame);
		}
	}

	@Test
	public void testOutputDuringScans() throws DeviceException {

		// a linear scan (so 1 repetition), with 10 timing groups of 1..10 frames in each.
		// So this will be 55 frames

		EdeScanParameters params = new EdeScanParameters();
		for (int i = 0; i <= 9; i++) {
			TimingGroup group1 = new TimingGroup();
			group1.setLabel("group" + i);
			group1.setNumberOfFrames(i + 1);
			group1.setTimePerScan(0.0001);
			group1.setDelayBetweenFrames(0);
			group1.setNumberOfScansPerFrame(1);
			params.addGroup(group1);
		}

//		"Light", "It", "Repetition", "Group", "Frame"
		FrameIndexer indexer = new FrameIndexer(EdeScanType.DARK, EdePositionType.OUTBEAM, 0);

		// first frame (frame is zero based but value reported to users will be 1 based)
		Integer group = DetectorScanDataUtils.getGroupNum(params, 0);
		Integer frame = DetectorScanDataUtils.getFrameNum(params, 0);
		indexer.setGroup(group);
		indexer.setFrame(frame);
		assertEquals(Integer.valueOf(0), group);
		assertEquals(Integer.valueOf(0), frame);
		assertArrayEquals(new Integer[] { 0, 0, 0, 0, 0 }, (Integer[]) indexer.getPosition());

		// 20th frame
		group = DetectorScanDataUtils.getGroupNum(params, 20);
		frame = DetectorScanDataUtils.getFrameNum(params, 20);
		indexer.setGroup(group);
		indexer.setFrame(frame);
		assertEquals(Integer.valueOf(5), group);
		assertEquals(Integer.valueOf(5), frame);
		assertArrayEquals(new Integer[] { 0, 0, 0, 5, 5 }, (Integer[]) indexer.getPosition());

		// 27th frame
		group = DetectorScanDataUtils.getGroupNum(params, 27);
		frame = DetectorScanDataUtils.getFrameNum(params, 27);
		indexer.setGroup(group);
		indexer.setFrame(frame);
		assertEquals(Integer.valueOf(6), group);
		assertEquals(Integer.valueOf(6), frame);
		assertArrayEquals(new Integer[] { 0, 0, 0, 6, 6 }, (Integer[]) indexer.getPosition());

		// 51st frame
		group = DetectorScanDataUtils.getGroupNum(params, 51);
		frame = DetectorScanDataUtils.getFrameNum(params, 51);
		indexer.setGroup(group);
		indexer.setFrame(frame);
		assertEquals(Integer.valueOf(9), group);
		assertEquals(Integer.valueOf(6), frame);
		assertArrayEquals(new Integer[] { 0, 0, 0, 9, 6 }, (Integer[]) indexer.getPosition());

	}
}
