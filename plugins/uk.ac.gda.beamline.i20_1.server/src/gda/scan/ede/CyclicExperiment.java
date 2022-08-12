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

package gda.scan.ede;

import java.util.List;
import java.util.Map;

import gda.device.DeviceException;
import uk.ac.gda.exafs.ui.data.TimingGroup;

/**
 *  An EDE Linear scan where the repetition number is not 1.
 */
public class CyclicExperiment extends TimeResolvedExperiment {

	@Override
	protected String getHeaderText() {
		StringBuilder metadataText = new StringBuilder();
		metadataText.append(super.getHeaderText());
		metadataText.append(String.format("\nCycles: %d\n", numberOfRepetitions));
		return metadataText.toString();
	}

	public CyclicExperiment(double i0accumulationTime, List<TimingGroup> itTimingGroups,
			Map<String, Double> i0ScanableMotorPositions, Map<String, Double> iTScanableMotorPositions,
			String detectorName, String topupMonitorName, String beamShutterScannableName)
					throws DeviceException {
		super(i0accumulationTime, itTimingGroups, i0ScanableMotorPositions, iTScanableMotorPositions, detectorName,
				topupMonitorName, beamShutterScannableName);
		this.numberOfRepetitions = 1;
	}
}
