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
import java.util.List;

import org.dawnsci.ede.EdeDataConstants;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DoubleDataset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.nexus.extractor.NexusExtractor;
import gda.data.nexus.extractor.NexusGroupData;
import gda.device.detector.NXDetectorData;
import gda.scan.ScanDataPoint;

public class ScanDataHelper {
	private static final Logger logger = LoggerFactory.getLogger(ScanDataHelper.class);

	public static DoubleDataset extractDetectorDataFromSDP(String detectorName, ScanDataPoint sdp) {
		return extractDetectorDataFromSDP(detectorName, sdp, false);
	}

	public static DoubleDataset extractDetectorEnergyFromSDP(String detectorName, ScanDataPoint sdp) {
		return extractDetectorDataFromSDP(detectorName, sdp, true);
	}

	private static DoubleDataset extractDetectorDataFromSDP(String detectorName, ScanDataPoint sdp, boolean isEnergy) {
		List<Object> data = sdp.getDetectorData();
		int detIndex = getIndexOfMyDetector(detectorName, sdp);
		NXDetectorData detData = (NXDetectorData) data.get(detIndex);
		String dataType = isEnergy? EdeDataConstants.ENERGY_COLUMN_NAME : EdeDataConstants.DATA_COLUMN_NAME;
		NexusGroupData groupData = detData.getData(detectorName, dataType, NexusExtractor.SDSClassName);
		return extractDataFromNexusGroup(groupData);
	}

	public static DoubleDataset extractDataFromNexusGroup(NexusGroupData groupData) {
		Dataset dataset = DatasetFactory.createFromObject(groupData.getBuffer());
		// Generate a warning if there's a problem creating the Dataset or the shape does not match original data
		if (dataset==null) {
			logger.warn("Nexus data to could not be converted to Dataset");
		} else {
			boolean shapeOk = Arrays.equals(groupData.getDimensions(), dataset.getShape());
			if (!shapeOk) {
				logger.warn("Problem converting from Nexus data to Dataset : shape does not match original Nexus data.");
			}
		}
		// Return clone of dataset, so original NexusGroupData object is not affected if we manipulate the returned dataset...
		return dataset.copy(DoubleDataset.class);
	}

	public static int getIndexOfMyDetector(String detectorName, ScanDataPoint scanDataPoint) {
		return scanDataPoint.getDetectorNames().indexOf(detectorName);
	}
}
