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

package gda.device.detector.xstrip;

import gda.data.nexus.tree.NexusTreeProvider;
import gda.device.DeviceException;
import gda.device.detector.DetectorBase;
import gda.device.detector.NexusDetector;

/**
 * Drive an XHDetector object so it can be used in 'regular' step scans. For ad hoc scans during commissioning /
 * beamline alignment.
 */
public class StepScanXHDetector extends DetectorBase implements NexusDetector {

	private XhDetector xh;
	private int numberScansPerFrame = 1;

	@Override
	public void collectData() throws DeviceException {
		//		EdeScanParameters myscan = new EdeScanParameters();
		//		TimingGroup group1 = new TimingGroup();
		//		group1.setLabel("group1");
		//		group1.setNumberOfFrames(1);
		//		// for this class accept time in ms not s, as per the normal Detector interface
		//		group1.setTimePerScan(getCollectionTime() / 1000.0);
		//		group1.setNumberOfScansPerFrame(numberScansPerFrame);
		//		myscan.addGroup(group1);
		//		xh.loadParameters(myscan);
		//		xh.collectData();
	}

	@Override
	public int getStatus() throws DeviceException {
		return xh.getStatus();
	}

	@Override
	public boolean createsOwnFiles() throws DeviceException {
		return false;
	}

	@Override
	public NexusTreeProvider readout() throws DeviceException {
		return xh.readout();
	}

	public XhDetector getXh() {
		return xh;
	}

	public void setXh(XhDetector xh) {
		this.xh = xh;
	}

	@Override
	public String[] getExtraNames() {
		return xh.getExtraNames();
	}

	@Override
	public String[] getInputNames() {
		return xh.getInputNames();
	}

	@Override
	public String[] getOutputFormat() {
		return xh.getOutputFormat();
	}

	public int getNumberScansPerFrame() {
		return numberScansPerFrame;
	}

	public void setNumberScansPerFrame(int numberScansPerFrame) {
		this.numberScansPerFrame = numberScansPerFrame;
	}
}
