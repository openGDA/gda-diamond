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

package gda.scan.ede.drivers;

import gda.device.Monitor;
import gda.device.Scannable;
import gda.device.detector.StripDetector;
import gda.factory.Finder;
import gda.scan.ede.EdeLinearExperiment;

import java.util.Arrays;
import java.util.Vector;

import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

public class LinearExperimentDriver extends ScanDriver {

	private final StripDetector detector;
	private final EdeScanParameters params;
	private final Monitor topupMonitor;
	private final Scannable shutter2;

	public LinearExperimentDriver(String detectorName, String topupMonitorName, Vector<TimingGroup> timingGroups, Scannable shutter2) {
		super();
		detector = Finder.getInstance().find(detectorName);
		topupMonitor = Finder.getInstance().find(topupMonitorName);
		params = new EdeScanParameters();
		params.setGroups(timingGroups);
		this.shutter2 = shutter2;
	}

	public LinearExperimentDriver(String detectorName, String topupMonitorName, Vector<TimingGroup> timingGroups, String filenameTemplate, Scannable shutter2) {
		this(detectorName, topupMonitorName, timingGroups, shutter2);
		fileTemplate = filenameTemplate;
	}

	public LinearExperimentDriver(String detectorName, String topupMonitorName, TimingGroup[] timingGroups, Scannable shutter2) {
		this(detectorName, topupMonitorName, new Vector<TimingGroup>(Arrays.asList(timingGroups)), shutter2);
	}

	public LinearExperimentDriver(String detectorName, String topupMonitorName, TimingGroup[] timingGroups, String filenameTemplate, Scannable shutter2) {
		this(detectorName, topupMonitorName, new Vector<TimingGroup>(Arrays.asList(timingGroups)), shutter2);
		fileTemplate = filenameTemplate;
	}

	@Override
	public String doCollection() throws Exception {
		EdeLinearExperiment theExperiment = new EdeLinearExperiment(params, outbeamPosition, inbeamPosition,
				referencePosition, detector,topupMonitor, shutter2);
		if (fileTemplate != null) {
			theExperiment.setFilenameTemplate(fileTemplate);
		}
		return theExperiment.runExperiment();
	}
}