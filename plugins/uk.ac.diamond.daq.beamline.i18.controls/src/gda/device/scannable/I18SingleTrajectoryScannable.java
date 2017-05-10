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

package gda.device.scannable;

import gda.device.DeviceException;
import gda.scan.EpicsTrajectoryScanController;

/**
 * I18 specific EpicsSingleTrajectoryScannable which checks the beam after moving to the start of a line, but before starting the acquisition.
 */
public class I18SingleTrajectoryScannable extends EpicsSingleTrajectoryScannable {

	private BeamMonitor beamMonitor;
	private TopupChecker topupMonitor;
	private boolean isBidirectional;

	public I18SingleTrajectoryScannable() {
		super();
		this.isBidirectional = false;
	}

	@Override
	public void prepareForContinuousMove() throws DeviceException {

		// force rebuild of trajectory for bi-di maps only otherwise this adds extra time in Continuous scan
		// only added in GDA 8.44 but not present in GDA 8.50
		if (isBidirectional == true)
			trajectoryBuildDone = false;
		super.prepareForContinuousMove();

		EpicsTrajectoryScanController.setMAXIMUM_ELEMENT_NUMBER(100000);

		// just before the data collection begins, test the beam and topup.
		if (beamMonitor != null){
			beamMonitor.setPauseBeforePoint(true);
			beamMonitor.atPointStart();
		}

		if (topupMonitor != null){
			topupMonitor.setPauseBeforePoint(true);
			topupMonitor.atPointStart();
		}
	}

	@Override
	public void continuousMoveComplete() throws DeviceException {
//		rawAsynchronousMoveTo(continuousParameters.getStartPosition());
		super.continuousMoveComplete();
	}

	public BeamMonitor getBeamMonitor() {
		return beamMonitor;
	}

	/**
	 * Set to null to turn off this check
	 *
	 * @param beamMonitor
	 */
	public void setBeamMonitor(BeamMonitor beamMonitor) {
		this.beamMonitor = beamMonitor;
	}

	public TopupChecker getTopupMonitor() {
		return topupMonitor;
	}

	/**
	 * Set to null to turn off this check
	 *
	 * @param topupMonitor
	 */
	public void setTopupMonitor(TopupChecker topupMonitor) {
		this.topupMonitor = topupMonitor;
	}

	public boolean isBidirectional() {
		return isBidirectional;
	}

	public void setBidirectional(boolean isBidirectional) {
		this.isBidirectional = isBidirectional;
	}
}
