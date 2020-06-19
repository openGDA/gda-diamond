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
import gda.device.detector.xstrip.StripDetector;
import gda.factory.Finder;

/**
 * Convenience class which takes a series of parameters, runs the scan and then returns the name of the ascii file
 * created.
 */
@Deprecated
public class SingleSpectrumDriver extends ScanDriver{

	private final StripDetector detector;

	private final Double i0_scantime;
	private final Integer i0_numberscans;
	private final Monitor topupMonitor;
	private Double it_scantime;
	private Integer it_numberscans;
	private final Scannable shutter2;

	public SingleSpectrumDriver(String detectorName, String topupMonitorName, Double i0_scantime, Integer i0_numberscans, Double it_scantime,
			Integer it_numberscans, Scannable shutter2) {
		super();

		this.i0_scantime = i0_scantime;
		this.i0_numberscans = i0_numberscans;
		this.it_scantime = it_scantime;
		this.it_numberscans = it_numberscans;

		this.shutter2 = shutter2;

		detector = Finder.find(detectorName);
		topupMonitor = Finder.find(topupMonitorName);

		if (this.it_scantime == null) {
			this.it_scantime = i0_scantime;
		}
		if (this.it_numberscans == null) {
			this.it_numberscans = i0_numberscans;
		}

	}

	public SingleSpectrumDriver(String detectorName, String topupMonitorName, Double i0_scantime, Integer i0_numberscans, Double it_scantime,
			Integer it_numberscans, String fileTemplate, Scannable shutter2) {
		this(detectorName, topupMonitorName, i0_scantime, i0_numberscans, it_scantime, it_numberscans, shutter2);
		this.fileTemplate = fileTemplate;
	}

	@Override
	public String doCollection() throws Exception {
		//		validate();
		//
		//		EdeScanParameters i0scanparams = EdeScanParameters.createSingleFrameScan(i0_scantime, i0_numberscans);
		//		EdeScanParameters itscanparams = EdeScanParameters.createSingleFrameScan(it_scantime, it_numberscans);
		//
		//		EdeSingleExperiment theExperiment = new EdeSingleExperiment(i0scanparams, itscanparams, outbeamPosition,
		//				inbeamPosition, detector, topupMonitor, shutter2);
		//		if (fileTemplate != null) {
		//			theExperiment.setFilenameTemplate(fileTemplate);
		//		}
		//		return theExperiment.runExperiment();
		return null;
	}

}
