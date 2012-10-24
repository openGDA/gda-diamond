/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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

package uk.ac.gda.arpes.detector;

import gda.device.DeviceException;
import gda.device.detector.NXDetectorData;

import org.nexusformat.NexusFile;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class VGScientaAnalyser extends gda.device.detector.addetector.ADDetector {
	private static final Logger logger = LoggerFactory.getLogger(VGScientaAnalyser.class);

	private VGScientaController controller;
	private AnalyserCapabilties ac;
	private int[] fixedModeRegion;

	public AnalyserCapabilties getCapabilities() {
		return ac;
	}

	public void setCapabilities(AnalyserCapabilties ac) {
		this.ac = ac;
	}

	public VGScientaController getController() {
		return controller;
	}

	public void setController(VGScientaController controller) {
		this.controller = controller;
	}

	public double[] getEnergyAxis() throws Exception {
		double start, step;
		if (controller.getAcquisitionMode().equalsIgnoreCase("Fixed")) {
			int pass = controller.getPassEnergy().intValue();
			start = controller.getCentreEnergy() - (getCapabilities().getEnergyWidthForPass(pass) / 2);
			step = getCapabilities().getEnergyStepForPass(pass);
		} else {
			start = controller.getStartEnergy();
			step = controller.getEnergyStep();
		}

		int[] dims = determineDataDimensions(getNdArray());

		double[] axis = new double[dims[1]];
		for (int j = 0; j < dims[1]; j++) {
			axis[j] = start + j * step;
		}
		return axis;
	}

	public double[] getAngleAxis() throws Exception {
		return getCapabilities().getAngleAxis(controller.getLensMode(), getAdBase().getMinY_RBV(),
				getAdBase().getArraySizeY_RBV());
	}

	@Override
	protected void appendDataAxes(NXDetectorData data) throws Exception {
		if (firstReadoutInScan) {
			int i = 1;
			String aname = "energies";
			String aunit = "eV";
			double[] axis = getEnergyAxis();

			data.addAxis(getName(), aname, new int[] { axis.length }, NexusFile.NX_FLOAT64, axis, i + 1, 1, aunit,
					false);

			i = 0;
			aname = "angles";
			aunit = "degree";
			axis = getAngleAxis();

			data.addAxis(getName(), aname, new int[] { axis.length }, NexusFile.NX_FLOAT64, axis, i + 1, 1, aunit,
					false);
		}
	}
	
	public void prepareFixedMode() throws Exception {
		controller.setAcquisitionMode("Fixed");
		getAdBase().setMinX(fixedModeRegion[0]);
		getAdBase().setMinY(fixedModeRegion[1]);
		getAdBase().setSizeX(fixedModeRegion[2]);
		getAdBase().setSizeY(fixedModeRegion[3]);
		getAdBase().setImageMode(0);
		getAdBase().setTriggerMode(0);
		controller.setSlice(fixedModeRegion[3]);
	}

	public int[] getFixedModeRegion() {
		return fixedModeRegion;
	}

	public void setFixedModeRegion(int[] fixedModeRegion) {
		this.fixedModeRegion = fixedModeRegion;
	}
	
	@Override
	public double getCollectionTime() throws DeviceException {
		try {
			return getAdBase().getAcquireTime();
		} catch (Exception e) {
			throw new DeviceException("error getting collection time", e);
		}
	}
	
	@Override
	public void setCollectionTime(double collectionTime) throws DeviceException {
	try {
		getAdBase().setAcquireTime(collectionTime);
	} catch (Exception e) {
		throw new DeviceException("error setting collection time", e);
	}
	}
}