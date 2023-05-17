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

import java.util.List;

import gda.device.Scannable;
import gda.exafs.xes.IXesOffsets;

public class XesScanFactory extends XasScanFactory {


	private Scannable xesBraggGroup;
	private Scannable xesEnergyGroup;
	private Scannable xesEnergyBoth;
	private XesScan xesScan;
	private List<IXesOffsets> xesOffsetsList;

	public XesScan createXesScan(){

		if (xesScan != null){
			return xesScan;
		}

		checkSharedObjectsNonNull();
		// Check all the scannables exist
		checkDefined(xesBraggGroup, "analyserAngleBoth");
		checkDefined(xesEnergyBoth, "xesEnergyBoth");
		checkDefined(xesEnergyGroup, "xesEnergyGroup");
		checkDefined(energyScannable, "energyScannable");

		xesScan = new XesScan();

		// Set the important energy and angle scannables
		xesScan.setXesBraggGroup(xesBraggGroup);
		xesScan.setXesEnergyGroup(xesEnergyGroup);
		xesScan.setXesEnergyBoth(xesEnergyBoth);
		xesScan.setMono_energy(energyScannable);

		xesScan.setXas(createEnergyScan());
		xesScan.setBeamlinePreparer(beamlinePreparer);
		xesScan.setDetectorPreparer(detectorPreparer);
		xesScan.setSamplePreparer(samplePreparer);
		xesScan.setOutputPreparer(outputPreparer);
		xesScan.setLoggingScriptController(loggingScriptController);
		xesScan.setMetashop(metashop);
		xesScan.setIncludeSampleNameInNexusName(includeSampleNameInNexusName);
		xesScan.setXesOffsetsList(xesOffsetsList);

		return xesScan;
	}

	public Scannable getXesBraggGroup() {
		return xesBraggGroup;
	}

	public void setXesBraggGroup(Scannable xesBraggGroup) {
		this.xesBraggGroup = xesBraggGroup;
	}

	public Scannable getXesEnergyBoth() {
		return xesEnergyBoth;
	}

	public void setXesEnergyBoth(Scannable xesEnergyBoth) {
		this.xesEnergyBoth = xesEnergyBoth;
	}

	public Scannable getXesEnergyGroup() {
		return xesEnergyGroup;
	}

	public void setXesEnergyGroup(Scannable xesEnergyGroup) {
		this.xesEnergyGroup = xesEnergyGroup;
	}

	public List<IXesOffsets> getXesOffsetsList() {
		return xesOffsetsList;
	}

	public void setXesOffsetsList(List<IXesOffsets> xesOffsetsList) {
		this.xesOffsetsList = xesOffsetsList;
	}


}
