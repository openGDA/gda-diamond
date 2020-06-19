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

import java.util.Arrays;
import java.util.Vector;

import gda.device.Monitor;
import gda.device.Scannable;
import gda.device.detector.xstrip.StripDetector;
import gda.factory.Finder;
import gda.scan.ede.TimeResolvedExperiment;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

public class LinearExperimentDriver extends ScanDriver {

	private final StripDetector detector;
	private final EdeScanParameters iTScanParameters;
	private final Monitor topupMonitor;
	private final Scannable shutter2;
	private double noOfSecPerSpectrumToPublish = TimeResolvedExperiment.DEFALT_NO_OF_SEC_PER_SPECTRUM_TO_PUBLISH;
	@Deprecated
	public LinearExperimentDriver(String detectorName, String topupMonitorName, Vector<TimingGroup> timingGroups, Scannable shutter2) {
		super();
		detector = Finder.find(detectorName);
		topupMonitor = Finder.find(topupMonitorName);
		iTScanParameters = new EdeScanParameters();
		iTScanParameters.setTimingGroups(timingGroups);
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

	public void setNoOfSecPerSpectrumToPublish(int number) {
		noOfSecPerSpectrumToPublish = number;
	}

	@Override
	public String doCollection() throws Exception {
		return null;
	}
}