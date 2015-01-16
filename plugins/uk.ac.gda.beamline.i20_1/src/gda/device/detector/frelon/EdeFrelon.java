/*-
 * Copyright © 2015 Diamond Light Source Ltd.
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

package gda.device.detector.frelon;

import gda.data.nexus.tree.NexusTreeProvider;
import gda.device.DeviceException;
import gda.device.detector.EdeDetectorBase;
import gda.device.detector.DetectorData;
import gda.device.detector.DetectorStatus;
import gda.device.frelon.Frelon;
import gda.device.lima.LimaCCD;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class EdeFrelon extends EdeDetectorBase {

	private static final Logger logger = LoggerFactory.getLogger(EdeFrelon.class);

	private final LimaCCD limaCcd;
	private final Frelon frelon;

	public EdeFrelon(Frelon frelon, LimaCCD limaCcd) {
		this.frelon = frelon;
		this.limaCcd = limaCcd;
	}

	@Override
	public NexusTreeProvider readout() throws DeviceException {
		// TODO read data from detector
		return null;
	}

	@Override
	public void collectData() throws DeviceException {
		startScan();
	}

	private void startScan() {
		// TODO call prepare and start from Frelon
	}

	@Override
	public int getStatus() throws DeviceException {
		// TODO Check and report detector status
		return 0;
	}

	@Override
	public boolean createsOwnFiles() throws DeviceException {
		return false;
	}

	@Override
	protected DetectorData createData() {
		return new FrelonCcdDetectorData();
	}

	@Override
	public int getMaxPixel() {
		return FrelonCcdDetectorData.MAX_PIXEL;
	}

	@Override
	public int getNumberScansInFrame(double frameTime, double scanTime, int numberOfFrames) throws DeviceException {
		// TODO Query the detector to find out how many scans that can fit
		return 0;
	}

	@Override
	protected void configureDetectorForCollection() throws DeviceException {

		//try {
		FrelonCcdDetectorData frelonCcdDetectorData = (FrelonCcdDetectorData) getDetectorData();
		limaCcd.setImageBin(1, frelonCcdDetectorData.getBinValue());
		// frelon.setROIMode(frelonCcdDetectorData.getRoiMode());
		//logger.error("Unable to configure the detector for collection", e);
		//}
	}

	@Override
	public NexusTreeProvider[] readFrames(int startFrame, int finalFrame) throws DeviceException {
		// TODO Need to read this 1D array from detector and create nexus tree provider
		return null;
	}

	@Override
	public DetectorStatus fetchStatus() throws DeviceException {
		// TODO Check and report detector status
		return null;
	}
}
