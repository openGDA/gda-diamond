/*-
 * Copyright © 2023 Diamond Light Source Ltd.
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

package gda.device.detector;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.IDataset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.nexus.extractor.NexusGroupData;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.motor.EpicsMotor;
import gda.device.scannable.ScannableMotor;
import gda.device.scannable.ScannableUtils;
import gda.device.scannable.scannablegroup.ScannableGroup;

/**
 * NexusDetector that records the demand, readback and demand-readback values for a
 * single scannable/group of scannables. This works for ScannableMotor objects that use EpicsMotor
 * as the underlying motor object. All other scannables will record only current readback position
 * (using {@link Scannable#getPosition()}).
 */
public class ReadbackDemandDifference extends DatasetNexusDetector {
	private static final Logger logger = LoggerFactory.getLogger(ReadbackDemandDifference.class);

	private Scannable scannable;

	private List<Double> demand;
	private List<Double> readback;
	private List<Double> difference;

	public ReadbackDemandDifference() {
		setDataGroupName("readback");
	}
	public Scannable getScannable() {
		return scannable;
	}

	public void setScannable(Scannable scannable) {
		this.scannable = scannable;
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return scannable.isBusy();
	}

	private void updateValues() throws DeviceException {
		demand = new ArrayList<>();
		readback = new ArrayList<>();
		difference = new ArrayList<>();

		for(var scn : getScannableList()) {
			if (scn instanceof ScannableMotor scnMot && scnMot.getMotor() instanceof EpicsMotor mot) {
				demand.add(mot.getTargetPosition());
				readback.add(mot.getPosition());
				difference.add(mot.getTargetPosition() - mot.getPosition());
			} else {
				readback.add( ScannableUtils.objectToArray(scn.getPosition())[0]);
			}
		}
	}

	private List<Scannable> getScannableList() {
		List<Scannable> scnList = new ArrayList<>();
		if (scannable instanceof ScannableGroup scnGroup) {
			scnList.addAll(scnGroup.getGroupMembers());
		} else {
			scnList.add(scannable);
		}
		return scnList;
	}

	@Override
	public IDataset getDataset() throws DeviceException {
		updateValues();
		return DatasetFactory.createFromList(readback);
	}

	private <T> NexusGroupData makeNexusGroupData(List<T> dat) {
		IDataset dataset = DatasetFactory.createFromList(dat);
		return new NexusGroupData(dataset);
	}

	@Override
	protected NXDetectorData createNexusData(IDataset dataset) {
		// Add the readback values (the dataset passed in is from 'getDataset')
		NXDetectorData frame = super.createNexusData(dataset);

		//try to add demand and readback positions
		if (!demand.isEmpty()) {
			frame.addData(getName(), "demand", makeNexusGroupData(demand));
		}
		if (!difference.isEmpty()) {
			frame.addData(getName(), "difference", makeNexusGroupData(difference));
		}

		// Add the names of the scannables as an axis
		List<String> nameList = getScannableList().stream().map(Scannable::getName).toList();
		frame.addAxis(getName(), "scannable names", makeNexusGroupData(nameList), 1, 1, "", false);


		return frame;
	}
}