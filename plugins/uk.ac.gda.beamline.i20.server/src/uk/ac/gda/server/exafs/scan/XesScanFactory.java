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

package uk.ac.gda.server.exafs.scan;

import gda.device.Scannable;

public class XesScanFactory extends XasScanFactory {


	private Scannable analyserAngle;
	private Scannable xes_energy;
	private XesScan xesScan;
	private IXesOffsets xesOffsets;

	public XesScan createXesScan(){

		if (xesScan != null){
			return xesScan;
		}

		checkSharedObjectsNonNull();

		checkDefined(analyserAngle, "analyserAngle");
		checkDefined(xes_energy, "xes_energy");

		xesScan = new XesScan();
		xesScan.setAnalyserAngle(analyserAngle);
		xesScan.setXes_energy(xes_energy);
		xesScan.setMono_energy(energyScannable);
		xesScan.setXas(createEnergyScan());
		xesScan.setBeamlinePreparer(beamlinePreparer);
		xesScan.setDetectorPreparer(detectorPreparer);
		xesScan.setSamplePreparer(samplePreparer);
		xesScan.setOutputPreparer(outputPreparer);
		xesScan.setLoggingScriptController(loggingScriptController);
		xesScan.setDatawriterconfig(datawriterconfig);
		xesScan.setMetashop(metashop);
		xesScan.setIncludeSampleNameInNexusName(true);
		xesScan.setXesOffsets(xesOffsets);

		return xesScan;
	}

	public Scannable getAnalyserAngle() {
		return analyserAngle;
	}

	public void setAnalyserAngle(Scannable analyserAngle) {
		this.analyserAngle = analyserAngle;
	}

	public Scannable getXes_energy() {
		return xes_energy;
	}

	public void setXes_energy(Scannable xes_energy) {
		this.xes_energy = xes_energy;
	}

	public IXesOffsets getXesOffsets() {
		return xesOffsets;
	}

	public void setXesOffsets(IXesOffsets xesOffsets) {
		this.xesOffsets = xesOffsets;
	}


}
