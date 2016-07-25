/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

package gda.scan.ede.datawriters;

import java.util.Arrays;
import java.util.Vector;

import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DoubleDataset;

import gda.data.nexus.extractor.NexusExtractor;
import gda.data.nexus.extractor.NexusGroupData;
import gda.device.detector.NXDetectorData;
import gda.scan.ScanDataPoint;

public class ScanDataHelper {
	public static DoubleDataset extractDetectorDataFromSDP(String detectorName, ScanDataPoint sdp) {
		return extractDetectorDataFromSDP(detectorName, sdp, false);
	}

	public static DoubleDataset extractDetectorEnergyFromSDP(String detectorName, ScanDataPoint sdp) {
		return extractDetectorDataFromSDP(detectorName, sdp, true);
	}

	private static DoubleDataset extractDetectorDataFromSDP(String detectorName, ScanDataPoint sdp, boolean isEnergy) {
		Vector<Object> data = sdp.getDetectorData();
		int detIndex = getIndexOfMyDetector(detectorName, sdp);
		NXDetectorData detData = (NXDetectorData) data.get(detIndex);
		String dataType = isEnergy? EdeDataConstants.ENERGY_COLUMN_NAME : EdeDataConstants.DATA_COLUMN_NAME;
		NexusGroupData groupData = detData.getData(detectorName, dataType, NexusExtractor.SDSClassName);
		double[] originalData = (double[]) groupData.getBuffer();
		return DatasetFactory.createFromObject(DoubleDataset.class, Arrays.copyOf(originalData, originalData.length));
	}

	public static int getIndexOfMyDetector(String detectorName, ScanDataPoint scanDataPoint) {
		Vector<String> names = scanDataPoint.getDetectorNames();
		return names.indexOf(detectorName);
	}
}
