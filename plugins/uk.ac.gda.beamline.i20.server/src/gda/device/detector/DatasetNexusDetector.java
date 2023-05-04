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

import org.eclipse.january.dataset.IDataset;

import gda.data.nexus.extractor.NexusGroupData;
import gda.data.nexus.tree.INexusTree;
import gda.data.nexus.tree.NexusTreeProvider;
import gda.device.DeviceException;

/**
 * NexusDetector implementation that returns a Nexus tree containing a Dataset.
 * The {@link #readout()} method returns a NexusTreeProvider object containing the dataset
 * produced by {@link #getDataset()} method.
 */
public abstract class DatasetNexusDetector extends DetectorBase implements NexusDetector {

	private String dataGroupName = "imagedata";

	@Override
	public void collectData() throws DeviceException {
	}

	/**
	 * The {@link #readout()} function calls this method
	 * @return A dataset object. .
	 * @throws DeviceException
	 */
	public abstract IDataset getDataset() throws DeviceException;

	@Override
	public int getStatus() throws DeviceException {
		return 0;
	}

	@Override
	public boolean createsOwnFiles() throws DeviceException {
		return false;
	}

	/**
	 * Produce the detector data, by putting the dataset returned by {@#link #getDataset()} into a NexusTreeProvider object.
	 */
	@Override
	public NexusTreeProvider readout() throws DeviceException {
		return createNexusData(getDataset());
	}

	@Override
	public Object getPosition() throws DeviceException {
		return 1.0;
	}

	/**
	 * Create a Nexus tree containing a dataset
	 *
	 * @param dataset
	 * @return NexusTreeProvider object
	 */
	protected NXDetectorData createNexusData(IDataset dataset) {
		NXDetectorData frame = new NXDetectorData(getExtraNames(), getOutputFormat(), getName());
		INexusTree detTree = frame.getDetTree(getName());
		// Add the image data
		NXDetectorData.addData(detTree, dataGroupName, new NexusGroupData(dataset), "", 1);

		// Value displayed during scans
		frame.setPlottableValue(getName(), 1.0);
		return frame;
	}

	public String getDataGroupName() {
		return dataGroupName;
	}

	public void setDataGroupName(String dataGroupName) {
		this.dataGroupName = dataGroupName;
	}
}
