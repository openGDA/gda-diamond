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

import gda.device.detector.StripDetector;
import gda.factory.Finder;
import gda.scan.ede.EdeLinearExperiment;

import java.util.Vector;

import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

public class LinearExperimentDriver extends ScanDriver {

	private final StripDetector detector;
	private final EdeScanParameters params;

	public LinearExperimentDriver(String detectorName, Vector<TimingGroup> timingGroups) {
		super();
		detector = Finder.getInstance().find(detectorName);
		params = new EdeScanParameters();
		params.setGroups(timingGroups);
	}

	public LinearExperimentDriver(String detectorName, Vector<TimingGroup> timingGroups, String filenameTemplate) {
		this(detectorName, timingGroups);
		fileTemplate = filenameTemplate;
	}


	@Override
	public String doCollection() throws Exception {
		EdeLinearExperiment theExperiment = new EdeLinearExperiment(params, outbeamPosition, inbeamPosition, detector);
		if (fileTemplate != null) {
			theExperiment.setFilenameTemplate(fileTemplate);
		}
		return theExperiment.runExperiment();

	}
}